import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.models.base import Base
from bot.utils.config import Config

# Database URL from Config
DATABASE_URL = Config.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """
    Initializes the database. 
    Note: Ongoing schema changes should be handled via Alembic migrations.
    """
    async with engine.begin() as conn:
        # We still use create_all for initial setup in new environments
        # but Alembic will manage it thereafter.
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
