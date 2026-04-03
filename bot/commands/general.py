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
from bot.utils.ui import FamiliarView

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def familiar_autocomplete(self, interaction: discord.Interaction, current: str):
        async with AsyncSessionLocal() as session:
            familiars = await InventoryService.get_familiars(session, interaction.user.id)
            choices = [
                discord.app_commands.Choice(name=f"{f.name} (ID: {f.id})", value=f.id)
                for f in familiars if current.lower() in f.name.lower()
            ]
            return choices[:25]

    @discord.app_commands.command(name="familiar", description="View detailed info about a familiar and activate its resonance.")
    @discord.app_commands.autocomplete(familiar_id=familiar_autocomplete)
    async def familiar_info(self, interaction: discord.Interaction, familiar_id: int):
        async with AsyncSessionLocal() as session:
            stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == interaction.user.id)
            res = await session.execute(stmt)
            f = res.scalar_one_or_none()

            if not f:
                await interaction.response.send_message("Familiar not found.", ephemeral=True)
                return

            embed = discord.Embed(title=f"🐾 {f.name}", color=discord.Color.gold())
            embed.add_field(name="Type", value=f"{f.spirit_type} / {f.essence_type}", inline=True)
            embed.add_field(name="Rarity", value=f.rarity.title(), inline=True)
            
            now = datetime.now()
            status = "💤 Inactive"
            if f.active_until and now < f.active_until:
                delta = f.active_until - now
                mins = int(delta.total_seconds() / 60)
                status = f"🔥 RESONATING ({mins}m left)"
            embed.add_field(name="Resonance Status", value=status, inline=False)

            # Passive Description
            chance_map = {"common": 8, "uncommon": 15, "rare": 25, "legendary": 40}
            base_chance = chance_map.get(f.rarity, 8)
            if f.essence_type == "Arcane": base_chance += 10

            mode_desc = "**ECHO:** 2x chance for same element." if f.resonance_mode == "echo" else "**PULSE:** Chance for a RANDOM element."
            passive_desc = f"{mode_desc}\n**Trigger Chance:** {base_chance}%"

            embed.add_field(name=f"Passive Power ({f.resonance_mode.upper()})", value=passive_desc, inline=False)


            view = FamiliarView(f.id, interaction.user.id)
            # Disable button if already active, used today, or NOT SUMMONED
            if not f.is_active:
                view.children[0].disabled = True
                view.children[0].label = "Summon First"
            elif f.last_activated_at and f.last_activated_at.date() == now.date():
                if not (f.active_until and now < f.active_until):
                    view.children[0].disabled = True
                    view.children[0].label = "Used Today"
                else:
                    view.children[0].disabled = True
                    view.children[0].label = "Resonating..."

            await interaction.response.send_message(embed=embed, view=view)

    @discord.app_commands.command(name="incense", description="Ignite spectral incense to guarantee spawns in this channel for a set time.")
    @discord.app_commands.describe(
        lure_type="The type of energy to attract (Spirit, Essence, or Targeted)",
        minutes="How many minutes to burn (must have stored time)",
        element="If using Pure Incense, which element to attract?"
    )
    @discord.app_commands.choices(lure_type=[
        discord.app_commands.Choice(name="Spirit Incense", value="spirit"),
        discord.app_commands.Choice(name="Essence Incense", value="essence"),
        discord.app_commands.Choice(name="Pure Incense (Targeted)", value="pure")
    ])
    @discord.app_commands.choices(element=[
        discord.app_commands.Choice(name=e, value=e) for e in ["Earth", "Wind", "Fire", "Arcane", "Water"]
    ])
    async def incense(self, interaction: discord.Interaction, lure_type: str, minutes: int, element: Optional[str] = None):
        if minutes <= 0:
            await interaction.response.send_message("Minutes must be a positive number.", ephemeral=True)
            return
        
        if lure_type == "pure" and not element:
            await interaction.response.send_message("Pure Incense requires you to choose an **element**.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            success, msg = await ConfigService.activate_lure(session, interaction.user.id, interaction.channel_id, lure_type, minutes, subtype=element)
            if success:
                target_text = f"**{element}** " if element else ""
                embed = discord.Embed(
                    title="🕯️ Incense Ignited!",
                    description=f"{interaction.user.mention} has lit **{lure_type.title()} Incense**!\n{target_text}Spawns are now **GUARANTEED** in this channel for the next **{minutes} minutes**.",
                    color=discord.Color.gold()
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ {msg}", ephemeral=True)

    @discord.app_commands.command(name="inventory", description="View your essences and spirits or those of another user.")
    async def inventory(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        target_user = user or interaction.user
        
        async with AsyncSessionLocal() as session:
            await InventoryService.get_or_create_user(session, target_user.id)
            stmt = select(User).where(User.id == target_user.id)
            res = await session.execute(stmt)
            db_user = res.scalar_one()

            essences = await InventoryService.get_essences(session, target_user.id)
            spirits = await InventoryService.get_spirits(session, target_user.id)
            
            embed = discord.Embed(title=f"🎒 {target_user.name}'s Inventory", color=discord.Color.green())
            
            e_text = "\n".join([f"{e.type}: {e.count}" for e in essences]) or "No essences."
            embed.add_field(name="Essences", value=e_text, inline=True)
            
            s_text = "\n".join([f"ID: {s.id} - {s.rarity.title()} {s.type}" for s in spirits]) or "No spirits."
            embed.add_field(name="Spirits (Max 5)", value=s_text, inline=True)

            l_text = f"✨ **Essence Incense:** {db_user.stored_essence_lure_mins} mins\n"
            l_text += f"👻 **Spirit Incense:** {db_user.stored_spirit_lure_mins} mins\n"
            l_text += f"💎 **Pure Incense:** {db_user.stored_pure_lure_mins} mins"
            embed.add_field(name="Stored Incense", value=l_text, inline=False)
            
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="familiars", description="View your collection of familiars in the stable.")
    async def familiars(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            fams = await InventoryService.get_familiars(session, interaction.user.id)
            embed = discord.Embed(title=f"🏰 {interaction.user.name}'s Stable", color=discord.Color.gold())
            
            if not fams:
                embed.description = "No familiars yet. Perform a /ritual to create one!"
            else:
                now = datetime.now()
                for f in fams:
                    status_icon = "🟢 [SUMMONED]" if f.is_active else "⚪"
                    resonance_status = "💤 Inactive"
                    if f.active_until and now < f.active_until:
                        delta = f.active_until - now
                        mins = int(delta.total_seconds() / 60)
                        resonance_status = f"🔥 RESONATING ({mins}m left)"
                    
                    limit_map = {"common": 20, "uncommon": 25, "rare": 30, "legendary": 40}
                    max_trig = limit_map.get(f.rarity, 20)
                    triggers = f"{f.daily_trigger_count}/{max_trig} used"

                    field_value = (
                        f"**Type:** {f.spirit_type}/{f.essence_type}\n"
                        f"**Rarity:** {f.rarity.title()}\n"
                        f"**Status:** {resonance_status}\n"
                        f"**Passives:** {triggers}"
                    )
                    
                    embed.add_field(name=f"{status_icon} {f.name} (ID: {f.id})", value=field_value, inline=False)
            
            embed.set_footer(text="Use /summon [id] to swap active familiars. Use /familiar [id] to ignite resonance.")
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="ritual-guide", description="View the guide for familiar creation, gifting, and taxes.")
    async def ritual_guide(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 The Mystic's Guide to Rituals",
            description="Every ritual in Feral Familiars requires energy (essences) to complete.",
            color=discord.Color.blue()
        )
        
        ritual_text = (
            "To create a familiar, you need a Spirit and matching Essences:\n"
            "▫️ **Common:** 10 | **Uncommon:** 20\n"
            "▫️ **Rare:** 40 | **Legendary:** 80\n\n"
            "🕯️ **Restless Spirits:** Require an extra infusion of **Arcane Essence**:\n"
            "▫️ +5 (Common) to +25 (Legendary)"
        )
        embed.add_field(name="✨ Familiar Creation", value=ritual_text, inline=False)
        
        resonance_text = (
            "Passives must be manually enabled using **/familiar [name]**:\n"
            "🔥 **Resonance:** Active for **2 hours** once per day.\n"
            "✨ **Arcane:** Doubles ANY essence + Server Timer Bonus.\n"
            "💀 **Restless:** % Chance to 'Anchor' fading spirits for the server."
        )
        embed.add_field(name="🔥 Passive Resonance", value=resonance_text, inline=False)

        bestow_text = (
            "When you bestow a gift, **YOU** pay a ritual fee:\n"
            "▫️ **Essences:** 2% (Min 1)\n"
            "▫️ **Spirits:** 1-13 based on rarity"
        )
        embed.add_field(name="🎁 Gifting", value=bestow_text, inline=True)
        
        transmute_text = (
            "When transmuting, **THE RECIPIENT** pays a fee:\n"
            "▫️ **Essences:** 5% (Min 1)\n"
            "▫️ **Spirits:** 2-25 based on rarity"
        )
        embed.add_field(name="🧪 Trading", value=transmute_text, inline=True)
        
        embed.set_footer(text="Fees can be paid with ANY essence type of your choice.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
