from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from bot.models.encounter import Encounter, EncounterParticipant
from bot.models.familiar import Familiar
from bot.models.base import User
from bot.services.inventory_service import InventoryService
from bot.utils.constants import GameConstants
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
            # If the existing encounter is past its expires_at, mark it as inactive
            if datetime.now() > existing.expires_at:
                existing.is_active = False
                await session.commit()
            else:
                # Still active and fresh, don't spawn another one
                return None
        
        # 2. Determine Rarity and Duration
        duration_seconds = 45 # Default
        
        # --- Temporal Anchor (Arcane Passive) ---
        # Check if anyone in this guild has an active Arcane familiar
        arcane_stmt = select(Familiar).where(
            Familiar.user_id.in_(
                select(User.id).where(User.id == Familiar.user_id) # Implicit join/check
            ),
            Familiar.is_active == True,
            Familiar.essence_type == GameConstants.ARCANE
        )
        # Simpler: Just check if any active Arcane familiar exists for any user. 
        # To be guild-specific, we'd need a join with a member table, but since we don't 
        # track 'User-in-Guild' explicitly in a join table yet, let's look for ANY 
        # active Arcane familiar globally for now as a "World Blessing", 
        # or I can add a quick check for players who have interacted in this guild.
        
        # Let's do a more performant check: Is there ANY active Arcane familiar?
        # (We can refine this to Guild-only later if we add a GuildMember model)
        stmt_arcane = select(Familiar).where(Familiar.is_active == True, Familiar.essence_type == GameConstants.ARCANE).limit(1)
        arcane_res = await session.execute(stmt_arcane)
        has_arcane_anchor = arcane_res.scalar_one_or_none() is not None

        if type == "essence":
            subtype = override_subtype or random.choices(GameConstants.ESSENCES, weights=GameConstants.ESSENCE_WEIGHTS, k=1)[0]
            rarity = None
            duration_seconds = random.randint(42, 50)
        else:
            # 10% chance for Restless spirit, others balanced (22.5% each)
            weights = [22.5, 22.5, 22.5, 22.5, 10]
            subtype = override_subtype or random.choices(GameConstants.SPIRITS, weights=weights, k=1)[0]
            # Rarity distribution
            if override_rarity:
                rarity = override_rarity
                duration_seconds = 45
            else:
                rand = random.random()
                if rand < 0.6: 
                    rarity = GameConstants.COMMON
                    duration_seconds = random.randint(40, 45)
                elif rand < 0.85: 
                    rarity = GameConstants.UNCOMMON
                    duration_seconds = random.randint(38, 42)
                elif rand < 0.97: 
                    rarity = GameConstants.RARE
                    duration_seconds = random.randint(36, 40)
                else: 
                    rarity = GameConstants.LEGENDARY
                    duration_seconds = random.randint(34, 37)

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
        expired = result.scalars().all()
        
        for e in expired:
            e.is_active = False
        
        await session.commit()
        return expired

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
        
        # 3. Check anti-macro delay (1s)
        now = datetime.now()
        if now - encounter.spawned_at < timedelta(seconds=1):
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
