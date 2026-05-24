"""restructure_projects_blog_skills_categories_tags

Revision ID: 986226cff33f
Revises: e1a2b3c4d5e6
Create Date: 2026-05-16 10:11:34.961923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '986226cff33f'
down_revision = 'e1a2b3c4d5e6'
branch_labels = None
depends_on = None

category_type_enum = sa.Enum('BLOG_POST', 'PROJECT', name='category_type')


def upgrade() -> None:
    # --- projects table ---
    op.add_column('projects', sa.Column('sub_title', sa.String(255), nullable=True))
    op.drop_column('projects', 'featured')

    # --- blog_posts table ---
    op.drop_column('blog_posts', 'featured_image_url')
    op.add_column('blog_posts', sa.Column('thumbnail_url', sa.String(500), nullable=True))
    op.add_column('blog_posts', sa.Column('image_url', sa.String(500), nullable=True))

    # --- categories table: add type column ---
    category_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('categories', sa.Column('type', sa.Enum('BLOG_POST', 'PROJECT', name='category_type'), nullable=False, server_default='BLOG_POST'))

    # --- skills table ---
    op.add_column('skills', sa.Column('icon_url', sa.String(500), nullable=True))

    # --- blog_post_categories: change id to UUID ---
    op.drop_table('blog_post_categories')
    op.create_table(
        'blog_post_categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('post_id', sa.BigInteger, sa.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.BigInteger, sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
    )

    # --- blog_post_tags: change id to UUID ---
    op.drop_table('blog_post_tags')
    op.create_table(
        'blog_post_tags',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('post_id', sa.BigInteger, sa.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_id', sa.BigInteger, sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
    )

    # --- project_skills table ---
    op.create_table(
        'project_skills',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.BigInteger, sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', sa.BigInteger, sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
    )

    # --- project_categories table ---
    op.create_table(
        'project_categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.BigInteger, sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.BigInteger, sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
    )

    # --- drop testimonials table ---
    op.drop_table('testimonials')


def downgrade() -> None:
    # Recreate testimonials
    op.create_table(
        'testimonials',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('position', sa.String(255), nullable=True),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('featured', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    op.drop_table('project_categories')
    op.drop_table('project_skills')

    # Recreate blog_post_tags with BigInteger id
    op.drop_table('blog_post_tags')
    op.create_table(
        'blog_post_tags',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('post_id', sa.BigInteger, sa.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_id', sa.BigInteger, sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
    )

    # Recreate blog_post_categories with BigInteger id
    op.drop_table('blog_post_categories')
    op.create_table(
        'blog_post_categories',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('post_id', sa.BigInteger, sa.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.BigInteger, sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
    )

    op.drop_column('skills', 'icon_url')
    op.drop_column('categories', 'type')
    category_type_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_column('blog_posts', 'image_url')
    op.drop_column('blog_posts', 'thumbnail_url')
    op.add_column('blog_posts', sa.Column('featured_image_url', sa.String(500), nullable=True))

    op.add_column('projects', sa.Column('featured', sa.Boolean, default=False, nullable=False))
    op.drop_column('projects', 'sub_title')
