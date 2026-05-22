import pytest
from httpx import AsyncClient
import asyncio
from uuid import uuid4
from app.models import Wallet
from app.database import AsyncSessionLocal

pytestmark = pytest.mark.asyncio

async def test_get_balance_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/wallets/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

async def test_deposit(client: AsyncClient):
    async with AsyncSessionLocal() as session:
        wallet = Wallet(id=uuid4(), balance=100.00)
        session.add(wallet)
        await session.commit()
        wallet_id = wallet.id
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 50.0}
    )
    assert resp.status_code == 200
    assert resp.json()["balance"] == 150.0

async def test_withdraw_success(client: AsyncClient):
    async with AsyncSessionLocal() as session:
        wallet = Wallet(id=uuid4(), balance=100.00)
        session.add(wallet)
        await session.commit()
        wallet_id = wallet.id
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 30.0}
    )
    assert resp.status_code == 200
    assert resp.json()["balance"] == 70.0

async def test_withdraw_insufficient(client: AsyncClient):
    async with AsyncSessionLocal() as session:
        wallet = Wallet(id=uuid4(), balance=50.00)
        session.add(wallet)
        await session.commit()
        wallet_id = wallet.id
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 100.0}
    )
    assert resp.status_code == 400
    assert "Insufficient funds" in resp.text

async def test_concurrent_updates(client: AsyncClient):
    async with AsyncSessionLocal() as session:
        wallet = Wallet(id=uuid4(), balance=100.00)
        session.add(wallet)
        await session.commit()
        wallet_id = wallet.id

    for _ in range(5):
        resp = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "DEPOSIT", "amount": 10})
        assert resp.status_code == 200
    for _ in range(5):
        resp = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 5})
        assert resp.status_code == 200

    resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert float(resp.json()["balance"]) == 125.0