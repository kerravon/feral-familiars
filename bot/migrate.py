import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://arcane_user:arcane_pass@db:5432/arcane_db")

async def migrate():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Starting migration...")
        
        # 1. Update 'users' table
        print("Updating 'users' table...")
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_spirits_gifted INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_essences_gifted INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_gift_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS stored_essence_lure_mins INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS stored_spirit_lure_mins INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS stored_pure_lure_mins INTEGER DEFAULT 0"))
        
        # 2. Update 'familiars' table
        print("Updating 'familiars' table...")
        await conn.execute(text("ALTER TABLE familiars ADD COLUMN IF NOT EXISTS active_until TIMESTAMP"))
        await conn.execute(text("ALTER TABLE familiars ADD COLUMN IF NOT EXISTS last_activated_at TIMESTAMP"))
        await conn.execute(text("ALTER TABLE familiars ADD COLUMN IF NOT EXISTS daily_trigger_count INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE familiars ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1"))
        await conn.execute(text("ALTER TABLE familiars ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0"))

        # 3. Update 'encounters' table
        print("Updating 'encounters' table...")
        await conn.execute(text("ALTER TABLE encounters ADD COLUMN IF NOT EXISTS blacklisted_user_id BIGINT"))
        await conn.execute(text("ALTER TABLE encounters ADD COLUMN IF NOT EXISTS captured_by BIGINT"))

        # 4. Update 'channel_configs' table
        print("Updating 'channel_configs' table...")
        await conn.execute(text("ALTER TABLE channel_configs ADD COLUMN IF NOT EXISTS active_lure_type VARCHAR(20)"))
        await conn.execute(text("ALTER TABLE channel_configs ADD COLUMN IF NOT EXISTS active_lure_subtype VARCHAR(20)"))
        await conn.execute(text("ALTER TABLE channel_configs ADD COLUMN IF NOT EXISTS lure_expires_at TIMESTAMP"))

        # 5. Create new tables
        print("Ensuring all tables exist...")
        from bot.models.base import Base
        from bot.models.trade import Trade, TradeOffer
        from bot.models.config import ChannelConfig
        from bot.models.essence import Essence
        from bot.models.familiar import Familiar, Spirit
        from bot.models.encounter import Encounter, EncounterParticipant
        
        await conn.run_sync(Base.metadata.create_all)
        
        print("Migration complete! All new systems (Resonance, Surges, Leveling, Incense) ready.")

if __name__ == "__main__":
    asyncio.run(migrate())
