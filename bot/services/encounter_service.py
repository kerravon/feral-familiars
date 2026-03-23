from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from bot.models.encounter import Encounter, EncounterParticipant
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
        override_rarity: str = None
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
        if type == "essence":
            subtype = override_subtype or random.choice(GameConstants.ESSENCES)
            rarity = None
            duration_seconds = random.randint(42, 50)
        else:
            subtype = override_subtype or random.choice(GameConstants.SPIRITS)
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
            expires_at=spawn_time + timedelta(seconds=duration_seconds)
        )
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
