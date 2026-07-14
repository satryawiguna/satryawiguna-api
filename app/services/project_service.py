"""
Project service for project-related business logic
"""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, DuplicateError
from app.models.project import Project, ProjectImage, ProjectSkill, ProjectCategory
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repositories.project_repository import ProjectRepository
from app.utils.pagination import PaginatedResult


class ProjectService:
    """Service for project-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repository = ProjectRepository(db)

    async def get_project_by_id(self, project_id: int, published_only: bool = False) -> Optional[Project]:
        return await self.project_repository.get_by_id_with_relations(project_id, published_only=published_only)

    async def get_project_by_slug(self, slug: str) -> Optional[Project]:
        return await self.project_repository.get_by_slug(slug)

    async def get_projects(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        skill_id: Optional[int] = None,
        published_only: bool = False,
    ) -> PaginatedResult:
        return await self.project_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
            category_id=category_id,
            skill_id=skill_id,
            published_only=published_only,
        )

    async def _sync_relations(self, project: Project, skill_ids, image_urls, category_ids):
        """Delete and re-insert project relations."""
        if skill_ids is not None:
            for ps in list(project.project_skills):
                await self.db.delete(ps)
            for skill_id in skill_ids:
                self.db.add(ProjectSkill(id=str(uuid.uuid4()), project_id=project.id, skill_id=skill_id))

        if image_urls is not None:
            for pi in list(project.project_images):
                await self.db.delete(pi)
            for image_url in image_urls:
                self.db.add(ProjectImage(project_id=project.id, image_url=image_url))

        if category_ids is not None:
            for pc in list(project.project_categories):
                await self.db.delete(pc)
            for category_id in category_ids:
                self.db.add(ProjectCategory(id=str(uuid.uuid4()), project_id=project.id, category_id=category_id))

    async def create_project(self, project_data: ProjectCreate) -> Project:
        existing_project = await self.project_repository.get_by_slug(project_data.slug)
        if existing_project:
            raise DuplicateError("Slug already exists")

        project_dict = project_data.model_dump(exclude={"skill_ids", "image_urls", "category_ids"})
        project = Project(**project_dict)
        self.db.add(project)
        await self.db.flush()

        # Directly add relations — no need to iterate over existing ones for a new project.
        # This avoids lazy-loading issues on the newly flushed (persistent) object.
        for skill_id in (project_data.skill_ids or []):
            self.db.add(ProjectSkill(id=str(uuid.uuid4()), project_id=project.id, skill_id=skill_id))
        for image_url in (project_data.image_urls or []):
            self.db.add(ProjectImage(project_id=project.id, image_url=image_url))
        for category_id in (project_data.category_ids or []):
            self.db.add(ProjectCategory(id=str(uuid.uuid4()), project_id=project.id, category_id=category_id))

        await self.db.commit()

        # Expire cached state so the re-query populates all relations fresh.
        # Capture ID before expiring — accessing project.id after expire triggers lazy load.
        created_id = project.id
        self.db.expire(project)
        return await self.project_repository.get_by_id_with_relations(created_id)

    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> Project:
        project = await self.project_repository.get_by_id_with_relations(project_id)
        if not project:
            raise NotFoundError("Project not found")

        if project_data.slug and project_data.slug != project.slug:
            existing_project = await self.project_repository.get_by_slug(project_data.slug)
            if existing_project:
                raise DuplicateError("Slug already exists")

        data = project_data.model_dump(exclude_unset=True, exclude={"skill_ids", "image_urls", "category_ids"})
        for field, value in data.items():
            setattr(project, field, value)

        skill_ids = project_data.skill_ids if project_data.skill_ids is not None else None
        image_urls = project_data.image_urls if project_data.image_urls is not None else None
        category_ids = project_data.category_ids if project_data.category_ids is not None else None

        await self._sync_relations(project, skill_ids, image_urls, category_ids)
        await self.db.commit()

        # Expire cached state so the re-query populates all relations fresh.
        # Capture ID before expiring — accessing project.id after expire triggers lazy load.
        updated_id = project.id
        self.db.expire(project)
        return await self.project_repository.get_by_id_with_relations(updated_id)

    async def delete_project(self, project_id: int) -> bool:
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        return await self.project_repository.delete(project_id)

