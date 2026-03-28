import asyncio
import random
import discord
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db import AsyncSessionLocal
from bot.services.encounter_service import EncounterService
from bot.utils.constants import GameConstants

logger = logging.getLogger("FeralFamiliars")

class SurgeService:
    @staticmethod
    async def trigger_spirit_surge(bot, channel_id, guild_id, releaser_id, spirit_type, rarity):
        """
        30% chance to respawn the spirit.
        70% chance to splinter into 3 essences.
        Spawns occur in series with a delay.
        """
        await asyncio.sleep(2) # Brief pause after the release message
        
        chance = random.random()
        if chance < 0.30:
            # Respawn spirit
            await SurgeService._spawn_with_announcement(
                bot, channel_id, guild_id, "spirit", spirit_type, rarity, releaser_id,
                "✨ The released spirit lingers! Bind it quickly!"
            )
        else:
            # Splinter into 3 essences
            for i in range(3):
                await SurgeService._spawn_with_announcement(
                    bot, channel_id, guild_id, "essence", spirit_type, None, releaser_id,
                    f"💎 A fragment of the spirit has splintered! ({i+1}/3)"
                )
                await asyncio.sleep(5) # Delay between splinter spawns

    @staticmethod
    async def trigger_familiar_surge(bot, channel_id, guild_id, releaser_id, spirit_type, rarity, essence_type):
        """
        Guaranteed: Original Spirit + 5 random Essences.
        """
        await asyncio.sleep(2)
        
        # 1. The Spirit
        await SurgeService._spawn_with_announcement(
            bot, channel_id, guild_id, "spirit", spirit_type, rarity, releaser_id,
            "🕯️ The familiar's soul has returned to the wild! Bind it!"
        )
        await asyncio.sleep(6)
        
        # 2. 5 random essences
        for i in range(5):
            etype = random.choice(GameConstants.ESSENCES)
            await SurgeService._spawn_with_announcement(
                bot, channel_id, guild_id, "essence", etype, None, releaser_id,
                f"✨ Prismatic Burst: An essence has materialized! ({i+1}/5)"
            )
            await asyncio.sleep(4)

    @staticmethod
    async def _spawn_with_announcement(bot, channel_id, guild_id, type, subtype, rarity, releaser_id, announcement):
        async with AsyncSessionLocal() as session:
            encounter = await EncounterService.spawn_encounter(
                session, channel_id, guild_id, type, 
                override_subtype=subtype, 
                override_rarity=rarity,
                blacklisted_user_id=releaser_id
            )
            
            if encounter:
                channel = bot.get_channel(channel_id)
                if not channel:
                    channel = await bot.fetch_channel(channel_id)
                
                embed = discord.Embed(
                    title="🌌 RESONANCE SURGE!",
                    description=f"{announcement}\n\nType `bind` to capture!" if type == "essence" else f"{announcement}\n\nType `bind spirit` to capture!",
                    color=discord.Color.gold()
                )
                
                if type == "essence":
                    embed.set_image(url=GameConstants.ESSENCE_IMAGES.get(subtype))
                else:
                    embed.set_image(url=GameConstants.SPIRIT_IMAGES.get(subtype))
                if rarity:
                    embed.add_field(name="Rarity", value=rarity.upper())
                
                embed.set_footer(text="Energy released by a former master. Releaser cannot bind.")
                
                msg = await channel.send(embed=embed)
                encounter.message_id = msg.id
                await session.commit()
            else:
                logger.warning(f"Surge failed to spawn {type} in {channel_id} - channel busy.")
