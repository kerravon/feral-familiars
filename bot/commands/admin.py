import discord
from discord.ext import commands
import random
import logging
from bot.db import AsyncSessionLocal
from bot.services.config_service import ConfigService
from bot.services.encounter_service import EncounterService
from bot.services.inventory_service import InventoryService
from bot.models.familiar import Familiar
from bot.domain.constants import GameRules as GameConstants, AssetUrls

logger = logging.getLogger("FeralFamiliars")

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        # Track activity for spawning bonus
        if message.guild:
            async with AsyncSessionLocal() as session:
                await ConfigService.increment_activity(session, message.channel.id)

    @discord.app_commands.command(name="toggle-channel", description="Enable or disable essence spawns in this channel (Requires Manage Channels).")
    async def toggle_channel(self, interaction: discord.Interaction):
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
            
            if is_active:
                from bot.services.guidance_service import GuidanceService
                embed = GuidanceService.get_onboarding_embed()
                await interaction.response.send_message(msg, embed=embed)
            else:
                await interaction.response.send_message(msg)

    @discord.app_commands.command(name="sync", description="Sync slash commands (Admin only)")
    async def sync_slash(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only admins can sync.", ephemeral=True)
            return
        await self.bot.tree.sync()
        await interaction.response.send_message("Commands synced.")

    # --- Debug Prefix Commands ---

    @commands.command(name="sync")
    @commands.has_permissions(manage_guild=True)
    async def sync_prefix(self, ctx):
        """Manual Sync for testing"""
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.reply("✅ Slash commands synced INSTANTLY to this server!")

    @commands.command(name="testspawn")
    @commands.has_permissions(manage_channels=True)
    async def test_spawn(self, ctx, target_type: str = None, target_subtype: str = None, target_rarity: str = None):
        """Manual Spawn for testing"""
        if target_subtype: target_subtype = target_subtype.title()
        if target_rarity: target_rarity = target_rarity.lower()

        async with AsyncSessionLocal() as session:
            try:
                if not target_type:
                    target_type = "spirit" if random.random() < 0.3 else "essence"
                
                encounter = await EncounterService.spawn_encounter(
                    session, ctx.channel.id, ctx.guild.id, target_type,
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

                    msg = await ctx.send(embed=embed)
                    encounter.message_id = msg.id
                    await session.commit()
                else:
                    await ctx.reply("An encounter is already active in this channel.")
            except Exception as e:
                logger.error(f"Error in !testspawn: {e}", exc_info=True)

    @commands.command(name="givefamiliar")
    @commands.has_permissions(manage_guild=True)
    async def give_familiar(self, ctx, etype: str = "Fire", rarity: str = "common", stype: str = "Feline"):
        """Manual Familiar for testing"""
        etype = etype.title()
        rarity = rarity.lower()
        stype = stype.title()

        if etype not in GameConstants.ESSENCES or rarity not in GameConstants.RARITIES:
            await ctx.reply(f"Invalid type or rarity. Types: {GameConstants.ESSENCES}, Rarities: {GameConstants.RARITIES}")
            return

        async with AsyncSessionLocal() as session:
            from bot.services.inventory_service import InventoryService
            await InventoryService.get_or_create_user(session, ctx.author.id)
            adj = random.choice(GameConstants.ESSENCE_ADJECTIVES[etype][rarity])
            noun = random.choice(GameConstants.SPIRIT_NOUNS.get(stype, GameConstants.SPIRIT_NOUNS["Feline"])[rarity])
            fname = f"DEBUG {adj} {noun}"

            new_fam = Familiar(user_id=ctx.author.id, spirit_type=stype, essence_type=etype, rarity=rarity, name=fname)
            session.add(new_fam)
            await session.commit()
            await ctx.reply(f"🎁 **Debug Gift:** You have received **{fname}**!")

    @commands.command(name="givelure")
    @commands.has_permissions(manage_guild=True)
    async def give_lure(self, ctx, ltype: str = "essence", mins: int = 30):
        """Manual Lure for testing"""
        async with AsyncSessionLocal() as session:
            user = await InventoryService.get_or_create_user(session, ctx.author.id)
            if ltype == "spirit":
                user.stored_spirit_lure_mins += mins
            elif ltype == "pure":
                user.stored_pure_lure_mins += mins
            else:
                user.stored_essence_lure_mins += mins
            await session.commit()
            await ctx.reply(f"🕯️ **Debug Lure:** Added **{mins} minutes** of {ltype} incense to your inventory.")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
