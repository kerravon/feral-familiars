import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from bot.models.familiar import Spirit, Familiar
from bot.models.essence import Essence
from bot.models.base import User
from bot.domain.enums import EssenceType, SpiritType, Rarity
from bot.domain.constants import GameRules
from bot.domain.naming import NamingRules

logger = logging.getLogger("FeralFamiliars")

class RitualService:
    @staticmethod
    async def create_familiar(
        session: AsyncSession, 
        user_id: int, 
        spirit_id: int, 
        essence_type: EssenceType
    ):
        """Creates a familiar. Does NOT commit."""
        try:
            # 1. Fetch Spirit
            stmt = select(Spirit).where(Spirit.id == spirit_id, Spirit.user_id == user_id)
            result = await session.execute(stmt)
            spirit = result.scalar_one_or_none()
            
            if not spirit:
                return False, "Spirit not found in your inventory."
            
            # 2. Check Cost
            actual_cost = GameRules.RITUAL_COSTS[spirit.rarity]
            
            stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == essence_type)
            result = await session.execute(stmt)
            essence = result.scalar_one_or_none()
            
            if not essence or essence.count < actual_cost:
                return False, f"Insufficient {essence_type.value} essences. Need {actual_cost}, you have {essence.count if essence else 0}."
            
            # --- Restless Spirit Extra Cost (Arcane) ---
            arcane_cost = 0
            arcane_essence = None
            if spirit.type == SpiritType.RESTLESS and essence_type != EssenceType.ARCANE:
                arcane_cost = GameRules.RESTLESS_ARCANE_COSTS[spirit.rarity]
                stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == EssenceType.ARCANE)
                res = await session.execute(stmt)
                arcane_essence = res.scalar_one_or_none()
                if not arcane_essence or arcane_essence.count < arcane_cost:
                    return False, f"Restless spirits require extra Arcane energy to bind. Need {arcane_cost} Arcane essences."
            
            # 3. Check Stable Limit
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one()
            
            stmt = select(Familiar).where(Familiar.user_id == user_id)
            result = await session.execute(stmt)
            familiars = result.scalars().all()
            
            if len(familiars) >= user.stable_limit:
                return False, f"Stable is full ({user.stable_limit}). Expand your stable or release a familiar."
            
            # 4. Perform Ritual (No internal commit)
            essence.count -= actual_cost
            if arcane_essence:
                arcane_essence.count -= arcane_cost
            
            await session.delete(spirit)
            
            familiar_name = NamingRules.generate_familiar_name(spirit.type, essence_type, spirit.rarity)
            
            familiar = Familiar(
                user_id=user_id,
                spirit_type=spirit.type,
                essence_type=essence_type,
                rarity=spirit.rarity,
                name=familiar_name
            )
            session.add(familiar)
            
            return True, familiar
            
        except Exception as e:
            logger.error(f"Error during ritual: {e}", exc_info=True)
            return False, "An ancient disturbance interrupted the ritual. Please try again."

    @staticmethod
    async def delete_familiar(session: AsyncSession, user_id: int, familiar_id: int):
        """Deletes a familiar. Does NOT commit."""
        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        if familiar:
            await session.delete(familiar)
            return True, familiar.name
        return False, "Familiar not found."
