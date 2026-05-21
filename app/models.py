from sqlalchemy import Column, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = Column(Numeric(12, 2), default=0.00)