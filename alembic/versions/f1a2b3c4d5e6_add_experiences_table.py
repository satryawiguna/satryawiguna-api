"""add_experiences_table

Revision ID: f1a2b3c4d5e6
Revises: c1d2e3f4a5b6
Create Date: 2026-05-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None

employment_type_enum = sa.Enum(
    'FULL_TIME', 'PART_TIME', 'CONTRACT', 'FREELANCE', 'INTERNSHIP',
    name='employment_type',
)


def upgrade() -> None:
    # Create employment_type enum type
    employment_type_enum.create(op.get_bind(), checkfirst=True)

    # Create experiences table
    op.create_table(
        'experiences',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column(
            'employment_type',
            sa.Enum('FULL_TIME', 'PART_TIME', 'CONTRACT', 'FREELANCE', 'INTERNSHIP', name='employment_type'),
            nullable=False,
            server_default='FULL_TIME',
        ),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_experiences_id', 'experiences', ['id'])

    # Create experience_skills pivot table
    op.create_table(
        'experience_skills',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('experience_id', sa.BigInteger(), sa.ForeignKey('experiences.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', sa.BigInteger(), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('experience_skills')
    op.drop_index('ix_experiences_id', table_name='experiences')
    op.drop_table('experiences')
    employment_type_enum.drop(op.get_bind(), checkfirst=True)
