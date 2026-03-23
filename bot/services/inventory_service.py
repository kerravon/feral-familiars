from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.base import User
from bot.models.essence import Essence
from bot.models.familiar import Spirit, Familiar
from typing import List, Optional

class InventoryService:
    @staticmethod
    async def get_or_create_user(session: AsyncSession, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    @staticmethod
    async def add_essence(session: AsyncSession, user_id: int, type: str, count: int = 1):
        # Ensure user exists
        await InventoryService.get_or_create_user(session, user_id)
        
        stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == type)
        result = await session.execute(stmt)
        essence = result.scalar_one_or_none()
        
        if not essence:
            essence = Essence(user_id=user_id, type=type, count=count)
            session.add(essence)
        else:
            essence.count += count
        
        await session.commit()

    @staticmethod
    async def add_spirit(session: AsyncSession, user_id: int, type: str, rarity: str):
        await InventoryService.get_or_create_user(session, user_id)
        
        # Check spirit limit
        stmt = select(Spirit).where(Spirit.user_id == user_id)
        result = await session.execute(stmt)
        spirits = result.scalars().all()
        
        if len(spirits) >= 5: # Default limit
            return False, "Spirit inventory full (max 5)."
        
        spirit = Spirit(user_id=user_id, type=type, rarity=rarity)
        session.add(spirit)
        await session.commit()
        return True, spirit

    @staticmethod
    async def get_essences(session: AsyncSession, user_id: int) -> List[Essence]:
        stmt = select(Essence).where(Essence.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_spirits(session: AsyncSession, user_id: int) -> List[Spirit]:
        stmt = select(Spirit).where(Spirit.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_familiars(session: AsyncSession, user_id: int) -> List[Familiar]:
        stmt = select(Familiar).where(Familiar.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())
