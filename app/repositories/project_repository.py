"""
Project repository for project-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectSkill, ProjectCategory
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_by_slug(self, slug: str) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.project_images),
                selectinload(Project.project_skills).selectinload(ProjectSkill.skill),
                selectinload(Project.project_categories).selectinload(ProjectCategory.category),
            )
            .where(Project.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, project_id: int) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.project_images),
                selectinload(Project.project_skills).selectinload(ProjectSkill.skill),
                selectinload(Project.project_categories).selectinload(ProjectCategory.category),
            )
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        skill_id: Optional[int] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(Project, sort_by, Project.id)
        order = desc(sort_column) if sort_order.upper() == "DESC" else asc(sort_column)
        stmt = (
            select(Project)
            .options(
                selectinload(Project.project_images),
                selectinload(Project.project_skills).selectinload(ProjectSkill.skill),
                selectinload(Project.project_categories).selectinload(ProjectCategory.category),
            )
            .order_by(order)
        )

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(Project.title.ilike(pattern), Project.description.ilike(pattern))
            )
        if category_id is not None:
            stmt = stmt.where(
                exists().where(
                    (ProjectCategory.project_id == Project.id) &
                    (ProjectCategory.category_id == category_id)
                )
            )
        if skill_id is not None:
            stmt = stmt.where(
                exists().where(
                    (ProjectSkill.project_id == Project.id) &
                    (ProjectSkill.skill_id == skill_id)
                )
            )

        return await paginate_async(self.db, stmt, page=page, limit=limit)

