from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.config import ChannelConfig
from typing import List

class ConfigService:
    @staticmethod
    async def toggle_channel(session: AsyncSession, channel_id: int, guild_id: int) -> bool:
        stmt = select(ChannelConfig).where(ChannelConfig.channel_id == channel_id)
        result = await session.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            config = ChannelConfig(channel_id=channel_id, guild_id=guild_id, is_active=True)
            session.add(config)
            new_state = True
        else:
            config.is_active = not config.is_active
            new_state = config.is_active
        
        await session.commit()
        return new_state

    @staticmethod
    async def get_guild_active_channels(session: AsyncSession, guild_id: int) -> List[ChannelConfig]:
        stmt = select(ChannelConfig).where(
            ChannelConfig.guild_id == guild_id, 
            ChannelConfig.is_active == True
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_active_channels(session: AsyncSession) -> List[ChannelConfig]:
        stmt = select(ChannelConfig).where(ChannelConfig.is_active == True)
        result = await session.execute(stmt)
        return list(result.scalars().all())
