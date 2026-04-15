import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.models.base import Base, User
from bot.domain.enums import EssenceType, SpiritType, Rarity

# Use in-memory SQLite for fast testing
# Note: SQLite doesn't support Postgres Enums natively, 
# so SQLAlchemy will treat them as strings/VARCHARs automatically.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def mock_user(db_session):
    user = User(id=123456789, stable_limit=3)
    db_session.add(user)
    await db_session.flush() # Sync state without committing
    return user
