"""
Admin Settings API endpoints
"""
from typing import Dict, Optional

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.setting_service import SettingService
from app.utils.response import APIResponse


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_SETTINGS_DATA = {
    "GITHUB_URL": "https://github.com/satryawiguna",
    "LINKED_IN_URL": "https://linkedin.com/in/satryawiguna",
    "RESUME_FILE_URL": None,
}

SETTINGS_GET_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Setting retrieved successfully",
        "data": _SETTINGS_DATA,
        "timestamp": "2026-05-30T00:00:00.000Z",
    }
}



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "",
    summary="Get all settings",
    description="Retrieve all application settings as a flat key/value map.",
    responses={
        200: {
            "description": "Setting retrieved successfully",
            "content": {"application/json": SETTINGS_GET_EXAMPLE},
        }
    },
)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingService(db)
    data = await service.get_all_settings()
    return APIResponse.success(message="Setting retrieved successfully", data=data)


@router.put(
    "",
    summary="Update settings",
    description="""Update one or more settings in bulk.

Supply a flat JSON object where each key is a setting name and the value is a string or `null`.
Only the keys present in the request body are updated; other existing settings are unchanged.
New keys that do not yet exist in the database will be created automatically.
""",
)
async def update_settings(
    data: Dict[str, Optional[str]] = Body(
        ...,
        example={
            "GITHUB_URL": "https://github.com/satryawiguna",
            "LINKED_IN_URL": "https://linkedin.com/in/satryawiguna",
            "RESUME_FILE_URL": "test",
        },
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingService(db)
    updated = await service.update_settings(data)
    return APIResponse.success(message="Setting updated successfully", data=updated)
