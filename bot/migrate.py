import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://arcane_user:arcane_pass@db:5432/arcane_db")

async def migrate():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Starting migration...")
        
        # 1. Add new columns to 'users' table if they don't exist
        print("Updating 'users' table...")
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_spirits_gifted INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_essences_gifted INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_gift_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        
        # 2. Create new tables (SQLAlchemy's create_all will only create what's missing)
        print("Creating new tables (trades, trade_offers, channel_configs)...")
        from bot.models.base import Base
        from bot.models.trade import Trade, TradeOffer
        from bot.models.config import ChannelConfig
        
        # This is the safe way to create only the MISSING tables
        await conn.run_sync(Base.metadata.create_all)
        
        print("Migration complete! Inventories preserved.")

if __name__ == "__main__":
    asyncio.run(migrate())
