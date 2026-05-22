from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet
from decimal import Decimal
from uuid import UUID

async def get_wallet_balance(session: AsyncSession, wallet_id: UUID) -> Decimal | None:
    result = await session.execute(select(Wallet.balance).where(Wallet.id == wallet_id))
    return result.scalar_one_or_none()

async def update_balance(session: AsyncSession, wallet_id: UUID, amount: Decimal, operation: str) -> Decimal:
    stmt = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise ValueError("Wallet not found")
    if operation == "WITHDRAW" and wallet.balance < amount:
        raise ValueError("Insufficient funds")
    if operation == "DEPOSIT":
        wallet.balance += amount
    else:
        wallet.balance -= amount
    await session.commit()
    return wallet.balance