import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_session, Base
import os

# Используем тестовую БД (можно отдельный контейнер или заменить на test_db)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/wallet_db_test")

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def setup_db():
    # создать таблицы перед тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def create_wallet():
    """Создаёт новый кошелёк и возвращает его UUID (через прямую вставку в БД)"""
    from uuid import uuid4
    from app.models import Wallet
    async with TestingSessionLocal() as session:
        wallet = Wallet(id=uuid4(), balance=100.00)
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)
        return wallet.id