import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import random
import logging
from typing import Optional
from discord import app_commands

from bot.db import init_db, AsyncSessionLocal
from bot.services.encounter_service import EncounterService
from bot.services.inventory_service import InventoryService
from bot.services.ritual_service import RitualService
from bot.services.config_service import ConfigService
from bot.services.passive_service import PassiveService
from bot.services.bestow_service import BestowService
from bot.services.transmute_service import TransmuteService
from bot.utils.ui import TransmuteView
from bot.models.familiar import Familiar
from bot.utils.constants import GameConstants

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeralFamiliars")

class FeralFamiliarsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await init_db()
        # Register background tasks
        self.spawn_loop.start()
        self.cleanup_loop.start()
        logger.info("Bot setup complete.")

    @tasks.loop(seconds=10)
    async def cleanup_loop(self):
        async with AsyncSessionLocal() as session:
            expired_encounters = await EncounterService.get_expired_encounters(session)
            
            for e in expired_encounters:
                channel = self.get_channel(e.channel_id)
                if not channel:
                    channel = await self.fetch_channel(e.channel_id)
                
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

    @tasks.loop(minutes=2) # Check every 2 minutes
    async def spawn_loop(self):
        # Only spawn in channels configured as "active"
        async with AsyncSessionLocal() as session:
            active_configs = await ConfigService.get_active_channels(session)
            
            for config in active_configs:
                channel = self.get_channel(config.channel_id)
                if not channel: continue
                
                # Roll for spawn
                spawn_chance = int(os.getenv("SPAWN_CHANCE_PERCENT", "15"))
                if random.randint(1, 100) > spawn_chance:
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
                    
                    msg = await channel.send(embed=embed)
                    encounter.message_id = msg.id
                    await session.commit()
                    logger.info(f"Spawned {type} in {channel.name} ({channel.guild.name})")

    @spawn_loop.before_loop
    async def before_spawn_loop(self):
        await self.wait_until_ready()

bot = FeralFamiliarsBot()

# --- Slash Commands ---

@bot.tree.command(name="toggle-channel", description="Enable or disable essence spawns in this channel (Requires Manage Channels).")
async def toggle_channel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Only users with the **Manage Channels** permission can toggle spawns.", ephemeral=True)
        return
        
    async with AsyncSessionLocal() as session:
        is_active = await ConfigService.toggle_channel(session, interaction.channel_id, interaction.guild_id)
        
        # Get all active channels in the guild for a better response
        active_configs = await ConfigService.get_guild_active_channels(session, interaction.guild_id)
        channel_mentions = [f"<#{c.channel_id}>" for c in active_configs]
        
        status = "ACTIVE" if is_active else "INACTIVE"
        active_list = ", ".join(channel_mentions) if channel_mentions else "None"
        
        msg = f"✨ Spawns in this channel are now **{status}**.\n\n"
        msg += f"**Active Channels in this server:**\n{active_list}"
        
        await interaction.response.send_message(msg)

@bot.tree.command(name="inventory", description="View your essences and spirits or those of another user.")
async def inventory(interaction: discord.Interaction, user: Optional[discord.User] = None):
    target_user = user or interaction.user
    
    async with AsyncSessionLocal() as session:
        essences = await InventoryService.get_essences(session, target_user.id)
        spirits = await InventoryService.get_spirits(session, target_user.id)
        
        embed = discord.Embed(title=f"{target_user.name}'s Inventory", color=discord.Color.green())
        
        e_text = "\n".join([f"{e.type}: {e.count}" for e in essences]) or "No essences."
        embed.add_field(name="Essences", value=e_text, inline=True)
        
        s_text = "\n".join([f"ID: {s.id} - {s.rarity.title()} {s.type}" for s in spirits]) or "No spirits."
        embed.add_field(name="Spirits (Max 5)", value=s_text, inline=True)
        
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transmute", description="Start a ritual of transmutation (trade) with another player (5% Ritual Fee).")
async def transmute(interaction: discord.Interaction, user: discord.User):
    if user.id == interaction.user.id:
        await interaction.response.send_message("You cannot transmute with yourself!", ephemeral=True)
        return
    if user.bot:
        await interaction.response.send_message("You cannot transmute with a bot!", ephemeral=True)
        return

    async with AsyncSessionLocal() as session:
        trade = await TransmuteService.create_trade(session, interaction.user.id, user.id)
        
        view = TransmuteView(trade.id, interaction.user.id, user.id)
        
        embed = discord.Embed(
            title="✨ Ritual of Transmutation",
            description=f"<@{interaction.user.id}> has initiated a ritual with <@{user.id}>.",
            color=discord.Color.purple()
        )
        embed.add_field(name=f"{interaction.user.name}'s Offer", value="Empty\n*Fee: 0 essences*", inline=True)
        embed.add_field(name=f"{user.name}'s Offer", value="Empty\n*Fee: 0 essences*", inline=True)
        embed.set_footer(text="Click 'Offer' to add items. Both must 'Confirm' to complete.")

        await interaction.response.send_message(
            f"<@{user.id}>, <@{interaction.user.id}> wants to trade!",
            embed=embed,
            view=view
        )

