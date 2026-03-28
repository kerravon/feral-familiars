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
            expired_encounters = await EncounterService.get_expired_encounters(session)
            
            for e in expired_encounters:
                # --- Soul Anchor (Restless Passive) ---
                if e.type == "spirit":
                    # Check if any user in guild has an active RESONATING Restless familiar
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
                        # 20-50% chance based on rarity
                        chances = {"common": 0.2, "uncommon": 0.3, "rare": 0.4, "legendary": 0.5}
                        if random.random() < chances.get(anchor_fam.rarity, 0.2):
                            # SAVE the spirit!
                            from datetime import timedelta
                            e.expires_at = now + timedelta(seconds=30)
                            e.is_active = True
                            await session.commit()
                            
                            channel = self.get_channel(e.channel_id) or await self.fetch_channel(e.channel_id)
                            msg = await channel.fetch_message(e.message_id)
                            embed = msg.embeds[0]
                            
                            # Fetch user name for the public boost
                            user = self.get_user(anchor_fam.user_id) or await self.fetch_user(anchor_fam.user_id)
                            user_name = user.display_name if user else "A mysterious master"
                            
                            embed.set_footer(text=f"✨ SOUL ANCHOR: {user_name}'s {anchor_fam.name} has anchored this spirit for +30s!")
                            await msg.edit(embed=embed)
                            logger.info(f"Soul Anchor saved spirit {e.id} (Owner: {user_name})")
                            continue

                channel = self.get_channel(e.channel_id)
                if not channel:
                    try:
                        channel = await self.fetch_channel(e.channel_id)
                    except: continue
                
                try:
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
                    await msg.edit(embed=embed)
                    logger.info(f"Cleaned up expired encounter {e.id}")
                except Exception as ex:
                    logger.warning(f"Could not update expired message {e.message_id}: {ex}")

    @cleanup_loop.before_loop
    async def before_cleanup_loop(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=Config.SPAWN_INTERVAL_MINUTES)
    async def spawn_loop(self):
        async with AsyncSessionLocal() as session:
            active_configs = await ConfigService.get_active_channels(session)
            logger.info(f"Spawn check: {len(active_configs)} active channels. Chance: {Config.SPAWN_CHANCE_PERCENT}%")
            
            for config in active_configs:
                channel = self.get_channel(config.channel_id)
                if not channel: continue
                
                # Roll for spawn
                if random.randint(1, 100) > Config.SPAWN_CHANCE_PERCENT:
                    continue

                type = "spirit" if random.random() < 0.2 else "essence"
                encounter = await EncounterService.spawn_encounter(session, channel.id, channel.guild.id, type)
                
                if encounter:
                    embed = discord.Embed(
                        title=f"A {encounter.subtype} {encounter.type.title()} has appeared!",
                        description=f"Type `bind` to capture this {encounter.type}." if type == "essence" else f"Type `bind spirit` to capture this {encounter.type}!",
                        color=discord.Color.blue() if type == "essence" else discord.Color.purple()
                    )
                    if type == "essence":
                        embed.set_image(url=GameConstants.ESSENCE_IMAGES.get(encounter.subtype))
                    
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
                    bound_url = GameConstants.BOUND_IMAGES.get(encounter.subtype)
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
