import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from bot.models.encounter import Encounter, EncounterParticipant
from bot.models.familiar import Familiar
from bot.models.base import User
from bot.services.inventory_service import InventoryService
from bot.domain.enums import EncounterType, EssenceType, SpiritType, Rarity
from bot.domain.constants import GameRules, AssetUrls
from bot.utils.config import Config

class EncounterService:
    @staticmethod
    async def spawn_encounter(
        session: AsyncSession, 
        channel_id: int, 
        guild_id: int,
        type: EncounterType,
        override_subtype: str = None,
        override_rarity: Rarity = None,
        blacklisted_user_id: int = None
    ):
        """Spawns an encounter. Does NOT commit."""
        # 1. Check if active encounter exists
        stmt = select(Encounter).where(
            Encounter.channel_id == channel_id, 
            Encounter.is_active == True
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return None
        
        # 2. Determine Rarity and Duration
        duration_seconds = Config.CAPTURE_WINDOW_SECONDS
        
        # --- Temporal Anchor (Arcane Passive) ---
        stmt_arcane = select(Familiar).where(
            Familiar.active_until > datetime.now(), 
            Familiar.essence_type == EssenceType.ARCANE
        ).limit(1)
        arcane_res = await session.execute(stmt_arcane)
        has_arcane_anchor = arcane_res.scalar_one_or_none() is not None

        subtype = override_subtype
        rarity = override_rarity

        if type == EncounterType.ESSENCE:
            if not subtype:
                choices = list(GameRules.ESSENCE_WEIGHTS.keys())
                weights = list(GameRules.ESSENCE_WEIGHTS.values())
                subtype = random.choices(choices, weights=weights, k=1)[0].value
            rarity = None
            duration_seconds = Config.CAPTURE_WINDOW_SECONDS + random.randint(0, 5)
        else: # Spirit
            if not subtype:
                choices = list(GameRules.SPIRIT_WEIGHTS.keys())
                weights = list(GameRules.SPIRIT_WEIGHTS.values())
                subtype = random.choices(choices, weights=weights, k=1)[0].value
            
            if not rarity:
                choices = list(GameRules.RARITY_WEIGHTS.keys())
                weights = list(GameRules.RARITY_WEIGHTS.values())
                rarity = random.choices(choices, weights=weights, k=1)[0]
            
            # Duration based on rarity
            rarity_penalties = {
                Rarity.COMMON: 0,
                Rarity.UNCOMMON: 2,
                Rarity.RARE: 5,
                Rarity.LEGENDARY: 8
            }
            duration_seconds = Config.CAPTURE_WINDOW_SECONDS - rarity_penalties.get(rarity, 0)

        if has_arcane_anchor:
            duration_seconds += 15

        spawn_time = datetime.now()
        encounter = Encounter(
            channel_id=channel_id,
            guild_id=guild_id,
            type=type,
            subtype=subtype,
            rarity=rarity,
            message_id=0,
            is_active=True,
            spawned_at=spawn_time,
            expires_at=spawn_time + timedelta(seconds=duration_seconds),
            blacklisted_user_id=blacklisted_user_id
        )
        encounter._temp_anchor_active = has_arcane_anchor
        
        session.add(encounter)
        return encounter

    @staticmethod
    async def get_expired_encounters(session: AsyncSession):
        """Finds active encounters past their expiration time."""
        stmt = select(Encounter).where(
            Encounter.is_active == True,
            Encounter.expires_at < datetime.now()
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def handle_soul_anchor(session: AsyncSession, encounter: Encounter):
        """Checks for Restless Soul Anchor and extends encounter if triggered. Does NOT commit."""
        if encounter.type != EncounterType.SPIRIT:
            return None
            
        now = datetime.now()
        stmt = select(Familiar).where(
            Familiar.active_until > now, 
            Familiar.spirit_type == SpiritType.RESTLESS
        ).limit(1)
        res = await session.execute(stmt)
        anchor_fam = res.scalar_one_or_none()
        
        if anchor_fam:
            chances = {Rarity.COMMON: 0.2, Rarity.UNCOMMON: 0.3, Rarity.RARE: 0.4, Rarity.LEGENDARY: 0.5}
            if random.random() < chances.get(anchor_fam.rarity, 0.2):
                encounter.expires_at = now + timedelta(seconds=30)
                return anchor_fam
        return None

    @staticmethod
    async def process_capture_attempt(
        session: AsyncSession,
        channel_id: int,
        user_id: int,
        keyword: str
    ):
        """Processes capture attempt. Does NOT commit."""
        # 1. Fetch active encounter
        stmt = select(Encounter).where(
            Encounter.channel_id == channel_id,
            Encounter.is_active == True
        )
        result = await session.execute(stmt)
        encounter = result.scalar_one_or_none()
        
        if not encounter:
            return None, "No active encounter in this channel."
        
        if encounter.blacklisted_user_id and user_id == encounter.blacklisted_user_id:
            return None, "This energy is unstable for you. Let others bind it!"
        
        # 2. Validate keyword
        expected = "bind" if encounter.type == EncounterType.ESSENCE else "bind spirit"
        if keyword.lower().strip() != expected:
            return None, None
        
        # 3. Check anti-macro delay
        now = datetime.now()
        if now - encounter.spawned_at < timedelta(seconds=Config.ANTI_MACRO_DELAY_SECONDS):
            return None, "Too fast! Wait a moment before binding."
        
        # 4. Check capture window
        if now > encounter.expires_at:
            encounter.is_active = False
            return None, "The essence has faded..."

        # 5. Check if player already attempted
        stmt = select(EncounterParticipant).where(
            EncounterParticipant.encounter_id == encounter.id,
            EncounterParticipant.user_id == user_id
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            return None, "You already tried to bind this!"

        # 6. Capture!
        encounter.is_active = False
        encounter.captured_by = user_id
        
        # Add to inventory
        if encounter.type == EncounterType.ESSENCE:
            e_enum = EssenceType(encounter.subtype)
            await InventoryService.add_essence(session, user_id, e_enum, 1)
            msg = f"Successfully bound the {encounter.subtype} essence!"
        else:
            s_enum = SpiritType(encounter.subtype)
            success, result = await InventoryService.add_spirit(session, user_id, s_enum, encounter.rarity)
            if not success:
                return None, result
            
            cost = GameRules.RITUAL_COSTS[encounter.rarity]
            msg = (
                f"Successfully bound the {encounter.rarity.value} {encounter.subtype} spirit! "
                f"You will need **{cost} matching essences** to create a familiar with this spirit."
            )

        participant = EncounterParticipant(encounter_id=encounter.id, user_id=user_id)
        session.add(participant)
        
        return encounter, msg