@bot.tree.command(name="bestow", description="Gift essences or spirits to another player (YOU pay the Ritual Fee).")
@app_commands.describe(
    user="The player you are gifting to",
    essence_type="Type of essence to gift (Optional)",
    amount="Amount of essences to gift (Optional)",
    spirit_id="ID of the spirit to gift (Optional)",
    tax_payment="Essence YOU pay (Fee: 2% for essences | 1-12 for spirits based on rarity)"
)
async def bestow(
    interaction: discord.Interaction, 
    user: discord.User, 
    tax_payment: str,
    essence_type: Optional[str] = None, 
    amount: Optional[int] = None,
    spirit_id: Optional[int] = None
):
    if user.id == interaction.user.id:
        await interaction.response.send_message("You cannot bestow gifts to yourself!", ephemeral=True)
        return

    tax_payment = tax_payment.title()
    if tax_payment not in GameConstants.ESSENCES:
        await interaction.response.send_message(f"Invalid tax payment type. Choose: {', '.join(GameConstants.ESSENCES)}", ephemeral=True)
        return

    async with AsyncSessionLocal() as session:
        if essence_type and amount:
            essence_type = essence_type.title()
            success, result = await BestowService.bestow_essence(
                session, interaction.user.id, user.id, essence_type, amount, tax_payment
            )
        elif spirit_id:
            success, result = await BestowService.bestow_spirit(
                session, interaction.user.id, user.id, spirit_id, tax_payment
            )
        else:
            await interaction.response.send_message("You must specify either essences or a spirit to bestow.", ephemeral=True)
            return

        if success:
            await interaction.response.send_message(f"🎁 **Gift Bestowed!** {result}")
        else:
            await interaction.response.send_message(f"❌ **Bestowal Failed:** {result}", ephemeral=True)

@bot.tree.command(name="equip", description="Equip a familiar to gain its passive bonus.")
async def equip(interaction: discord.Interaction, familiar_id: int):
    async with AsyncSessionLocal() as session:
        from sqlalchemy import update, select
        await session.execute(
            update(Familiar).where(Familiar.user_id == interaction.user.id).values(is_active=False)
        )
        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == interaction.user.id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        if not familiar:
            await interaction.response.send_message("Familiar not found.", ephemeral=True)
            return
        familiar.is_active = True
        await session.commit()
        await interaction.response.send_message(f"✅ **{familiar.name}** is now your active familiar!")

@bot.tree.command(name="ritual", description="Combine a spirit and essences to create a familiar.")
async def ritual(interaction: discord.Interaction, spirit_id: int, essence_type: str):
    essence_type = essence_type.title()
    if essence_type not in GameConstants.ESSENCES:
        await interaction.response.send_message(f"Invalid essence type. Choose from: {', '.join(GameConstants.ESSENCES)}", ephemeral=True)
        return
    async with AsyncSessionLocal() as session:
        success, result = await RitualService.create_familiar(session, interaction.user.id, spirit_id, essence_type)
        if success:
            await interaction.response.send_message(f"✨ **Ritual Success!** You have created a **{result.name}**!")
        else:
            await interaction.response.send_message(f"❌ **Ritual Failed:** {result}", ephemeral=True)

@bot.tree.command(name="familiars", description="View your familiars in the stable.")
async def familiars(interaction: discord.Interaction):
    async with AsyncSessionLocal() as session:
        fams = await InventoryService.get_familiars(session, interaction.user.id)
        embed = discord.Embed(title=f"{interaction.user.name}'s Stable", color=discord.Color.gold())
        if not fams:
            embed.description = "No familiars yet. Perform a /ritual to create one!"
        else:
            for f in fams:
                status = "🟢 [ACTIVE]" if f.is_active else ""
                embed.add_field(name=f"{f.name} (ID: {f.id}) {status}", value=f"Type: {f.spirit_type}/{f.essence_type}\nRarity: {f.rarity.title()}", inline=False)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ritual-guide", description="View the guide for familiar creation, gifting, and taxes.")
