import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.db import AsyncSessionLocal
from bot.services.transmute_service import TransmuteService
from bot.services.bestow_service import BestowService
from bot.utils.ui import TransmuteView
from bot.utils.constants import GameConstants

class TradeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="transmute", description="Start a ritual of transmutation (trade) with another player (5% Ritual Fee).")
    async def transmute(self, interaction: discord.Interaction, user: discord.User):
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

    @app_commands.command(name="bestow", description="Gift essences or spirits to another player (YOU pay the Ritual Fee).")
    @app_commands.describe(
        user="The player you are gifting to",
        essence_type="Type of essence to gift (Optional)",
        amount="Amount of essences to gift (Optional)",
        spirit_id="ID of the spirit to gift (Optional)",
        tax_payment="Essence YOU pay (Fee: 2% for essences | 1-12 for spirits based on rarity)"
    )
    async def bestow(
        self,
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

async def setup(bot):
    await bot.add_cog(TradeCog(bot))
