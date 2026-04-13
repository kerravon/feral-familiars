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
            embed.add_field(name="Level", value=f"**Lv. {f.level}** / 10", inline=True)
            
            # XP Progress Bar
            from bot.services.leveling_service import LevelingService
            xp_needed = LevelingService.XP_CURVE.get(f.level, 0)
            if xp_needed > 0:
                progress = (f.xp / xp_needed) * 100
                filled = int(progress / 10)
                bar = "🟦" * filled + "⬛" * (10 - filled)
                embed.add_field(name="Experience", value=f"{bar} {f.xp}/{xp_needed} XP ({progress:.1f}%)", inline=False)
            else:
                embed.add_field(name="Experience", value="🌟 **MAX LEVEL**", inline=False)

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
            
            total_chance = base_chance + (f.growth_bonus * 100)

            mode_info = {
                "echo": "**ECHO:** 2x chance for same element.",
                "pulse": "**PULSE:** Chance for a RANDOM element.",
                "attract": f"**ATTRACT:** Attracts **{f.attract_element or 'Arcane'}** essence."
            }
            mode_desc = mode_info.get(f.resonance_mode, "Unknown Mode")
            passive_desc = f"{mode_desc}\n**Trigger Chance:** {total_chance:.1f}% ({base_chance}% base + {f.growth_bonus:.1%} growth)"

            embed.add_field(name=f"Passive Power ({f.resonance_mode.upper()})", value=passive_desc, inline=False)


            view = FamiliarView(f, interaction.user.id)
            # Disable button if already active, used today, or NOT SUMMONED
            # Note: button index is 1 because select menu is index 0
            ignite_btn = view.children[1] 
            if not f.is_active:
                ignite_btn.disabled = True
                ignite_btn.label = "Summon First"
            elif f.last_activated_at and f.last_activated_at.date() == now.date():
                if not (f.active_until and now < f.active_until):
                    ignite_btn.disabled = True
                    ignite_btn.label = "Used Today"
                else:
                    ignite_btn.disabled = True
                    ignite_btn.label = "Resonating..."

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
                    
                    field_value = (
                        f"**Type:** {f.spirit_type}/{f.essence_type}\n"
                        f"**Rarity:** {f.rarity.title()}\n"
                        f"**Status:** {resonance_status}"
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
        
        # 1. Creation Costs
        ritual_text = (
            "To create a familiar, you need a Spirit and matching Essences:\n"
            "▫️ **Common:** 10 | **Uncommon:** 20\n"
            "▫️ **Rare:** 40 | **Legendary:** 80\n\n"
            "🕯️ **Restless Spirits:** Require an extra infusion of **Arcane Essence**:\n"
            "▫️ +5 (Common) to +25 (Legendary)"
        )
        embed.add_field(name="✨ Familiar Creation", value=ritual_text, inline=False)
        
        # 2. Resonance Logic
        resonance_text = (
            "Passives must be enabled via **/familiar [name]**:\n"
            "🔥 **Resonance:** Active for **4 hours** once ignited.\n"
            "⚖️ **Global Limit:** You can ignite resonance **2 times per day**.\n"
            "🔄 **Modes:** Choose between **ECHO** (Double same type) or **PULSE** (Random different element)."
        )
        embed.add_field(name="🔥 Passive Resonance", value=resonance_text, inline=False)

        # 3. Incense Logic
        incense_text = (
            "Burn stored time blocks to guarantee spawns in this channel:\n"
            "👻 **Spirit:** 100% Spirit spawns every minute.\n"
            "✨ **Essence:** 100% random Essence spawns every minute.\n"
            "💎 **Pure:** 100% spawns of a **specifically chosen** element."
        )
        embed.add_field(name="🕯️ Spectral Incense", value=incense_text, inline=False)

        # 4. Gifting & Trading Taxes
        taxes_text = (
            "Every ritual fee is paid to the **Well of Souls**:\n"
            "**Gifting (Bestow):** Sender pays 3% fee (Spirits: 2-25)\n"
            "**Trading (Transmute):** Recipient pays 3% fee (Spirits: 2-25)\n\n"
            "**XP & Leveling:**\n"
            "Feed your familiar essences via **/feed** to level them up (Max 10)!"
        )
        embed.add_field(name="🤝 Social Taxes & XP", value=taxes_text, inline=False)
        
        embed.set_footer(text="Check your /inventory to see how many Incense minutes you have stored.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
