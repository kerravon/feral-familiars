from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.config import ChannelConfig
from bot.models.base import User
from bot.domain.enums import LureType, EssenceType
from typing import List, Tuple
from datetime import datetime, timedelta

class ConfigService:
    @staticmethod
    async def get_guild_active_channels(session: AsyncSession, guild_id: int) -> List[ChannelConfig]:
        stmt = select(ChannelConfig).where(
            ChannelConfig.guild_id == guild_id, 
            ChannelConfig.is_active == True
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def toggle_channel(session: AsyncSession, channel_id: int, guild_id: int) -> bool:
        stmt = select(ChannelConfig).where(ChannelConfig.channel_id == channel_id)
        result = await session.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            config = ChannelConfig(channel_id=channel_id, guild_id=guild_id, is_active=True)
            session.add(config)
        else:
            config.is_active = not config.is_active
        
        return config.is_active

    @staticmethod
    async def get_active_channels(session: AsyncSession) -> List[ChannelConfig]:
        stmt = select(ChannelConfig).where(ChannelConfig.is_active == True)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def ignite_lure(session: AsyncSession, user_id: int, channel_id: int, lure_type: LureType, minutes: int, element: EssenceType = None):
        """Sets an active lure. Does NOT commit."""
        stmt = select(ChannelConfig).where(ChannelConfig.channel_id == channel_id)
        result = await session.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            return False, "This channel is not initialized. Toggle it first."

        config.active_lure_type = lure_type
        config.active_lure_subtype = element
        config.lure_expires_at = datetime.now() + timedelta(minutes=minutes)
        
        return True, f"Ignited **{minutes} minutes** of {lure_type.value} resonance."

    @staticmethod
    async def increment_activity(session: AsyncSession, channel_id: int):
        """Increments the activity score for an active channel. Does NOT commit."""
        stmt = update(ChannelConfig).where(
            ChannelConfig.channel_id == channel_id,
            ChannelConfig.is_active == True
        ).values(activity_score=ChannelConfig.activity_score + 1)
        await session.execute(stmt)

    @staticmethod
    async def cleanup_expired_lures(session: AsyncSession):
        """Clears lures that have passed their expiry time. Does NOT commit."""
        now = datetime.now()
        stmt = update(ChannelConfig).where(
            ChannelConfig.lure_expires_at < now
        ).values(active_lure_type=None, active_lure_subtype=None, lure_expires_at=None)
        await session.execute(stmt)
