import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models.config import GuildConfig
import logging

logger = logging.getLogger("FeralFamiliars")

class GuildService:
    @staticmethod
    async def get_guild_config(session: AsyncSession, guild_id: int) -> GuildConfig:
        stmt = select(GuildConfig).where(GuildConfig.guild_id == guild_id)
        result = await session.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            config = GuildConfig(guild_id=guild_id)
            session.add(config)
            await session.commit()
            await session.refresh(config)
        return config

    @staticmethod
    async def add_to_pot(session: AsyncSession, guild_id: int, bot, channel_id: int, essence_amount: int = 0, spirit_amount: int = 0):
        config = await GuildService.get_guild_config(session, guild_id)
        
        config.pot_essence_total += essence_amount
        config.pot_spirit_total += spirit_amount
        
        logger.info(f"Added to Pot in Guild {guild_id}: {essence_amount} essences, {spirit_amount} spirits. Total: {config.pot_essence_total}/{config.surge_threshold}")
        
        if config.pot_essence_total >= config.surge_threshold:
            logger.info(f"THRESHOLD REACHED in Guild {guild_id}! Triggering Prismatic Surge.")
            # Reset pot before triggering to prevent double-triggers if it takes time
            config.pot_essence_total = 0
            await session.commit()
            
            # Trigger surge in the channel where the last tax was paid
            from bot.services.surge_service import SurgeService
            asyncio.create_task(SurgeService.trigger_well_of_souls_surge(bot, channel_id, guild_id))
        else:
            await session.commit()
