from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from enum import Enum

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, decimal_places=2)

    @field_validator('amount')
    def positive_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class BalanceResponse(BaseModel):
    balance: Decimal