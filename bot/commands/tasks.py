import asyncio
import discord
from discord.ext import commands, tasks
import random
import logging
import datetime
from bot.db import AsyncSessionLocal
from bot.services.encounter_service import EncounterService
from bot.services.config_service import ConfigService
from bot.ui.embeds import EmbedFactory
from bot.domain.enums import EncounterType, EssenceType, SpiritType
from bot.domain.constants import GameRules, AssetUrls
from bot.utils.config import Config

logger = logging.getLogger("FeralFamiliars")

class TaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spawn_loop.start()
        self.cleanup_loop.start()

    def cog_unload(self):
        self.spawn_loop.cancel()
        self.cleanup_loop.cancel()

    @tasks.loop(seconds=Config.CLEANUP_INTERVAL_SECONDS)
    async def cleanup_loop(self):
        async with AsyncSessionLocal() as session:
            await ConfigService.cleanup_expired_lures(session)
            expired_encounters = await EncounterService.get_expired_encounters(session)
            
            for e in expired_encounters:
                # --- Soul Anchor (Restless Passive) ---
                anchor_fam = await EncounterService.handle_soul_anchor(session, e)
                if anchor_fam:
                    try:
                        channel = self.bot.get_channel(e.channel_id) or await self.bot.fetch_channel(e.channel_id)
                        msg = await channel.fetch_message(e.message_id)
                        embed = msg.embeds[0]
                        user = self.bot.get_user(anchor_fam.user_id) or await self.bot.fetch_user(anchor_fam.user_id)
                        user_name = user.display_name if user else "A mysterious master"
                        embed.set_footer(text=f"✨ SOUL ANCHOR: {user_name}'s {anchor_fam.name} has anchored this spirit for +30s!")
                        await msg.edit(embed=embed)
                        continue
                    except: pass

                # Visual Fade
                try:
                    channel = self.bot.get_channel(e.channel_id) or await self.bot.fetch_channel(e.channel_id)
                    msg = await channel.fetch_message(e.message_id)
                    embed = msg.embeds[0]
                    
                    if e.type == EncounterType.ESSENCE:
                        embed.title = "✨ The Essence has faded..."
                        embed.description = "The mystical energy has disappeared back into the ether."
                    else:
                        embed.title = "🕯️ The Spirit has vanished..."
                        embed.description = "The mystical creature has returned to the spirit realm."
                        
                    embed.set_image(url=AssetUrls.FADED_IMAGE)
                    embed.color = discord.Color.dark_grey()
                    embed.set_footer(text=None)
                    await msg.edit(embed=embed)
                    
                    e.is_active = False
                    await session.commit()

                except discord.NotFound:
                    e.is_active = False
                    await session.commit()
                except Exception as ex:
                    logger.warning(f"Could not fade message {e.message_id}: {ex}")

    @cleanup_loop.before_loop
    async def before_cleanup_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=Config.SPAWN_INTERVAL_SECONDS)
    async def spawn_loop(self):
        async with AsyncSessionLocal() as session:
            active_configs = await ConfigService.get_active_channels(session)
            
            for config in active_configs:
                try:
                    channel = self.bot.get_channel(config.channel_id)
                    if not channel: continue
                    
                    now = datetime.datetime.now()
                    is_lured = config.active_lure_type and config.lure_expires_at and config.lure_expires_at > now
                    
                    if not is_lured:
                        activity_bonus = min(config.activity_score * GameRules.ACTIVITY_BONUS_PER_MSG, GameRules.ACTIVITY_BONUS_MAX)
                        pity_bonus = config.pity_count * GameRules.PITY_BONUS_PER_FAILED_TICK
                        total_chance = Config.SPAWN_CHANCE_PERCENT + activity_bonus + pity_bonus
                        
                        if random.randint(1, 100) > total_chance:
                            config.pity_count += 1
                            await session.commit()
                            continue
                        
                        config.activity_score = 0
                        config.pity_count = 0
                        spawn_type = EncounterType.SPIRIT if random.random() < 0.2 else EncounterType.ESSENCE
                        spawn_subtype = None
                    else:
                        spawn_type = EncounterType.ESSENCE if config.active_lure_type == LureType.PURE else EncounterType(config.active_lure_type.value)
                        spawn_subtype = config.active_lure_subtype.value if config.active_lure_subtype else None

                    encounter = await EncounterService.spawn_encounter(
                        session, channel.id, channel.guild.id, spawn_type, 
                        override_subtype=spawn_subtype
                    )
                    
                    if encounter:
                        await session.commit()
                        embed = EmbedFactory.create_encounter_embed(encounter, is_lured)
                        msg = await channel.send(embed=embed)
                        encounter.message_id = msg.id
                        await session.commit()
                except Exception as e:
                    logger.error(f"Error in spawn_loop: {e}", exc_info=True)
                    continue

    @spawn_loop.before_loop
    async def before_spawn_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TaskCog(bot))
