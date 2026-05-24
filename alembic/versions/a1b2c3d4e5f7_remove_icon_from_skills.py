"""remove icon from skills

Revision ID: a1b2c3d4e5f7
Revises: 986226cff33f
Create Date: 2026-05-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f7'
down_revision = '986226cff33f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('skills', 'icon')


def downgrade() -> None:
    op.add_column('skills', sa.Column('icon', sa.String(255), nullable=True))
