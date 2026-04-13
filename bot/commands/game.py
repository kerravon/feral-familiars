import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy import update, select
import asyncio
import logging
import random

from bot.db import AsyncSessionLocal
from bot.services.ritual_service import RitualService
from bot.services.passive_service import PassiveService
from bot.services.inventory_service import InventoryService
from bot.services.surge_service import SurgeService
from bot.services.encounter_service import EncounterService
from bot.services.leveling_service import LevelingService
from bot.services.guidance_service import GuidanceService
from bot.models.familiar import Familiar, Spirit
from bot.utils.constants import GameConstants
from bot.utils.config import Config

logger = logging.getLogger("FeralFamiliars")

class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        
        content = message.content.lower().strip()
        if content not in ["bind", "bind spirit"]: return

        logger.info(f"Capture attempt by {message.author.name}: {content}")
        async with AsyncSessionLocal() as session:
            encounter, result = await EncounterService.process_capture_attempt(session, message.channel.id, message.author.id, content)
            
            if encounter:
                await message.reply(result)
                logger.info(f"Capture SUCCESS: {message.author.name} bound {encounter.subtype}")
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
                
                # --- Award XP to summoned familiar ---
                active_fam = await PassiveService.get_active_familiar(session, message.author.id)
                if active_fam:
                    xp_amount = 10 if (encounter.type == "essence" and encounter.subtype == active_fam.essence_type) else 5
                    level_ups = await LevelingService.add_xp(session, active_fam, xp_amount)
                    
                    for level_up in level_ups:
                        lvl = level_up['level']
                        roll = level_up['roll']
                        unlocks = "\n".join([f"✨ **Unlocked:** {u}" for u in level_up['unlocks']])
                        
                        embed = discord.Embed(
                            title=f"🌟 LEVEL UP: {active_fam.name}!",
                            description=f"Your familiar has reached **Level {lvl}**!\n\n"
                                        f"📈 **Growth Roll:** +{roll:.2%}\n"
                                        f"{unlocks}",
                            color=discord.Color.gold()
                        )
                        await message.channel.send(content=f"<@{message.author.id}>", embed=embed)

                # --- Guidance Milestone Check ---
                tip_embed = await GuidanceService.check_milestone(session, message.author.id, encounter.type)
                if tip_embed:
                    await message.channel.send(content=f"<@{message.author.id}>", embed=tip_embed)
            else:
                if result:
                    await message.reply(result, delete_after=5)
                    logger.info(f"Capture FAILED for {message.author.name}: {result}")

    async def spirit_autocomplete(self, interaction: discord.Interaction, current: str):
        async with AsyncSessionLocal() as session:
            spirits = await InventoryService.get_spirits(session, interaction.user.id)
            choices = [
                app_commands.Choice(name=f"{s.rarity.title()} {s.type} (ID: {s.id})", value=s.id)
                for s in spirits if current.lower() in f"{s.rarity} {s.type}".lower()
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
            app_commands.Choice(name=e, value=e)
            for e in GameConstants.ESSENCES if current.lower() in e.lower()
        ]
        return choices[:25]

    @app_commands.command(name="ritual", description="Combine a spirit and essences to create a familiar.")
    @app_commands.autocomplete(spirit_id=spirit_autocomplete)
    async def ritual(self, interaction: discord.Interaction, spirit_id: int, essence_type: str):
        essence_type = essence_type.title()
        if essence_type not in GameConstants.ESSENCES:
            await interaction.response.send_message(f"Invalid essence type. Choose from: {', '.join(GameConstants.ESSENCES)}", ephemeral=True)
            return
        async with AsyncSessionLocal() as session:
            success, result = await RitualService.create_familiar(session, interaction.user.id, spirit_id, essence_type)
            if success:
                familiar, tip_embed = result
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
                await interaction.response.send_message(f"✨ **{result.name}** has manifested by your side!")
            else:
                await interaction.response.send_message(f"❌ **Summon Failed:** {result}", ephemeral=True)

    @app_commands.command(name="release-spirit", description="Release a spirit from your inventory back into the wild.")
    @app_commands.autocomplete(spirit_id=spirit_autocomplete)
    async def release_spirit(self, interaction: discord.Interaction, spirit_id: int):
        async with AsyncSessionLocal() as session:
            # First fetch to show info
            stmt = select(Spirit).where(Spirit.id == spirit_id, Spirit.user_id == interaction.user.id)
            result = await session.execute(stmt)
            spirit = result.scalar_one_or_none()
            
            if not spirit:
                await interaction.response.send_message("Spirit not found in your inventory.", ephemeral=True)
                return

            stype, srarity = spirit.type, spirit.rarity
            
            success = await InventoryService.delete_spirit(session, interaction.user.id, spirit_id)
            if success:
                await interaction.response.send_message(f"🍃 You have released the **{srarity.title()} {stype} spirit** back into the ether. Its energy lingers in the air...")
                asyncio.create_task(SurgeService.trigger_spirit_surge(
                    self.bot, interaction.channel_id, interaction.guild_id, interaction.user.id, stype, srarity
                ))
            else:
                await interaction.response.send_message("❌ Failed to release spirit.", ephemeral=True)

    @app_commands.command(name="release-familiar", description="Release a familiar from your stable. This is permanent!")
    @app_commands.autocomplete(familiar_id=familiar_autocomplete)
    async def release_familiar(self, interaction: discord.Interaction, familiar_id: int):
        async with AsyncSessionLocal() as session:
            stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == interaction.user.id)
            res = await session.execute(stmt)
            f = res.scalar_one_or_none()
            if not f:
                await interaction.response.send_message("Familiar not found.", ephemeral=True)
                return
            
            fname, stype, srarity, etype = f.name, f.spirit_type, f.rarity, f.essence_type

            success, result = await RitualService.delete_familiar(session, interaction.user.id, familiar_id)
            if success:
                await interaction.response.send_message(f"🕊️ **{fname}** has been released from your stable. Its resonance shatters, scattering energy across the server!")
                asyncio.create_task(SurgeService.trigger_familiar_surge(
                    self.bot, interaction.channel_id, interaction.guild_id, interaction.user.id, stype, srarity, etype
                ))
            else:
                await interaction.response.send_message(f"❌ **Release Failed:** {result}", ephemeral=True)

    @app_commands.command(name="donate", description="Voluntarily contribute essences to the Well of Souls (Guild Pot).")
    @app_commands.autocomplete(essence_type=essence_autocomplete)
    async def donate(self, interaction: discord.Interaction, essence_type: str, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Donation must be a positive amount.", ephemeral=True)
            return

        essence_type = essence_type.title()
        if essence_type not in GameConstants.ESSENCES:
            await interaction.response.send_message(f"Invalid essence type. Choose from: {', '.join(GameConstants.ESSENCES)}", ephemeral=True)
            return

        from bot.services.guild_service import GuildService
        async with AsyncSessionLocal() as session:
            success = await InventoryService.deduct_essence(session, interaction.user.id, essence_type, amount)
            if not success:
                await interaction.response.send_message(f"You do not have {amount}x {essence_type} essences.", ephemeral=True)
                return

            await GuildService.add_to_pot(session, interaction.guild_id, self.bot, interaction.channel_id, essence_amount=amount)
            await interaction.response.send_message(f"🌟 **Offering Accepted!** You donated **{amount}x {essence_type}** to the Well of Souls. The resonance grows stronger...")

    @app_commands.command(name="vault", description="Check the status of the Well of Souls (Guild Pot).")
    async def vault(self, interaction: discord.Interaction):
        from bot.services.guild_service import GuildService
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
            
            # Progress bar
            filled = int(progress / 10)
            bar = "🟦" * filled + "⬛" * (10 - filled)
            embed.add_field(name="Overflow Progress", value=f"{bar} ({progress:.1f}%)", inline=False)
            
            embed.set_footer(text="Gifting and Trading adds to the Well. Voluntary contributions coming soon!")
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="feed", description="Feed essences to your active familiar to gain XP.")
    @app_commands.describe(
        essence_type="Type of essence to feed",
        amount="How many essences to feed"
    )
    @app_commands.autocomplete(essence_type=essence_autocomplete)
    async def feed(self, interaction: discord.Interaction, essence_type: str, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You must feed at least 1 essence.", ephemeral=True)
            return

        essence_type = essence_type.title()
        async with AsyncSessionLocal() as session:
            # 1. Get active familiar
            active_fam = await PassiveService.get_active_familiar(session, interaction.user.id)
            if not active_fam:
                await interaction.response.send_message("You must have a familiar **summoned** to feed it!", ephemeral=True)
                return
            
            if active_fam.level >= 10:
                await interaction.response.send_message(f"**{active_fam.name}** is already at maximum level!", ephemeral=True)
                return

            # 2. Deduct Essence
            success = await InventoryService.deduct_essence(session, interaction.user.id, essence_type, amount)
            if not success:
                await interaction.response.send_message(f"You don't have {amount}x {essence_type} essences.", ephemeral=True)
                return

            # 3. Calculate XP
            # Matching: 10, Arcane: 20, Other: 2
            multiplier = 2
            if essence_type == active_fam.essence_type:
                multiplier = 10
            elif essence_type == GameConstants.ARCANE:
                multiplier = 20
            
            xp_gain = amount * multiplier
            
            # 4. Add XP
            from bot.services.leveling_service import LevelingService
            level_ups = await LevelingService.add_xp(session, active_fam, xp_gain)
            
            # 5. Feedback
            await interaction.response.send_message(f"✨ You fed **{amount}x {essence_type}** to **{active_fam.name}**, gaining **{xp_gain} XP**!")
            
            for level_up in level_ups:
                lvl = level_up['level']
                roll = level_up['roll']
                unlocks = "\n".join([f"✨ **Unlocked:** {u}" for u in level_up['unlocks']])
                
                embed = discord.Embed(
                    title=f"🌟 LEVEL UP: {active_fam.name}!",
                    description=f"Your familiar has reached **Level {lvl}**!\n\n"
                                f"📈 **Growth Roll:** +{roll:.2%}\n"
                                f"{unlocks}",
                    color=discord.Color.gold()
                )
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="set-attract", description="Choose which element your Level 8+ familiar attracts.")
    @app_commands.describe(element="The element to attract during resonance")
    @app_commands.autocomplete(element=essence_autocomplete)
    async def set_attract(self, interaction: discord.Interaction, element: str):
        async with AsyncSessionLocal() as session:
            active_fam = await PassiveService.get_active_familiar(session, interaction.user.id)
            if not active_fam or active_fam.level < 8:
                await interaction.response.send_message("Only Level 8+ summoned familiars can use ATTRACT mode.", ephemeral=True)
                return
            
            success, result = await PassiveService.set_attract_element(session, interaction.user.id, active_fam.id, element)
            if success:
                await interaction.response.send_message(f"🎯 **{active_fam.name}** is now focused on attracting **{element.title()}** essences!")
            else:
                await interaction.response.send_message(f"❌ Failed: {result}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GameCog(bot))