async def ritual_guide(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 The Mystic's Guide to Rituals",
        description="Every ritual in Feral Familiars requires energy (essences) to complete.",
        color=discord.Color.blue()
    )
    
    # 1. Creation Costs
    ritual_text = (
        "To create a familiar, you need a Spirit and matching Essences:\n"
        "▫️ **Common:** 10 Essences\n"
        "▫️ **Uncommon:** 20 Essences\n"
        "▫️ **Rare:** 40 Essences\n"
        "▫️ **Legendary:** 80 Essences"
    )
    embed.add_field(name="✨ Familiar Creation", value=ritual_text, inline=False)
    
    # 2. Gifting (Bestow) Taxes
    bestow_text = (
        "When you bestow a gift, **YOU** pay a ritual fee:\n"
        "▫️ **Essences:** 2% of total (Min 1)\n"
        "▫️ **Common Spirit:** 1 Essence\n"
        "▫️ **Uncommon Spirit:** 3 Essences\n"
        "▫️ **Rare Spirit:** 5 Essences\n"
        "▫️ **Legendary Spirit:** 13 Essences"
    )
    embed.add_field(name="🎁 Gifting (Bestow)", value=bestow_text, inline=True)
    
    # 3. Trading (Transmute) Taxes
    transmute_text = (
        "When transmuting, **THE RECIPIENT** pays a fee:\n"
        "▫️ **Essences:** 5% of total (Min 1)\n"
        "▫️ **Common Spirit:** 2 Essences\n"
        "▫️ **Uncommon Spirit:** 5 Essences\n"
        "▫️ **Rare Spirit:** 10 Essences\n"
        "▫️ **Legendary Spirit:** 25 Essences"
    )
    embed.add_field(name="🧪 Trading (Transmute)", value=transmute_text, inline=True)
    
    embed.set_footer(text="Fees can be paid with ANY essence type of your choice.")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sync", description="Sync slash commands (Admin only)")
async def sync(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Only admins can sync.", ephemeral=True)
        return
    await bot.tree.sync()
    await interaction.response.send_message("Commands synced.")

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
    if content == "!testspawn" and message.author.guild_permissions.manage_channels:
        async with AsyncSessionLocal() as session:
            type = "spirit" if random.random() < 0.3 else "essence"
            encounter = await EncounterService.spawn_encounter(session, message.channel.id, message.guild.id, type)
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
                msg = await message.channel.send(embed=embed)
                encounter.message_id = msg.id
                await session.commit()
            else:
                await message.reply("An encounter is already active in this channel.")
        return

    if content in ["bind", "bind spirit"]:
        async with AsyncSessionLocal() as session:
            encounter, result = await EncounterService.process_capture_attempt(session, message.channel.id, message.author.id, content)
            if encounter:
                await message.reply(result)
                
                # Tiny delay to allow Discord API to settle
                import asyncio
                await asyncio.sleep(0.5)
                
                try:
                    msg = await message.channel.fetch_message(encounter.message_id)
                    
                    # Create a fresh embed to force Discord to update the image
                    new_embed = discord.Embed(
                        title=f"Captured by {message.author.display_name}!",
                        description=f"The {encounter.subtype} {encounter.type} has been bound.",
                        color=discord.Color.green()
                    )
                    
                    # Set the 'Bound' image
                    bound_url = GameConstants.BOUND_IMAGES.get(encounter.subtype)
                    new_embed.set_image(url=bound_url)
                    
                    # Re-add rarity if it was a spirit
                    if encounter.rarity:
                        new_embed.add_field(name="Rarity", value=encounter.rarity.upper())
                        
                    await msg.edit(embed=new_embed)
                except: pass
                if encounter.type == "essence":
                    passive_msg = await PassiveService.trigger_passive_bonus(session, message.author.id, encounter.subtype)
                    if passive_msg:
                        await message.channel.send(passive_msg)
            elif result and result not in ["The essence has faded...", "No active encounter in this channel."]:
                await message.reply(result, delete_after=5)

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)
