"""add_refresh_tokens_table

Revision ID: b5c3d8f1a9e2
Revises: 72dea81ed358
Create Date: 2026-03-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b5c3d8f1a9e2'
down_revision = '72dea81ed358'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: refresh_tokens table already created in migration 72dea81ed358
    pass


def downgrade() -> None:
    # No-op: refresh_tokens table will be dropped by migration 72dea81ed358 downgrade
    pass
