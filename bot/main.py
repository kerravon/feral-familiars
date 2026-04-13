import asyncio
import discord
from discord.ext import commands
import logging
from bot.db import init_db
from bot.utils.config import Config

# Setup Logging
Config.validate()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeralFamiliars")

class FeralFamiliarsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.initial_extensions = [
            'bot.commands.general',
            'bot.commands.game',
            'bot.commands.trade',
            'bot.commands.admin',
            'bot.commands.tasks',
        ]

    async def setup_hook(self):
        await init_db()
        
        # Load extensions (Cogs)
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}")

        logger.info("Bot setup complete.")

bot = FeralFamiliarsBot()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
