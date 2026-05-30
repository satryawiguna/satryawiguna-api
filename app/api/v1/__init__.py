"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1 import blog_posts, auth, media, projects, skills, categories, tags, experiences, educations, settings
from app.api.v1.admin import users as admin_users
from app.api.v1.admin import projects as admin_projects
from app.api.v1.admin import blog_posts as admin_blog_posts
from app.api.v1.admin import skills as admin_skills
from app.api.v1.admin import categories as admin_categories
from app.api.v1.admin import tags as admin_tags
from app.api.v1.admin import experiences as admin_experiences
from app.api.v1.admin import educations as admin_educations
from app.api.v1.admin import settings as admin_settings


# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)  # No prefix for auth routes
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["Admin - Users"])
api_router.include_router(admin_projects.router, prefix="/admin/projects", tags=["Admin - Projects"])
api_router.include_router(admin_blog_posts.router, prefix="/admin/blog-posts", tags=["Admin - Blog Posts"])
api_router.include_router(admin_skills.router, prefix="/admin/skills", tags=["Admin - Skills"])
api_router.include_router(admin_categories.router, prefix="/admin/categories", tags=["Admin - Categories"])
api_router.include_router(admin_tags.router, prefix="/admin/tags", tags=["Admin - Tags"])
api_router.include_router(admin_experiences.router, prefix="/admin/experiences", tags=["Admin - Experiences"])
api_router.include_router(admin_educations.router, prefix="/admin/educations", tags=["Admin - Educations"])
api_router.include_router(admin_settings.router, prefix="/admin/settings", tags=["Admin - Settings"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(blog_posts.router, prefix="/blog-posts", tags=["Blog Posts"])
api_router.include_router(media.router, prefix="/media", tags=["Media Library"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(experiences.router, prefix="/experiences", tags=["Experiences"])
api_router.include_router(educations.router, prefix="/educations", tags=["Educations"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
