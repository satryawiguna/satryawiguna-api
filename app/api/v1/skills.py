"""
Skills API endpoints
"""
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.other import SkillResponse
from app.services.skill_service import SkillService
from app.utils.response import APIResponse, create_pagination_meta


# Allowed columns for groupBy
GROUP_BY_ALLOWED = {"name", "level", "category_id", "sort_order"}

# Allowed level operators
LEVEL_OPERATORS = {"eq", "lt", "lte", "gt", "gte"}

router = APIRouter()


# Response examples for Swagger
_SKILL_DATA = {
    "name": "Python",
    "category_id": 1,
    "level": 90,
    "icon_url": "https://example.com/icons/python.svg",
    "sort_order": 1,
    "id": 1,
    "category": {"id": 1, "name": "Backend", "slug": "backend", "type": "SKILL"}
}

SKILLS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [_SKILL_DATA],
            "pagination": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False
            },
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    },
    "without_pagination": {
        "summary": "Without pagination (default — limit omitted)",
        "description": "Response without pagination metadata (default behaviour)",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [_SKILL_DATA],
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    },
    "level_filtered": {
        "summary": "Filtered by level (gte 80)",
        "description": "Response filtered by level >= 80 using level=80&level_operator=gte",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [_SKILL_DATA],
            "pagination": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False
            },
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    },
    "grouped": {
        "summary": "Grouped by category_id",
        "description": "Data is an array of arrays when groupBy is used",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [
                [
                    {
                        "name": "Python",
                        "category_id": 1,
                        "level": 90,
                        "icon_url": "https://example.com/icons/python.svg",
                        "sort_order": 1,
                        "id": 1,
                        "category": {"id": 1, "name": "Backend", "slug": "backend", "type": "SKILL"}
                    }
                ],
                [
                    {
                        "name": "JavaScript",
                        "category_id": 2,
                        "level": 85,
                        "icon_url": "https://example.com/icons/javascript.svg",
                        "sort_order": 2,
                        "id": 2,
                        "category": {"id": 2, "name": "Frontend", "slug": "frontend", "type": "SKILL"}
                    }
                ]
            ],
            "pagination": {
                "total": 2,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False
            },
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    }
}


@router.get(
    "",
    summary="Get all skills",
    description="""Get all skills with optional pagination and filters.

    **Pagination Options:**
    - Without pagination (default): Omit `limit` to get all skills
    - With pagination: Provide `limit` parameter (e.g. `?limit=10&page=2`)

    **Filters:**
    - `keyword`: Search in name
    - `category`: Filter by category ID
    - `level`: Filter by level value (e.g. `?level=80`)
    - `level_operator`: Comparison operator (default: `eq`).
      Allowed: `eq` (equal), `lt` (less than), `lte` (less than or equal),
      `gt` (greater than), `gte` (greater than or equal).
      Example: `?level=80&level_operator=gte` returns skills with level >= 80.
    - `sortBy`: Field to sort by (default: sort_order)
    - `sortOrder`: ASC or DESC (default: ASC)
    - `orderBy`: Alias for `sortOrder` (asc or desc) — overrides `sortOrder` when provided

    **Grouping:**
    - `groupBy`: Group results by a column value. `data` becomes an array of arrays.
      Allowed columns: `name`, `level`, `category_id`, `sort_order`.
      Works with or without pagination.
    """,
    responses={
        200: {
            "description": "Skills retrieved successfully",
            "content": {
                "application/json": {
                    "examples": SKILLS_LIST_EXAMPLES
                }
            }
        }
    }
)
async def get_skills(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Items per page. Omit or set to null for all skills without pagination"),
    sortBy: str = Query("sort_order", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC) — overridden by orderBy when provided"),
    orderBy: Optional[str] = Query(None, description="Sort order alias (asc or desc) — overrides sortOrder for frontend compatibility"),
    keyword: Optional[str] = Query(None, description="Search keyword for name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    level: Optional[int] = Query(None, ge=0, le=100, description="Filter by level value. Use with level_operator to specify comparison type."),
    level_operator: str = Query("eq", description="Comparison operator for level filter. Allowed: eq, lt, lte, gt, gte"),
    groupBy: Optional[str] = Query(None, description="Group results by this column. Allowed: name, level, category_id, sort_order"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all skills with optional pagination, filters, and grouping.

    Returns list of skills with or without pagination based on limit parameter.
    When groupBy is provided, data becomes an array of arrays grouped by the column value.
    """
    # Normalise sort order — orderBy overrides sortOrder for frontend compatibility
    if orderBy is not None:
        sortOrder = orderBy

    # Validate level_operator
    if level is not None and level_operator not in LEVEL_OPERATORS:
        return APIResponse.error(
            message=f"Invalid level_operator '{level_operator}'. Allowed values: {', '.join(sorted(LEVEL_OPERATORS))}",
            status=422,
        )

    # Validate groupBy column
    if groupBy is not None and groupBy not in GROUP_BY_ALLOWED:
        return APIResponse.error(
            message=f"Invalid groupBy column '{groupBy}'. Allowed values: {', '.join(sorted(GROUP_BY_ALLOWED))}",
            status=422,
        )

    service = SkillService(db)
    result = await service.get_skills(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
        category_id=category_id,
        level=level,
        level_operator=level_operator,
    )

    skills_data = [SkillResponse.from_orm(skill).model_dump() for skill in result.items]

    # Group by column value if groupBy is provided
    if groupBy is not None:
        grouped = defaultdict(list)
        for item in skills_data:
            key = item.get(groupBy)
            grouped[key].append(item)
        data = list(grouped.values())
    else:
        data = skills_data

    if limit is None:
        return APIResponse.success(
            message="Skills retrieved successfully",
            data=data,
        )
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Skills retrieved successfully",
        data=data,
        pagination=pagination,
    )

