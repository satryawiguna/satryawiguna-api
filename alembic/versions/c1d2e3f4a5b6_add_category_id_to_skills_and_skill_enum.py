"""add category_id to skills and add SKILL to category_type enum

Revision ID: c1d2e3f4a5b6
Revises: a1b2c3d4e5f7
Create Date: 2026-05-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = 'a1b2c3d4e5f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add SKILL to category_type enum
    op.execute(
        "ALTER TABLE categories MODIFY COLUMN type "
        "ENUM('BLOG_POST', 'PROJECT', 'SKILL') NOT NULL DEFAULT 'BLOG_POST'"
    )

    # 2. Add category_id column (nullable initially for existing data)
    op.add_column('skills', sa.Column('category_id', sa.BigInteger(), nullable=True))

    # 3. Create foreign key constraint
    op.create_foreign_key(
        'fk_skills_category_id_categories',
        'skills', 'categories',
        ['category_id'], ['id'],
        ondelete='SET NULL'
    )

    # 4. Drop the old category column
    op.drop_column('skills', 'category')


def downgrade() -> None:
    # 1. Re-add the old category column
    op.add_column('skills', sa.Column('category', sa.String(255), nullable=True))

    # 2. Drop foreign key constraint
    op.drop_constraint('fk_skills_category_id_categories', 'skills', type_='foreignkey')

    # 3. Drop category_id column
    op.drop_column('skills', 'category_id')

    # 4. Remove SKILL from category_type enum
    op.execute(
        "ALTER TABLE categories MODIFY COLUMN type "
        "ENUM('BLOG_POST', 'PROJECT') NOT NULL DEFAULT 'BLOG_POST'"
    )
