"""add_strengths_table

Revision ID: h1i2j3k4l5m6
Revises: g1h2i3j4k5l6
Create Date: 2026-07-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'h1i2j3k4l5m6'
down_revision = 'g1h2i3j4k5l6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'strengths',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_strengths_id', 'strengths', ['id'])


def downgrade() -> None:
    op.drop_index('ix_strengths_id', table_name='strengths')
    op.drop_table('strengths')
