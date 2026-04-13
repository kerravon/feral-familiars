from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from bot.models.encounter import Encounter, EncounterParticipant
from bot.models.familiar import Familiar
from bot.models.base import User
from bot.services.inventory_service import InventoryService
from bot.utils.constants import GameConstants
from bot.utils.config import Config
from datetime import datetime, timedelta
import random

class EncounterService:
    @staticmethod
    async def spawn_encounter(
        session: AsyncSession, 
        channel_id: int, 
        guild_id: int,
        type: str, # essence or spirit
        override_subtype: str = None,
        override_rarity: str = None,
        blacklisted_user_id: int = None
    ):
        # 1. Check if active encounter exists
        stmt = select(Encounter).where(
            Encounter.channel_id == channel_id, 
            Encounter.is_active == True
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Still an active record in DB, wait for cleanup_loop to fade it
            return None
        
        # 2. Determine Rarity and Duration
        duration_seconds = Config.CAPTURE_WINDOW_SECONDS
        
        # --- Temporal Anchor (Arcane Passive) ---
        # Check if anyone has an IGNITED Arcane familiar
        stmt_arcane = select(Familiar).where(
            Familiar.active_until > datetime.now(), 
            Familiar.essence_type == GameConstants.ARCANE
        ).limit(1)
        arcane_res = await session.execute(stmt_arcane)
        has_arcane_anchor = arcane_res.scalar_one_or_none() is not None

        if type == "essence":
            subtype = override_subtype or random.choices(GameConstants.ESSENCES, weights=GameConstants.ESSENCE_WEIGHTS, k=1)[0]
            rarity = None
            # Essence duration is standard
            duration_seconds = Config.CAPTURE_WINDOW_SECONDS + random.randint(0, 5)
        else:
            # 10% chance for Restless spirit, others balanced (22.5% each)
            weights = [22.5, 22.5, 22.5, 22.5, 10]
            subtype = override_subtype or random.choices(GameConstants.SPIRITS, weights=weights, k=1)[0]
            # Rarity distribution affects duration slightly
            if override_rarity:
                rarity = override_rarity
                duration_seconds = Config.CAPTURE_WINDOW_SECONDS
            else:
                rand = random.random()
                if rand < 0.6: 
                    rarity = GameConstants.COMMON
                    duration_seconds = Config.CAPTURE_WINDOW_SECONDS
                elif rand < 0.85: 
                    rarity = GameConstants.UNCOMMON
                    duration_seconds = Config.CAPTURE_WINDOW_SECONDS - 2
                elif rand < 0.97: 
                    rarity = GameConstants.RARE
                    duration_seconds = Config.CAPTURE_WINDOW_SECONDS - 5
                else: 
                    rarity = GameConstants.LEGENDARY
                    duration_seconds = Config.CAPTURE_WINDOW_SECONDS - 8

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
        # Store if anchor was active for UI feedback
        # (We can use a temporary attribute or just return it)
        encounter._temp_anchor_active = has_arcane_anchor
        
        session.add(encounter)
        await session.commit()
        await session.refresh(encounter)
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
        """Checks for Restless Soul Anchor and extends encounter if triggered. Returns True if anchored."""
        if encounter.type != "spirit":
            return False
            
        from bot.models.familiar import Familiar
        now = datetime.now()
        
        stmt = select(Familiar).where(
            Familiar.active_until > now, 
            Familiar.spirit_type == GameConstants.RESTLESS
        ).limit(1)
        res = await session.execute(stmt)
        anchor_fam = res.scalar_one_or_none()
        
        if anchor_fam:
            chances = {"common": 0.2, "uncommon": 0.3, "rare": 0.4, "legendary": 0.5}
            if random.random() < chances.get(anchor_fam.rarity, 0.2):
                encounter.expires_at = now + timedelta(seconds=30)
                await session.commit()
                return anchor_fam
        return None

    @staticmethod
    async def process_capture_attempt(
        session: AsyncSession,
        channel_id: int,
        user_id: int,
        keyword: str
    ):
        # 1. Fetch active encounter
        stmt = select(Encounter).where(
            Encounter.channel_id == channel_id,
            Encounter.is_active == True
        )
        result = await session.execute(stmt)
        encounter = result.scalar_one_or_none()
        
        if not encounter:
            return None, "No active encounter in this channel."
        
        # Check blacklist (for released surges)
        if encounter.blacklisted_user_id and user_id == encounter.blacklisted_user_id:
            return None, "This energy is unstable for you. Let others bind it!"
        
        # 2. Validate keyword
        expected = "bind" if encounter.type == "essence" else "bind spirit"
        if keyword.lower().strip() != expected:
            return None, None # Ignore invalid keywords silently or with feedback
        
        # 3. Check anti-macro delay
        now = datetime.now()
        if now - encounter.spawned_at < timedelta(seconds=Config.ANTI_MACRO_DELAY_SECONDS):
            return None, "Too fast! Wait a moment before binding."
        
        # 4. Check capture window
        if now > encounter.expires_at:
            encounter.is_active = False
            await session.commit()
            return None, "The essence has faded..."

        # 5. Check if player already attempted
        stmt = select(EncounterParticipant).where(
            EncounterParticipant.encounter_id == encounter.id,
            EncounterParticipant.user_id == user_id
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            return None, "You already tried to bind this!"

        # 6. Capture! (First one wins)
        encounter.is_active = False
        encounter.captured_by = user_id
        
        # Add to inventory
        if encounter.type == "essence":
            await InventoryService.add_essence(session, user_id, encounter.subtype, 1)
            msg = f"Successfully bound the {encounter.subtype} essence!"
        else:
            success, result = await InventoryService.add_spirit(session, user_id, encounter.subtype, encounter.rarity)
            if not success:
                return None, result
            
            # Spirit success: tell them the cost
            cost = GameConstants.COST_MAP[encounter.rarity]
            msg = (
                f"Successfully bound the {encounter.rarity} {encounter.subtype} spirit! "
                f"You will need **{cost} matching essences** to create a familiar with this spirit."
            )

        participant = EncounterParticipant(encounter_id=encounter.id, user_id=user_id)
        session.add(participant)
        await session.commit()
        
        return encounter, msg
