import asyncio
import discord
from discord.ext import commands, tasks
import random
import logging
import datetime
from bot.db import AsyncSessionLocal
from bot.services.encounter_service import EncounterService
from bot.services.config_service import ConfigService
from bot.utils.constants import GameConstants
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
            if expired_encounters:
                logger.info(f"Cleanup: Found {len(expired_encounters)} expired encounters.")
            
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
                        logger.info(f"Soul Anchor saved spirit {e.id}")
                        continue
                    except: pass

                # 1. Attempt Visual Fade
                try:
                    channel = self.bot.get_channel(e.channel_id) or await self.bot.fetch_channel(e.channel_id)
                    msg = await channel.fetch_message(e.message_id)
                    embed = msg.embeds[0]
                    
                    if e.type == "essence":
                        embed.title = "✨ The Essence has faded..."
                        embed.description = "The mystical energy has disappeared back into the ether."
                    else:
                        embed.title = "🕯️ The Spirit has vanished..."
                        embed.description = "The mystical creature has returned to the spirit realm."
                        
                    embed.set_image(url="https://i.ibb.co/NR7brt7/faded.webp")
                    embed.color = discord.Color.dark_grey()
                    embed.set_footer(text=None)
                    await msg.edit(embed=embed)
                    logger.info(f"Faded expired message {e.message_id}")
                    
                    # 2. Finalize Database State ONLY if edit worked
                    e.is_active = False
                    await session.commit()

                except discord.NotFound:
                    logger.info(f"Message {e.message_id} not found (deleted). Closing encounter.")
                    e.is_active = False
                    await session.commit()
                except Exception as ex:
                    logger.warning(f"Could not fade message {e.message_id}, will retry: {ex}")

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
                        # Dynamic Spawn Chance
                        activity_bonus = min(config.activity_score * 0.5, 20)
                        pity_bonus = config.pity_count * 2
                        total_chance = Config.SPAWN_CHANCE_PERCENT + activity_bonus + pity_bonus
                        
                        if random.randint(1, 100) > total_chance:
                            config.pity_count += 1
                            await session.commit()
                            continue
                        
                        config.activity_score = 0
                        config.pity_count = 0
                        await session.commit()
                        
                        spawn_type = "spirit" if random.random() < 0.2 else "essence"
                        spawn_subtype = None
                    else:
                        spawn_type = "essence" if config.active_lure_type == "pure" else config.active_lure_type
                        spawn_subtype = config.active_lure_subtype
                        logger.info(f"Lure active in {channel.name}: Spawning {spawn_type} ({spawn_subtype or 'random'})")

                    encounter = await EncounterService.spawn_encounter(
                        session, channel.id, channel.guild.id, spawn_type, 
                        override_subtype=spawn_subtype
                    )
                    
                    if encounter:
                        title = f"A {encounter.subtype} {encounter.type.title()} has appeared!"
                        if is_lured: title = f"✨ INCENSE: {title}"
                        
                        embed = discord.Embed(
                            title=title,
                            description=f"Type `bind` to capture this {encounter.type}." if spawn_type == "essence" else f"Type `bind spirit` to capture this {encounter.type}!",
                            color=discord.Color.gold() if is_lured else (discord.Color.blue() if spawn_type == "essence" else discord.Color.purple())
                        )
                        if spawn_type == "essence":
                            embed.set_image(url=GameConstants.ESSENCE_IMAGES.get(encounter.subtype))
                        else:
                            embed.set_image(url=GameConstants.SPIRIT_IMAGES.get(encounter.subtype))
                        
                        if encounter.rarity:
                            embed.add_field(name="Rarity", value=encounter.rarity.upper())
                        
                        if getattr(encounter, "_temp_anchor_active", False):
                            embed.set_footer(text="✨ Temporal Anchor Active: Spawns stay 15s longer!")

                        msg = await channel.send(embed=embed)
                        encounter.message_id = msg.id
                        await session.commit()
                        logger.info(f"Spawned {spawn_type} in {channel.name} (MsgID: {msg.id})")
                except Exception as e:
                    logger.error(f"Error in spawn_loop for channel {config.channel_id}: {e}", exc_info=True)
                    continue

    @spawn_loop.before_loop
    async def before_spawn_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TaskCog(bot))
