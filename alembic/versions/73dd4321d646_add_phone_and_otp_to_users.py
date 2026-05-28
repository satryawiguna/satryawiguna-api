"""add_phone_and_otp_to_users

Revision ID: 73dd4321d646
Revises: b5c3d8f1a9e2
Create Date: 2026-05-04 14:31:04.359043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73dd4321d646'
down_revision = 'b5c3d8f1a9e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: phone and otp columns already created in migration 72dea81ed358
    pass


def downgrade() -> None:
    # No-op: phone and otp columns will be dropped by migration 72dea81ed358 downgrade
    pass
