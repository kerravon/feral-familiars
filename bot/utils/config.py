import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://feral_user:feral_pass@db:5432/feral_db")
    
    # Game Settings
    SPAWN_CHANCE_PERCENT = int(os.getenv("SPAWN_CHANCE_PERCENT", "25"))
    SPAWN_INTERVAL_SECONDS = int(os.getenv("SPAWN_INTERVAL_SECONDS", "300"))
    SPAWN_INTERVAL_MINUTES = int(os.getenv("SPAWN_INTERVAL_MINUTES", "5")) # Legacy fallback
    CLEANUP_INTERVAL_SECONDS = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "10"))
    CAPTURE_WINDOW_SECONDS = int(os.getenv("CAPTURE_WINDOW_SECONDS", "45"))
    ANTI_MACRO_DELAY_SECONDS = int(os.getenv("ANTI_MACRO_DELAY_SECONDS", "1"))
    PLAYER_COOLDOWN_SECONDS = int(os.getenv("PLAYER_COOLDOWN_SECONDS", "30"))
    
    # Limits
    MAX_ESSENCES = int(os.getenv("MAX_ESSENCES", "500"))
    MAX_SPIRITS = int(os.getenv("MAX_SPIRITS", "5"))
    MAX_FAMILIARS = int(os.getenv("MAX_FAMILIARS", "5"))
    DEFAULT_STABLE_LIMIT = int(os.getenv("DEFAULT_STABLE_LIMIT", "3"))

    @classmethod
    def validate(cls):
        """Validates critical environment variables."""
        missing = []
        if not cls.DISCORD_TOKEN:
            missing.append("DISCORD_TOKEN")
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
        
        if missing:
            raise ValueError(f"CRITICAL: Missing required environment variables: {', '.join(missing)}")
        
        # Sane range checks
        if not (0 <= cls.SPAWN_CHANCE_PERCENT <= 100):
            raise ValueError("SPAWN_CHANCE_PERCENT must be between 0 and 100.")
        
        if cls.SPAWN_INTERVAL_SECONDS < 10:
            raise ValueError("SPAWN_INTERVAL_SECONDS must be at least 10 seconds.")
        
        if cls.CAPTURE_WINDOW_SECONDS < 5:
            raise ValueError("CAPTURE_WINDOW_SECONDS must be at least 5 seconds.")
