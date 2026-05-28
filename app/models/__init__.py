"""
Models package initialization
Import all models to ensure they're registered with SQLAlchemy
"""
from app.models.other import Media, Setting, Skill
from app.models.user import User, Role, UserRole
from app.models.project import Project, ProjectImage, ProjectSkill, ProjectCategory
from app.models.blog import BlogPost, Category, Tag, BlogPostCategory, BlogPostTag

__all__ = [
    # Other models
    "Media",
    "Setting",
    "Skill",

    # User models
    "User",
    "Role",
    "UserRole",

    # Project models
    "Project",
    "ProjectImage",
    "ProjectSkill",
    "ProjectCategory",

    # Blog models
    "BlogPost",
    "Category",
    "Tag",
    "BlogPostCategory",
    "BlogPostTag",
]
