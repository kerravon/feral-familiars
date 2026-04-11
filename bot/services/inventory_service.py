from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.base import User
from bot.models.essence import Essence
from bot.models.familiar import Spirit, Familiar
from bot.utils.config import Config
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
            essence = Essence(user_id=user_id, type=type, count=min(count, Config.MAX_ESSENCES))
            session.add(essence)
        else:
            essence.count = min(essence.count + count, Config.MAX_ESSENCES)
        
        await session.commit()

    @staticmethod
    async def add_spirit(session: AsyncSession, user_id: int, type: str, rarity: str):
        await InventoryService.get_or_create_user(session, user_id)
        
        # Check spirit limit
        stmt = select(Spirit).where(Spirit.user_id == user_id)
        result = await session.execute(stmt)
        spirits = result.scalars().all()
        
        if len(spirits) >= Config.MAX_SPIRITS:
            return False, f"Spirit inventory full (max {Config.MAX_SPIRITS})."
        
        spirit = Spirit(user_id=user_id, type=type, rarity=rarity)
        session.add(spirit)
        await session.commit()
        return True, spirit

    @staticmethod
    async def deduct_essence(session: AsyncSession, user_id: int, type: str, count: int) -> bool:
        """Deducts essence from a user's inventory. Returns True if successful, False if insufficient."""
        stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == type)
        result = await session.execute(stmt)
        essence = result.scalar_one_or_none()
        
        if not essence or essence.count < count:
            return False
            
        essence.count -= count
        if essence.count == 0:
            await session.delete(essence)
            
        await session.commit()
        return True

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

    @staticmethod
    async def delete_spirit(session: AsyncSession, user_id: int, spirit_id: int):
        stmt = select(Spirit).where(Spirit.id == spirit_id, Spirit.user_id == user_id)
        result = await session.execute(stmt)
        spirit = result.scalar_one_or_none()
        if spirit:
            await session.delete(spirit)
            await session.commit()
            return True
        return False
