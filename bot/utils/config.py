import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://feral_user:feral_pass@db:5432/feral_db")
    
    # Game Settings
    SPAWN_CHANCE_PERCENT = int(os.getenv("SPAWN_CHANCE_PERCENT", "15"))
    SPAWN_INTERVAL_MINUTES = int(os.getenv("SPAWN_INTERVAL_MINUTES", "2"))
    CLEANUP_INTERVAL_SECONDS = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "10"))
    
    # Limits
    MAX_SPIRITS = int(os.getenv("MAX_SPIRITS", "5"))
    DEFAULT_STABLE_LIMIT = int(os.getenv("DEFAULT_STABLE_LIMIT", "3"))

    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is not set in environment variables.")
