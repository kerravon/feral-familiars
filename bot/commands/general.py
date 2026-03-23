import discord
from discord.ext import commands
from typing import Optional
from bot.db import AsyncSessionLocal
from bot.services.inventory_service import InventoryService

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="inventory", description="View your essences and spirits or those of another user.")
    async def inventory(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
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

    @discord.app_commands.command(name="familiars", description="View your familiars in the stable.")
    async def familiars(self, interaction: discord.Interaction):
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

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
