import pytest
from httpx import AsyncClient
import asyncio
from decimal import Decimal

pytestmark = pytest.mark.asyncio

async def test_get_balance_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/wallets/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

async def test_deposit(client: AsyncClient, create_wallet):
    wallet_id = await create_wallet
    # сначала узнаём баланс
    resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert resp.status_code == 200
    old_balance = Decimal(resp.json()["balance"])

    # пополняем на 50
    payload = {"operation_type": "DEPOSIT", "amount": 50.00}
    resp = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json=payload)
    assert resp.status_code == 200
    new_balance = Decimal(resp.json()["balance"])
    assert new_balance == old_balance + 50

async def test_withdraw_success(client: AsyncClient, create_wallet):
    wallet_id = await create_wallet
    resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    old_balance = Decimal(resp.json()["balance"])
    # снимаем 30
    payload = {"operation_type": "WITHDRAW", "amount": 30.00}
    resp = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json=payload)
    assert resp.status_code == 200
    new_balance = Decimal(resp.json()["balance"])
    assert new_balance == old_balance - 30

async def test_withdraw_insufficient(client: AsyncClient, create_wallet):
    wallet_id = await create_wallet
    payload = {"operation_type": "WITHDRAW", "amount": 200.00}
    resp = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json=payload)
    assert resp.status_code == 400
    assert "Insufficient funds" in resp.text

async def test_concurrent_updates(client: AsyncClient, create_wallet):
    wallet_id = await create_wallet
    # начальный баланс 100
    # запускаем 5 пополнений по 10 и 5 снятий по 5 параллельно
    async def deposit():
        return await client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "DEPOSIT", "amount": 10})

    async def withdraw():
        return await client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 5})

    tasks = [deposit() for _ in range(5)] + [withdraw() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    # все запросы должны быть успешны (200)
    for resp in results:
        assert resp.status_code == 200

    # итоговый баланс: 100 + 5*10 - 5*5 = 100 + 50 - 25 = 125
    resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    final_balance = Decimal(resp.json()["balance"])
    assert final_balance == 125