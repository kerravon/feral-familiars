import discord
from discord.ext import commands
from bot.db import AsyncSessionLocal
from bot.services.config_service import ConfigService

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            
            await interaction.response.send_message(msg)

    @discord.app_commands.command(name="sync", description="Sync slash commands (Admin only)")
    async def sync(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only admins can sync.", ephemeral=True)
            return
        await self.bot.tree.sync()
        await interaction.response.send_message("Commands synced.")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
