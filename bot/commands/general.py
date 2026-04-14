import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from bot.db import AsyncSessionLocal
from bot.services.inventory_service import InventoryService
from bot.services.config_service import ConfigService
from bot.models.familiar import Familiar
from bot.models.base import User
from bot.utils.ui import FamiliarView, HelpView
from bot.ui.embeds import EmbedFactory
from bot.domain.enums import EssenceType, SpiritType, Rarity, LureType
from bot.domain.constants import GameRules

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="inventory", description="Check your mystical inventory.")
    async def inventory(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            user = await InventoryService.get_or_create_user(session, interaction.user.id)
            essences = await InventoryService.get_essences(session, interaction.user.id)
            spirits = await InventoryService.get_spirits(session, interaction.user.id)
            
            embed = discord.Embed(title=f"🎒 {interaction.user.display_name}'s Inventory", color=discord.Color.blue())
            
            ess_text = "\n".join([f"✨ {e.type.value}: **{e.count}**" for e in essences]) or "No essences."
            embed.add_field(name="Elemental Essences", value=ess_text, inline=False)
            
            spirit_text = "\n".join([f"👻 {s.rarity.value.title()} {s.type.value} (ID: {s.id})" for s in spirits]) or "No spirits."
            embed.add_field(name="Captured Spirits", value=spirit_text, inline=False)
            
            lure_text = (
                f"🕯️ Essence Incense: {user.stored_essence_lure_mins}m\n"
                f"🕯️ Spirit Incense: {user.stored_spirit_lure_mins}m\n"
                f"🕯️ Pure Incense: {user.stored_pure_lure_mins}m"
            )
            embed.add_field(name="Spectral Incense", value=lure_text, inline=False)
            
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="familiars", description="View your stable of familiars.")
    async def familiars(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            fams = await InventoryService.get_familiars(session, interaction.user.id)
            
            embed = discord.Embed(title="🐾 Your Familiar Stable", color=discord.Color.gold())
            now = datetime.now()

            if not fams:
                embed.description = "No familiars yet. Perform a /ritual to create one!"
            else:
                for f in fams:
                    status_icon = "🟢 [SUMMONED]" if f.is_active else "⚪"
                    resonance_status = "💤 Inactive"
                    if f.active_until and now < f.active_until:
                        delta = f.active_until - now
                        mins = int(delta.total_seconds() / 60)
                        resonance_status = f"🔥 RESONATING ({mins}m left)"
                    
                    field_value = (
                        f"**Type:** {f.spirit_type.value}/{f.essence_type.value}\n"
                        f"**Rarity:** {f.rarity.value.title()}\n"
                        f"**Level:** {f.level}\n"
                        f"**Status:** {resonance_status}"
                    )
                    
                    embed.add_field(name=f"{status_icon} {f.name} (ID: {f.id})", value=field_value, inline=False)
            
            embed.set_footer(text="Use /summon [id] to swap active familiars. Use /familiar [id] to ignite resonance.")
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="familiar", description="View detailed stats and manage a specific familiar.")
    async def familiar_details(self, interaction: discord.Interaction, familiar_id: int):
        async with AsyncSessionLocal() as session:
            stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == interaction.user.id)
            result = await session.execute(stmt)
            f = result.scalar_one_or_none()
            
            if not f:
                await interaction.response.send_message("Familiar not found.", ephemeral=True)
                return

            embed = EmbedFactory.create_familiar_card(f, datetime.now())
            view = FamiliarView(f, interaction.user.id)
            
            # Button logic
            ignite_btn = view.children[1] 
            if not f.is_active:
                ignite_btn.disabled = True
                ignite_btn.label = "Summon First"
            elif f.last_activated_at and f.last_activated_at.date() == datetime.now().date():
                if not (f.active_until and datetime.now() < f.active_until):
                    ignite_btn.disabled = True
                    ignite_btn.label = "Used Today"
                else:
                    ignite_btn.disabled = True
                    ignite_btn.label = "Resonating..."

            await interaction.response.send_message(embed=embed, view=view)

    @discord.app_commands.command(name="help", description="Get guidance on how to play Feral Familiars.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 The Mystic's Archive",
            description="Choose a category below to learn about the secrets of the world.",
            color=discord.Color.blue()
        )
        view = HelpView()
        await interaction.response.send_message(embed=embed, view=view)

    @discord.app_commands.command(name="incense", description="Ignite spectral incense to guarantee spawns in this channel for a set time.")
    async def incense(self, interaction: discord.Interaction, lure_type: str, minutes: int, element: Optional[str] = None):
        try:
            l_type = LureType(lure_type.lower())
        except ValueError:
            await interaction.response.send_message("Invalid incense type.", ephemeral=True)
            return

        e_type = None
        if element:
            try:
                e_type = EssenceType(element.title())
            except ValueError:
                await interaction.response.send_message("Invalid element type.", ephemeral=True)
                return

        async with AsyncSessionLocal() as session:
            user = await InventoryService.get_or_create_user(session, interaction.user.id)
            
            # Check storage
            storage_attr = f"stored_{l_type.value}_lure_mins"
            available = getattr(user, storage_attr, 0)
            
            if available < minutes:
                await interaction.response.send_message(f"You only have {available}m of {l_type.value} incense.", ephemeral=True)
                return
            
            success, result = await ConfigService.ignite_lure(session, interaction.user.id, interaction.channel_id, l_type, minutes, e_type)
            if success:
                setattr(user, storage_attr, available - minutes)
                await session.commit()
                await interaction.response.send_message(f"🔥 {result}")
            else:
                await interaction.response.send_message(f"❌ {result}", ephemeral=True)

    @discord.app_commands.command(name="ritual-guide", description="View the standard ritual costs and rules.")
    async def ritual_guide(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📜 The Mystic's Guide to Rituals", color=discord.Color.purple())
        
        ritual_text = (
            "**Standard Ritual:** 1 Spirit + Matching Essences = 1 Familiar\n"
            "**Restless Ritual:** Requires additional Arcane Essence (+5 to +25).\n\n"
            "**Costs by Rarity:**\n"
            "▫️ Common: 10 Essences\n"
            "▫️ Uncommon: 20 Essences\n"
            "▫️ Rare: 40 Essences\n"
            "▫️ Legendary: 80 Essences"
        )
        embed.add_field(name="✨ Ritual Costs", value=ritual_text, inline=False)
        
        incense_text = (
            "**Essence Incense:** Guaranteed Essence spawns every 60s.\n"
            "**Spirit Incense:** Guaranteed Spirit spawns every 60s.\n"
            "**Pure Incense:** Guaranteed specific element every 60s."
        )
        embed.add_field(name="🕯️ Spectral Incense", value=incense_text, inline=False)
        
        taxes_text = (
            "Every ritual fee is paid to the **Well of Souls**:\n"
            "**Gifting (Bestow):** Sender pays 3% fee (Spirits: 2-25)\n"
            "**Trading (Transmute):** Recipient pays 3% fee (Spirits: 2-25)\n\n"
            "**XP & Leveling:**\n"
            "Feed your familiar essences via **/feed** to level them up (Max 10)!"
        )
        embed.add_field(name="🤝 Social Taxes & XP", value=taxes_text, inline=False)
        
        embed.set_footer(text="Check your /inventory to see your stored items.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
