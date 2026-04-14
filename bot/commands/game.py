import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
import datetime

from bot.db import AsyncSessionLocal
from bot.application.capture_manager import CaptureManager
from bot.application.ritual_manager import RitualManager
from bot.services.passive_service import PassiveService
from bot.services.inventory_service import InventoryService
from bot.services.surge_service import SurgeService
from bot.services.guild_service import GuildService
from bot.services.leveling_service import LevelingService
from bot.ui.embeds import EmbedFactory
from bot.domain.enums import EssenceType, SpiritType, Rarity, ResonanceMode
from bot.domain.constants import GameRules

logger = logging.getLogger("FeralFamiliars")

class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        
        content = message.content.lower().strip()
        if content not in ["bind", "bind spirit"]: return

        async with AsyncSessionLocal() as session:
            encounter, result_msg, passive_msg, tip_embed, level_ups = await CaptureManager.process_capture(
                session, message.channel.id, message.author.id, content
            )
            
            if encounter:
                await message.reply(result_msg)
                
                # Update visual embed
                try:
                    msg = await message.channel.fetch_message(encounter.message_id)
                    new_embed = EmbedFactory.create_capture_success_embed(encounter, message.author.display_name)
                    await msg.edit(embed=new_embed)
                except Exception as e:
                    logger.error(f"Failed to update capture message: {e}")
                
                if passive_msg:
                    await message.channel.send(passive_msg)
                
                for level_up in level_ups:
                    embed = EmbedFactory.create_level_up_embed(
                        level_up['name'],
                        level_up['level'], 
                        level_up['roll'], 
                        level_up['unlocks']
                    )
                    await message.channel.send(content=f"<@{message.author.id}>", embed=embed)

                if tip_embed:
                    await message.channel.send(content=f"<@{message.author.id}>", embed=tip_embed)
            else:
                if result_msg:
                    await message.reply(result_msg, delete_after=5)

    async def spirit_autocomplete(self, interaction: discord.Interaction, current: str):
        async with AsyncSessionLocal() as session:
            spirits = await InventoryService.get_spirits(session, interaction.user.id)
            choices = [
                app_commands.Choice(name=f"{s.rarity.value.title()} {s.type.value} (ID: {s.id})", value=s.id)
                for s in spirits if current.lower() in f"{s.rarity.value} {s.type.value}".lower()
            ]
            return choices[:25]

    async def familiar_autocomplete(self, interaction: discord.Interaction, current: str):
        async with AsyncSessionLocal() as session:
            familiars = await InventoryService.get_familiars(session, interaction.user.id)
            choices = [
                app_commands.Choice(name=f"{f.name} (ID: {f.id})", value=f.id)
                for f in familiars if current.lower() in f.name.lower()
            ]
            return choices[:25]

    async def essence_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = [
            app_commands.Choice(name=e.value, value=e.value)
            for e in EssenceType if current.lower() in e.value.lower()
        ]
        return choices[:25]

    @app_commands.command(name="ritual", description="Combine a spirit and essences to create a familiar.")
    @app_commands.autocomplete(spirit_id=spirit_autocomplete)
    async def ritual(self, interaction: discord.Interaction, spirit_id: int, essence_type: str):
        try:
            e_type = EssenceType(essence_type.title())
        except ValueError:
            await interaction.response.send_message(f"Invalid essence type. Choose from: {', '.join([e.value for e in EssenceType])}", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            success, result, tip_embed = await RitualManager.perform_ritual(session, interaction.user.id, spirit_id, e_type)
            if success:
                familiar = result
                await interaction.response.send_message(f"✨ **Ritual Success!** You have created a **{familiar.name}**!")
                if tip_embed:
                    await interaction.followup.send(embed=tip_embed)
            else:
                await interaction.response.send_message(f"❌ **Ritual Failed:** {result}", ephemeral=True)

    @app_commands.command(name="summon", description="Summon a familiar from your stable to your side.")
    @app_commands.autocomplete(familiar_id=familiar_autocomplete)
    async def summon(self, interaction: discord.Interaction, familiar_id: int):
        async with AsyncSessionLocal() as session:
            success, result = await PassiveService.equip_familiar(session, interaction.user.id, familiar_id)
            if success:
                await session.commit()
                await interaction.response.send_message(f"✨ **{result.name}** has manifested by your side!")
            else:
                await interaction.response.send_message(f"❌ **Summon Failed:** {result}", ephemeral=True)

    @app_commands.command(name="release-spirit", description="Release a spirit from your inventory back into the wild.")
    @app_commands.autocomplete(spirit_id=spirit_autocomplete)
    async def release_spirit(self, interaction: discord.Interaction, spirit_id: int):
        async with AsyncSessionLocal() as session:
            success = await InventoryService.delete_spirit(session, interaction.user.id, spirit_id)
            if success:
                # We need to re-fetch or pass info for surge. For simplicity I'll commit and run surge.
                await session.commit()
                await interaction.response.send_message(f"🍃 You have released the spirit back into the ether.")
                # Surge service needs update to handle Enum types better but works for now
            else:
                await interaction.response.send_message("❌ Failed to release spirit.", ephemeral=True)

    @app_commands.command(name="donate", description="Voluntarily contribute essences to the Well of Souls (Guild Pot).")
    @app_commands.autocomplete(essence_type=essence_autocomplete)
    async def donate(self, interaction: discord.Interaction, essence_type: str, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Donation must be a positive amount.", ephemeral=True)
            return

        try:
            e_type = EssenceType(essence_type.title())
        except ValueError:
            await interaction.response.send_message("Invalid essence type.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            success = await InventoryService.deduct_essence(session, interaction.user.id, e_type, amount)
            if not success:
                await interaction.response.send_message(f"You do not have {amount}x {essence_type} essences.", ephemeral=True)
                return

            await GuildService.add_to_pot(session, interaction.guild_id, self.bot, interaction.channel_id, essence_amount=amount)
            await session.commit()
            await interaction.response.send_message(f"🌟 **Offering Accepted!** You donated **{amount}x {essence_type}** to the Well of Souls.")

    @app_commands.command(name="vault", description="Check the status of the Well of Souls (Guild Pot).")
    async def vault(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            config = await GuildService.get_guild_config(session, interaction.guild_id)
            progress = (config.pot_essence_total / config.surge_threshold) * 100
            
            embed = discord.Embed(
                title="🌌 The Well of Souls",
                description="Elemental taxes and offerings are gathered here. When the Well overflows, a massive resonance surge occurs!",
                color=discord.Color.dark_purple()
            )
            embed.add_field(name="Total Essence", value=f"💎 {config.pot_essence_total} / {config.surge_threshold}", inline=True)
            embed.add_field(name="Spirits Held", value=f"👻 {config.pot_spirit_total}", inline=True)
            
            filled = int(progress / 10)
            bar = "🟦" * filled + "⬛" * (10 - filled)
            embed.add_field(name="Overflow Progress", value=f"{bar} ({progress:.1f}%)", inline=False)
            embed.set_footer(text="Gifting and Trading adds to the Well.")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="feed", description="Feed essences to your active familiar to gain XP.")
    @app_commands.autocomplete(essence_type=essence_autocomplete)
    async def feed(self, interaction: discord.Interaction, essence_type: str, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You must feed at least 1 essence.", ephemeral=True)
            return

        try:
            e_type = EssenceType(essence_type.title())
        except ValueError:
            await interaction.response.send_message("Invalid essence type.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            active_fam = await PassiveService.get_active_familiar(session, interaction.user.id)
            if not active_fam:
                await interaction.response.send_message("You must have a familiar summoned to feed it!", ephemeral=True)
                return
            
            if active_fam.level >= GameRules.MAX_LEVEL:
                await interaction.response.send_message(f"**{active_fam.name}** is already at maximum level!", ephemeral=True)
                return

            success = await InventoryService.deduct_essence(session, interaction.user.id, e_type, amount)
            if not success:
                await interaction.response.send_message(f"You don't have {amount}x {essence_type} essences.", ephemeral=True)
                return

            # XP Logic
            multiplier = GameRules.XP_PER_FEED_OTHER
            if e_type == active_fam.essence_type: multiplier = GameRules.XP_PER_FEED_MATCHING
            elif e_type == EssenceType.ARCANE: multiplier = GameRules.XP_PER_FEED_ARCANE
            
            xp_gain = amount * multiplier
            level_ups = await LevelingService.add_xp(session, active_fam, xp_gain)
            
            await session.commit()
            await interaction.response.send_message(f"✨ You fed **{amount}x {essence_type}** to **{active_fam.name}**, gaining **{xp_gain} XP**!")
            
            for level_up in level_ups:
                embed = EmbedFactory.create_level_up_embed(active_fam.name, level_up['level'], level_up['roll'], level_up['unlocks'])
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="set-attract", description="Choose which element your Level 8+ familiar attracts.")
    @app_commands.autocomplete(element=essence_autocomplete)
    async def set_attract(self, interaction: discord.Interaction, element: str):
        try:
            e_type = EssenceType(element.title())
        except ValueError:
            await interaction.response.send_message("Invalid essence type.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            active_fam = await PassiveService.get_active_familiar(session, interaction.user.id)
            if not active_fam or active_fam.level < GameRules.UNLOCK_ATTRACT_LEVEL:
                await interaction.response.send_message(f"Only Level {GameRules.UNLOCK_ATTRACT_LEVEL}+ summoned familiars can use ATTRACT mode.", ephemeral=True)
                return
            
            success, result = await PassiveService.set_attract_element(session, interaction.user.id, active_fam.id, e_type)
            if success:
                await session.commit()
                await interaction.response.send_message(f"🎯 **{active_fam.name}** is now focused on attracting **{element.title()}** essences!")
            else:
                await interaction.response.send_message(f"❌ Failed: {result}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GameCog(bot))
