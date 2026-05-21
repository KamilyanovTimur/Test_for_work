from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal

from app import schemas, crud
from app.database import get_session

app = FastAPI(title="Wallet API", version="1.0")

@app.post("/api/v1/wallets/{wallet_uuid}/operation", status_code=200)
async def perform_operation(
    wallet_uuid: UUID,
    operation: schemas.OperationRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        new_balance = await crud.update_balance(
            session, wallet_uuid, operation.amount, operation.operation_type.value
        )
        return {"balance": new_balance}
    except ValueError as e:
        if str(e) == "Wallet not found":
            raise HTTPException(status_code=404, detail="Wallet not found")
        elif str(e) == "Insufficient funds":
            raise HTTPException(status_code=400, detail="Insufficient funds")
        else:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/wallets/{wallet_uuid}", response_model=schemas.BalanceResponse)
async def get_balance(
    wallet_uuid: UUID,
    session: AsyncSession = Depends(get_session)
):
    balance = await crud.get_wallet_balance(session, wallet_uuid)
    if balance is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return schemas.BalanceResponse(balance=balance)