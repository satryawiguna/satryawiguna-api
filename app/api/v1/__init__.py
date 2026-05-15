"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1 import users, projects, blog_posts, auth, skills, media


# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)  # No prefix for auth routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(blog_posts.router, prefix="/blog-posts", tags=["Blog Posts"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(media.router, prefix="/media", tags=["Media Library"])
