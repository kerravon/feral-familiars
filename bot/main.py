import asyncio
import discord
from discord.ext import commands, tasks
import random
import logging
from typing import Optional

from bot.db import init_db, AsyncSessionLocal
from bot.services.encounter_service import EncounterService
from bot.services.passive_service import PassiveService
from bot.services.config_service import ConfigService
from bot.utils.constants import GameConstants
from bot.utils.config import Config

# Setup Logging
Config.validate()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeralFamiliars")

class FeralFamiliarsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.initial_extensions = [
            'bot.commands.general',
            'bot.commands.game',
            'bot.commands.trade',
            'bot.commands.admin',
        ]

    async def setup_hook(self):
        await init_db()
        
        # Load extensions (Cogs)
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(self.initial_extensions)
                logger.info(f"Loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}")

        # Register background tasks
        self.spawn_loop.start()
        self.cleanup_loop.start()
        logger.info("Bot setup complete.")

    @tasks.loop(seconds=Config.CLEANUP_INTERVAL_SECONDS)
    async def cleanup_loop(self):
        async with AsyncSessionLocal() as session:
            await ConfigService.cleanup_expired_lures(session)
            expired_encounters = await EncounterService.get_expired_encounters(session)
            if expired_encounters:
                logger.info(f"Cleanup: Found {len(expired_encounters)} expired encounters.")
            
            for e in expired_encounters:
                # --- Soul Anchor (Restless Passive) ---
                if e.type == "spirit":
                    from sqlalchemy import select
                    from bot.models.familiar import Familiar
                    from datetime import datetime
                    now = datetime.now()
                    
                    stmt = select(Familiar).where(
                        Familiar.is_active == True,
                        Familiar.spirit_type == GameConstants.RESTLESS,
                        Familiar.active_until > now
                    ).limit(1)
                    res = await session.execute(stmt)
                    anchor_fam = res.scalar_one_or_none()
                    
                    if anchor_fam:
                        chances = {"common": 0.2, "uncommon": 0.3, "rare": 0.4, "legendary": 0.5}
                        if random.random() < chances.get(anchor_fam.rarity, 0.2):
                            from datetime import timedelta
                            e.expires_at = now + timedelta(seconds=30)
                            await session.commit()
                            
                            try:
                                channel = self.get_channel(e.channel_id) or await self.fetch_channel(e.channel_id)
                                msg = await channel.fetch_message(e.message_id)
                                embed = msg.embeds[0]
                                user = self.get_user(anchor_fam.user_id) or await self.fetch_user(anchor_fam.user_id)
                                user_name = user.display_name if user else "A mysterious master"
                                embed.set_footer(text=f"✨ SOUL ANCHOR: {user_name}'s {anchor_fam.name} has anchored this spirit for +30s!")
                                await msg.edit(embed=embed)
                                logger.info(f"Soul Anchor saved spirit {e.id}")
                                continue
                            except: pass

                # 1. Attempt Visual Fade
                try:
                    channel = self.get_channel(e.channel_id) or await self.fetch_channel(e.channel_id)
                    msg = await channel.fetch_message(e.message_id)
                    embed = msg.embeds[0]
                    
                    if e.type == "essence":
                        embed.title = "✨ The Essence has faded..."
                        embed.description = "The mystical energy has disappeared back into the ether."
                    else:
                        embed.title = "🕯️ The Spirit has vanished..."
                        embed.description = "The mystical creature has returned to the spirit realm."
                        
                    embed.set_image(url=None)
                    embed.color = discord.Color.dark_grey()
                    embed.set_footer(text=None) # Clear anchor info
                    await msg.edit(embed=embed)
                    logger.info(f"Faded expired message {e.message_id}")
                except Exception as ex:
                    # Message might be deleted, just log and continue
                    logger.debug(f"Could not fade message {e.message_id}: {ex}")

                # 2. Finalize Database State
                e.is_active = False
                await session.commit()

    @cleanup_loop.before_loop
    async def before_cleanup_loop(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=Config.SPAWN_INTERVAL_MINUTES)
    async def spawn_loop(self):
        async with AsyncSessionLocal() as session:
            active_configs = await ConfigService.get_active_channels(session)
            
            for config in active_configs:
                channel = self.get_channel(config.channel_id)
                if not channel: continue
                
                # Check for active Lure
                now = datetime.now()
                is_lured = config.active_lure_type and config.lure_expires_at and config.lure_expires_at > now
                
                # Roll for spawn (100% if lured, otherwise random)
                if not is_lured:
                    if random.randint(1, 100) > Config.SPAWN_CHANCE_PERCENT:
                        continue
                    spawn_type = "spirit" if random.random() < 0.2 else "essence"
                else:
                    spawn_type = config.active_lure_type
                    logger.info(f"Lure active in {channel.name}: Spawning {spawn_type}")

                encounter = await EncounterService.spawn_encounter(session, channel.id, channel.guild.id, spawn_type)
                
                if encounter:
                    title = f"A {encounter.subtype} {encounter.type.title()} has appeared!"
                    if is_lured:
                        title = f"✨ INCENSE: {title}"
                    
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
                    logger.info(f"Spawned {type} in {channel.name} ({channel.guild.name})")

    @spawn_loop.before_loop
    async def before_spawn_loop(self):
        await self.wait_until_ready()

bot = FeralFamiliarsBot()

