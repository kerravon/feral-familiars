import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy import update, select
from bot.db import AsyncSessionLocal
from bot.services.ritual_service import RitualService
from bot.services.passive_service import PassiveService
from bot.services.inventory_service import InventoryService
from bot.models.familiar import Familiar, Spirit
from bot.utils.constants import GameConstants

class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                await interaction.response.send_message(f"✨ **Ritual Success!** You have created a **{result.name}**!")
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

            success = await InventoryService.delete_spirit(session, interaction.user.id, spirit_id)
            if success:
                await interaction.response.send_message(f"🍃 You have released the **{spirit.rarity.title()} {spirit.type} spirit** back into the ether.")
            else:
                await interaction.response.send_message("❌ Failed to release spirit.", ephemeral=True)

    @app_commands.command(name="release-familiar", description="Release a familiar from your stable. This is permanent!")
    @app_commands.autocomplete(familiar_id=familiar_autocomplete)
    async def release_familiar(self, interaction: discord.Interaction, familiar_id: int):
        async with AsyncSessionLocal() as session:
            success, result = await RitualService.delete_familiar(session, interaction.user.id, familiar_id)
            if success:
                await interaction.response.send_message(f"🕊️ **{result}** has been released from your stable and returned to the spirit realm.")
            else:
                await interaction.response.send_message(f"❌ **Release Failed:** {result}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GameCog(bot))
