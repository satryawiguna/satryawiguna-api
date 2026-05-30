"""
Public Settings API endpoints (read-only, no auth)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.setting_service import SettingService
from app.utils.response import APIResponse


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
SETTINGS_BY_KEYS_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Setting retrieved successfully",
            "data": {
                "GITHUB_URL": "https://github.com/satryawiguna",
                "LINKED_IN_URL": "https://linkedin.com/in/satryawiguna",
            },
            "timestamp": "2026-05-30T00:00:00.000Z",
        }
    }
}


@router.get(
    "",
    summary="Get settings by keys (public)",
    description="""Retrieve one or more settings by key name.

**`slugs` parameter** — comma-separated list of setting keys, e.g. `GITHUB_URL,LINKED_IN_URL`.
If `slugs` is omitted, all settings are returned.
""",
    responses={
        200: {
            "description": "Setting retrieved successfully",
            "content": {"application/json": SETTINGS_BY_KEYS_EXAMPLE},
        }
    },
)
async def get_settings(
    slugs: Optional[str] = Query(
        None,
        description="Comma-separated setting keys, e.g. GITHUB_URL,LINKED_IN_URL",
        example="GITHUB_URL,LINKED_IN_URL",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = SettingService(db)
    if slugs:
        keys = [k.strip() for k in slugs.split(",") if k.strip()]
        data = await service.get_settings_by_keys(keys)
    else:
        data = await service.get_all_settings()
    return APIResponse.success(message="Setting retrieved successfully", data=data)