# --- Events ---

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower().strip()

    # Manual Sync for testing
    if content == "!sync" and message.author.guild_permissions.manage_guild:
        bot.tree.copy_global_to(guild=message.guild)
        await bot.tree.sync(guild=message.guild)
        await message.reply("✅ Slash commands synced INSTANTLY to this server!")
        return

    # Manual Spawn for testing
    if content.startswith("!testspawn") and message.author.guild_permissions.manage_channels:
        parts = content.split()
        target_type = parts[1] if len(parts) > 1 else None
        target_subtype = parts[2].title() if len(parts) > 2 else None
        target_rarity = parts[3].lower() if len(parts) > 3 else None

        async with AsyncSessionLocal() as session:
            if not target_type:
                target_type = "spirit" if random.random() < 0.3 else "essence"
            
            encounter = await EncounterService.spawn_encounter(
                session, message.channel.id, message.guild.id, target_type,
                override_subtype=target_subtype, override_rarity=target_rarity
            )
            
            if encounter:
                embed = discord.Embed(
                    title=f"A {encounter.subtype} {encounter.type.title()} has appeared!",
                    description=f"Type `bind` to capture this {encounter.type}." if encounter.type == "essence" else f"Type `bind spirit` to capture this {encounter.type}!",
                    color=discord.Color.blue() if encounter.type == "essence" else discord.Color.purple()
                )
                if encounter.type == "essence":
                    embed.set_image(url=GameConstants.ESSENCE_IMAGES.get(encounter.subtype))
                else:
                    embed.set_image(url=GameConstants.SPIRIT_IMAGES.get(encounter.subtype))
                if encounter.rarity:
                    embed.add_field(name="Rarity", value=encounter.rarity.upper())
                if getattr(encounter, "_temp_anchor_active", False):
                    embed.set_footer(text="✨ Temporal Anchor Active: Spawns stay 15s longer!")

                msg = await message.channel.send(embed=embed)
                encounter.message_id = msg.id
                await session.commit()
            else:
                await message.reply("An encounter is already active in this channel.")
        return

    # Manual Familiar for testing
    if content.startswith("!givefamiliar") and message.author.guild_permissions.manage_guild:
        parts = content.split()
        etype = parts[1].title() if len(parts) > 1 else "Fire"
        rarity = parts[2].lower() if len(parts) > 2 else "common"
        stype = parts[3].title() if len(parts) > 3 else "Feline"

        if etype not in GameConstants.ESSENCES or rarity not in GameConstants.RARITIES:
            await message.reply(f"Invalid type or rarity. Types: {GameConstants.ESSENCES}, Rarities: {GameConstants.RARITIES}")
            return

        async with AsyncSessionLocal() as session:
            from bot.services.inventory_service import InventoryService
            await InventoryService.get_or_create_user(session, message.author.id)
            adj = random.choice(GameConstants.ESSENCE_ADJECTIVES[etype][rarity])
            noun = random.choice(GameConstants.SPIRIT_NOUNS.get(stype, GameConstants.SPIRIT_NOUNS["Feline"])[rarity])
            fname = f"DEBUG {adj} {noun}"

            from bot.models.familiar import Familiar
            new_fam = Familiar(user_id=message.author.id, spirit_type=stype, essence_type=etype, rarity=rarity, name=fname)
            session.add(new_fam)
            await session.commit()
            await message.reply(f"🎁 **Debug Gift:** You have received **{fname}**!")
        return

    # Manual Lure for testing
    if content.startswith("!givelure") and message.author.guild_permissions.manage_guild:
        parts = content.split()
        # Usage: !givelure [essence/spirit] [minutes]
        ltype = parts[1].lower() if len(parts) > 1 else "essence"
        mins = int(parts[2]) if len(parts) > 2 else 30

        async with AsyncSessionLocal() as session:
            from bot.services.inventory_service import InventoryService
            user = await InventoryService.get_or_create_user(session, message.author.id)
            if ltype == "spirit":
                user.stored_spirit_lure_mins += mins
            else:
                user.stored_essence_lure_mins += mins
            await session.commit()
            await message.reply(f"🕯️ **Debug Lure:** Added **{mins} minutes** of {ltype} incense to your inventory.")
        return

    if content in ["bind", "bind spirit"]:
        logger.info(f"Capture attempt by {message.author.name}: {content}")
        async with AsyncSessionLocal() as session:
            encounter, result = await EncounterService.process_capture_attempt(session, message.channel.id, message.author.id, content)
            if encounter:
                await message.reply(result)
                await asyncio.sleep(0.5)
                try:
                    msg = await message.channel.fetch_message(encounter.message_id)
                    new_embed = discord.Embed(
                        title=f"Captured by {message.author.display_name}!",
                        description=f"The {encounter.subtype} {encounter.type} has been bound.",
                        color=discord.Color.green()
                    )
                    if encounter.type == "essence":
                        bound_url = GameConstants.BOUND_IMAGES.get(encounter.subtype)
                    else:
                        bound_url = GameConstants.SPIRIT_BOUND_IMAGES.get(encounter.subtype)
                    
                    if bound_url:
                        new_embed.set_image(url=bound_url)
                    if encounter.rarity:
                        new_embed.add_field(name="Rarity", value=encounter.rarity.upper())
                    await msg.edit(embed=new_embed)
                except Exception as e:
                    logger.error(f"Failed to update capture message: {e}")
                
                if encounter.type == "essence":
                    passive_msg = await PassiveService.trigger_passive_bonus(session, message.author.id, encounter.subtype)
                    if passive_msg:
                        await message.channel.send(passive_msg)
            elif result:
                await message.reply(result, delete_after=5)

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
