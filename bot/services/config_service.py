from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.config import ChannelConfig
from bot.models.base import User
from typing import List, Tuple
from datetime import datetime, timedelta

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

    @staticmethod
    async def activate_lure(session: AsyncSession, user_id: int, channel_id: int, lure_type: str, minutes: int, subtype: str = None) -> Tuple[bool, str]:
        """Burns stored lure minutes to activate a lure in a channel."""
        stmt_u = select(User).where(User.id == user_id)
        res_u = await session.execute(stmt_u)
        user = res_u.scalar_one_or_none()
        
        stmt_c = select(ChannelConfig).where(ChannelConfig.channel_id == channel_id)
        res_c = await session.execute(stmt_c)
        config = res_c.scalar_one_or_none()

        if not user: return False, "User not found."
        if not config or not config.is_active: return False, "Spawns are not enabled in this channel."
        
        if lure_type == "essence":
            if user.stored_essence_lure_mins < minutes:
                return False, f"Not enough Essence Incense. You have {user.stored_essence_lure_mins} mins."
            user.stored_essence_lure_mins -= minutes
        elif lure_type == "spirit":
            if user.stored_spirit_lure_mins < minutes:
                return False, f"Not enough Spirit Incense. You have {user.stored_spirit_lure_mins} mins."
            user.stored_spirit_lure_mins -= minutes
        elif lure_type == "pure":
            if user.stored_pure_lure_mins < minutes:
                return False, f"Not enough Pure Incense. You have {user.stored_pure_lure_mins} mins."
            user.stored_pure_lure_mins -= minutes
            if not subtype: return False, "Pure Incense requires a target element."

        now = datetime.now()
        # If a lure is already active, extend it. Otherwise start fresh.
        if config.active_lure_type == lure_type and config.active_lure_subtype == subtype and config.lure_expires_at and config.lure_expires_at > now:
            config.lure_expires_at += timedelta(minutes=minutes)
        else:
            config.active_lure_type = lure_type
            config.active_lure_subtype = subtype
            config.lure_expires_at = now + timedelta(minutes=minutes)
        
        await session.commit()
        return True, f"Ignited **{minutes} minutes** of {lure_type.title()} Incense!"

    @staticmethod
    async def cleanup_expired_lures(session: AsyncSession):
        """Clears lures that have passed their expiry time."""
        now = datetime.now()
        stmt = update(ChannelConfig).where(
            ChannelConfig.lure_expires_at < now
        ).values(active_lure_type=None, active_lure_subtype=None, lure_expires_at=None)
        await session.execute(stmt)
        await session.commit()
