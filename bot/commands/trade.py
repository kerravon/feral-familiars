import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.db import AsyncSessionLocal
from bot.services.transmute_service import TransmuteService
from bot.services.bestow_service import BestowService
from bot.utils.ui import TransmuteView
from bot.domain.enums import EssenceType

class TradeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="transmute", description="Initiate a Ritual of Transmutation (Trade) with another player.")
    @app_commands.describe(user="The player you want to trade with")
    async def transmute(self, interaction: discord.Interaction, user: discord.User):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot transmute with yourself!", ephemeral=True)
            return
        if user.bot:
            await interaction.response.send_message("You cannot transmute with a bot!", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            trade = await TransmuteService.create_trade(session, interaction.user.id, user.id)
            await session.commit()
            view = TransmuteView(trade.id, interaction.user.id, user.id, bot=self.bot)
            
            embed = discord.Embed(
                title="✨ Ritual of Transmutation",
                description=f"<@{interaction.user.id}> has initiated a ritual with <@{user.id}>.",
                color=discord.Color.purple()
            )
            embed.set_footer(text="Click 'Offer' to add items. Both must 'Confirm' to complete.")

            await interaction.response.send_message(
                f"<@{user.id}>, <@{interaction.user.id}> wants to trade!",
                embed=embed,
                view=view
            )

    @app_commands.command(name="bestow", description="Bestow (Gift) essences or a spirit to another player.")
    @app_commands.describe(
        user="The player to receive the gift",
        tax_payment="Essence type to use for the ritual fee",
        essence_type="Type of essence to gift (Optional)",
        amount="Amount of essence to gift (Optional)",
        spirit_id="ID of the spirit to gift (Optional)"
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
            await interaction.response.send_message("You cannot bestow to yourself!", ephemeral=True)
            return
        
        try:
            tax_enum = EssenceType(tax_payment.title())
        except ValueError:
            await interaction.response.send_message("Invalid tax payment element.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            if essence_type and amount:
                try:
                    e_type = EssenceType(essence_type.title())
                except ValueError:
                    await interaction.response.send_message("Invalid essence type.", ephemeral=True)
                    return

                success, result = await BestowService.bestow_essence(
                    session, interaction.user.id, user.id, e_type, amount, tax_enum,
                    bot=self.bot, guild_id=interaction.guild_id, channel_id=interaction.channel_id
                )
            elif spirit_id:
                success, result = await BestowService.bestow_spirit(
                    session, interaction.user.id, user.id, spirit_id, tax_enum,
                    bot=self.bot, guild_id=interaction.guild_id, channel_id=interaction.channel_id
                )
            else:
                await interaction.response.send_message("You must specify either essences or a spirit to bestow.", ephemeral=True)
                return

            if success:
                await session.commit()
                await interaction.response.send_message(f"🎁 **Gift Bestowed!** {result}")
            else:
                await session.rollback()
                await interaction.response.send_message(f"❌ **Bestowal Failed:** {result}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TradeCog(bot))
