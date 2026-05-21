"""add wallets table

Revision ID: 58862ee59ded
Revises: 
Create Date: 2026-05-21 19:40:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '58862ee59ded'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('wallets',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('balance', sa.Numeric(12, 2), server_default='0.00'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('wallets')