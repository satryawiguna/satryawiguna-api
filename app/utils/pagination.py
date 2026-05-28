"""
Pagination utilities
"""
from typing import TypeVar, Generic, List, Optional, TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.sql import Select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = 1
    limit: Optional[int] = 10
    sortBy: str = "id"
    sortOrder: str = "DESC"
    keyword: Optional[str] = None

    class Config:
        frozen = True


class PaginatedResult(Generic[T]):
    """Paginated query result"""

    def __init__(self, items: List[T], total: int, page: int, limit: int):
        self.items = items
        self.total = total
        self.page = page
        self.limit = limit

    @property
    def total_pages(self) -> int:
        if self.limit == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


async def paginate_async(
    db: "AsyncSession",
    stmt: Select,
    page: int = 1,
    limit: Optional[int] = 10,
) -> PaginatedResult:
    """
    Paginate a SQLAlchemy 2.0 select statement using an AsyncSession.

    Args:
        db: Async database session
        stmt: A SQLAlchemy ``select()`` statement (filters/ordering already applied)
        page: 1-based page number
        limit: Rows per page; ``None`` returns all rows without pagination

    Returns:
        PaginatedResult containing items + total count
    """
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar() or 0

    if limit is None:
        result = await db.execute(stmt)
        items = result.scalars().all()
        return PaginatedResult(items=items, total=total, page=1, limit=total or 0)

    offset = (page - 1) * limit
    result = await db.execute(stmt.offset(offset).limit(limit))
    items = result.scalars().all()
    return PaginatedResult(items=items, total=total, page=page, limit=limit)
