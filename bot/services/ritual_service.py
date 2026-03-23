from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from bot.models.familiar import Spirit, Familiar
from bot.models.essence import Essence
from bot.models.base import User
from bot.utils.constants import GameConstants
import random

class RitualService:
    @staticmethod
    async def create_familiar(
        session: AsyncSession, 
        user_id: int, 
        spirit_id: int, 
        essence_type: str
    ):
        # 1. Fetch Spirit
        stmt = select(Spirit).where(Spirit.id == spirit_id, Spirit.user_id == user_id)
        result = await session.execute(stmt)
        spirit = result.scalar_one_or_none()
        
        if not spirit:
            return False, "Spirit not found in your inventory."
        
        # 2. Check Cost
        actual_cost = GameConstants.COST_MAP[spirit.rarity]
        
        stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == essence_type)
        result = await session.execute(stmt)
        essence = result.scalar_one_or_none()
        
        if not essence or essence.count < actual_cost:
            return False, f"Insufficient {essence_type} essences. Need {actual_cost}, you have {essence.count if essence else 0}."
        
        # 3. Check Stable Limit
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one()
        
        stmt = select(Familiar).where(Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiars = result.scalars().all()
        
        if len(familiars) >= user.stable_limit:
            return False, f"Stable is full ({user.stable_limit}). Expand your stable or release a familiar."
        
        # 4. Perform Ritual
        # Consume essence
        essence.count -= actual_cost
        
        # Consume spirit
        await session.delete(spirit)
        
        # Create dynamic familiar name
        adj = random.choice(GameConstants.ESSENCE_ADJECTIVES[essence_type][spirit.rarity])
        noun = random.choice(GameConstants.SPIRIT_NOUNS[spirit.type][spirit.rarity])
        familiar_name = f"{adj} {noun}"
        
        familiar = Familiar(
            user_id=user_id,
            spirit_type=spirit.type,
            essence_type=essence_type,
            rarity=spirit.rarity,
            name=familiar_name
        )
        session.add(familiar)
        await session.commit()
        
        return True, familiar
