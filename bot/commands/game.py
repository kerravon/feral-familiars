import discord
from discord.ext import commands
from sqlalchemy import update, select
from bot.db import AsyncSessionLocal
from bot.services.ritual_service import RitualService
from bot.models.familiar import Familiar
from bot.utils.constants import GameConstants

class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ritual", description="Combine a spirit and essences to create a familiar.")
    async def ritual(self, interaction: discord.Interaction, spirit_id: int, essence_type: str):
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

    @discord.app_commands.command(name="equip", description="Equip a familiar to gain its passive bonus.")
    async def equip(self, interaction: discord.Interaction, familiar_id: int):
        async with AsyncSessionLocal() as session:
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

async def setup(bot):
    await bot.add_cog(GameCog(bot))
