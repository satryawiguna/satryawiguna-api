"""refactor_media_to_url_strings

Revision ID: e1a2b3c4d5e6
Revises: 73dd4321d646
Create Date: 2026-05-15 00:00:00.000000

This single migration performs the following interdependent changes:
  1. Drop all FK constraints that reference media.id
  2. Change media.id from BigInteger → String(36) (UUID)
  3. Rename projects.thumbnail_id → thumbnail_url (BigInteger → String)
  4. Rename project_images.media_id → image_url (BigInteger → String)
  5. Rename blog_posts.featured_image_id → featured_image_url (BigInteger → String)
  6. Rename testimonials.avatar_id → avatar_url (BigInteger → String)
  7. Add users.avatar_url (String)

All steps are bundled because dropping / retyping the PK of media invalidates
the existing FK columns immediately — the rename/type-change must happen in the
same migration to avoid a broken intermediate state.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = 'e1a2b3c4d5e6'
down_revision = '73dd4321d646'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # 1. Drop FK constraints that reference media.id
    #    (constraint names vary per DB — query them dynamically)
    # ---------------------------------------------------------------
    conn = op.get_bind()

    # Query actual FK constraint names pointing to media.id
    result = conn.execute(
        sa.text(
            "SELECT TABLE_NAME, CONSTRAINT_NAME "
            "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
            "WHERE REFERENCED_TABLE_NAME = 'media' "
            "AND TABLE_SCHEMA = DATABASE()"
        )
    )
    fk_rows = list(result)

    for row in fk_rows:
        op.drop_constraint(row.CONSTRAINT_NAME, row.TABLE_NAME, type_='foreignkey')

    # ---------------------------------------------------------------
    # 2. Change media.id  BigInteger (auto_increment) → String(36) (UUID)
    #    MySQL requires a raw MODIFY COLUMN to remove auto_increment and
    #    change the type in a single statement.
    # ---------------------------------------------------------------
    conn.execute(sa.text(
        "ALTER TABLE media MODIFY COLUMN id VARCHAR(36) NOT NULL"
    ))

    # ---------------------------------------------------------------
    # 3. projects.thumbnail_id → thumbnail_url  (BigInteger → String)
    # ---------------------------------------------------------------
    op.alter_column(
        'projects', 'thumbnail_id',
        new_column_name='thumbnail_url',
        existing_type=mysql.BIGINT(),
        type_=sa.String(500),
        existing_nullable=True,
    )

    # ---------------------------------------------------------------
    # 4. project_images.media_id → image_url  (BigInteger → String)
    # ---------------------------------------------------------------
    op.alter_column(
        'project_images', 'media_id',
        new_column_name='image_url',
        existing_type=mysql.BIGINT(),
        type_=sa.String(500),
        existing_nullable=False,
    )

    # ---------------------------------------------------------------
    # 5. blog_posts.featured_image_id → featured_image_url  (BigInteger → String)
    # ---------------------------------------------------------------
    op.alter_column(
        'blog_posts', 'featured_image_id',
        new_column_name='featured_image_url',
        existing_type=mysql.BIGINT(),
        type_=sa.String(500),
        existing_nullable=True,
    )

    # ---------------------------------------------------------------
    # 6. testimonials.avatar_id → avatar_url  (BigInteger → String)
    # ---------------------------------------------------------------
    op.alter_column(
        'testimonials', 'avatar_id',
        new_column_name='avatar_url',
        existing_type=mysql.BIGINT(),
        type_=sa.String(500),
        existing_nullable=True,
    )

    # ---------------------------------------------------------------
    # 7. Add avatar_url on users
    # ---------------------------------------------------------------
    op.add_column(
        'users',
        sa.Column('avatar_url', sa.String(500), nullable=True),
    )


def downgrade() -> None:
    # ---------------------------------------------------------------
    # 7. Remove avatar_url from users
    # ---------------------------------------------------------------
    op.drop_column('users', 'avatar_url')

    # ---------------------------------------------------------------
    # 6. testimonials.avatar_url → avatar_id  (String → BigInteger)
    # ---------------------------------------------------------------
    op.alter_column(
        'testimonials', 'avatar_url',
        new_column_name='avatar_id',
        existing_type=sa.String(500),
        type_=mysql.BIGINT(),
        existing_nullable=True,
    )

    # ---------------------------------------------------------------
    # 5. blog_posts.featured_image_url → featured_image_id  (String → BigInteger)
    # ---------------------------------------------------------------
    op.alter_column(
        'blog_posts', 'featured_image_url',
        new_column_name='featured_image_id',
        existing_type=sa.String(500),
        type_=mysql.BIGINT(),
        existing_nullable=True,
    )

    # ---------------------------------------------------------------
    # 4. project_images.image_url → media_id  (String → BigInteger)
    # ---------------------------------------------------------------
    op.alter_column(
        'project_images', 'image_url',
        new_column_name='media_id',
        existing_type=sa.String(500),
        type_=mysql.BIGINT(),
        existing_nullable=False,
    )

    # ---------------------------------------------------------------
    # 3. projects.thumbnail_url → thumbnail_id  (String → BigInteger)
    # ---------------------------------------------------------------
    op.alter_column(
        'projects', 'thumbnail_url',
        new_column_name='thumbnail_id',
        existing_type=sa.String(500),
        type_=mysql.BIGINT(),
        existing_nullable=True,
    )

    # ---------------------------------------------------------------
    # 2. Change media.id  String(36) → BigInteger
    # ---------------------------------------------------------------
    op.drop_index('ix_media_id', table_name='media')
    op.alter_column(
        'media', 'id',
        existing_type=sa.String(36),
        type_=mysql.BIGINT(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.create_index(op.f('ix_media_id'), 'media', ['id'], unique=False)

    # ---------------------------------------------------------------
    # 1. Re-create FK constraints (MySQL auto-names them)
    # ---------------------------------------------------------------
    op.create_foreign_key(
        'project_images_ibfk_1', 'project_images', 'media',
        ['media_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'blog_posts_ibfk_2', 'blog_posts', 'media',
        ['featured_image_id'], ['id'], ondelete='SET NULL',
    )
