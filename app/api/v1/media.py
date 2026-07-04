"""
Media Library API endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.other import MediaResponse, MediaUploadResponse
from app.services.media_service import MediaService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response examples
# ---------------------------------------------------------------------------

MEDIA_UPLOAD_EXAMPLE = {
    "summary": "Successful file upload",
    "value": {
        "success": True,
        "status": 201,
        "message": "File uploaded successfully",
        "data": {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "file_name": "f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
            "url": "https://satryawiguna-bucket.sgp1.digitaloceanspaces.com/dev/f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
            "mime_type": "image/jpeg",
            "size": 245760,
            "created_at": "2026-05-15T10:30:00.000Z"
        },
        "timestamp": "2026-05-15T10:30:00.000Z"
    }
}

MEDIA_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination",
        "value": {
            "success": True,
            "status": 200,
            "message": "Media retrieved successfully",
            "data": [
                {
                    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "file_name": "f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
                    "url": "https://satryawiguna-bucket.sgp1.digitaloceanspaces.com/dev/f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
                    "mime_type": "image/jpeg",
                    "size": 245760,
                    "created_at": "2026-05-15T10:30:00.000Z"
                }
            ],
            "pagination": {
                "total": 15,
                "page": 1,
                "limit": 10,
                "totalPages": 2,
                "hasNextPage": True,
                "hasPreviousPage": False
            },
            "timestamp": "2026-05-15T10:30:00.000Z"
        }
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "value": {
            "success": True,
            "status": 200,
            "message": "Media retrieved successfully",
            "data": [
                {
                    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "file_name": "f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
                    "url": "https://satryawiguna-bucket.sgp1.digitaloceanspaces.com/dev/f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
                    "mime_type": "image/jpeg",
                    "size": 245760,
                    "created_at": "2026-05-15T10:30:00.000Z"
                }
            ],
            "timestamp": "2026-05-15T10:30:00.000Z"
        }
    }
}

MEDIA_DETAIL_EXAMPLE = {
    "summary": "Single media item",
    "value": {
        "success": True,
        "status": 200,
        "message": "Media retrieved successfully",
        "data": {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "file_name": "f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
            "url": "https://satryawiguna-bucket.sgp1.digitaloceanspaces.com/dev/f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg",
            "mime_type": "image/jpeg",
            "size": 245760,
            "created_at": "2026-05-15T10:30:00.000Z"
        },
        "timestamp": "2026-05-15T10:30:00.000Z"
    }
}


def _media_to_response(media) -> dict:
    """Convert a Media model instance to the response dict with 'url' field."""
    return {
        "id": media.id,
        "file_name": media.file_name,
        "url": media.file_path,
        "mime_type": media.mime_type,
        "size": media.size,
        "created_at": media.created_at.isoformat() if media.created_at else None,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description="""Upload a file to the media library.

Files are automatically renamed using a UUID to prevent name collisions and
stored on DigitalOcean Spaces in a folder determined by the application environment:

- **Dev/Local** → uploaded to the `dev/` folder
- **Production** → uploaded to the `prod/` folder

**Allowed file types:** JPEG, PNG, GIF, WebP, SVG, PDF, TXT, DOC, DOCX, XLS, XLSX, ZIP, MP4, WEBM, MOV, AVI

**Maximum file size:** 50 MB

Requires authentication.
""",
    responses={
        201: {
            "description": "File uploaded successfully",
            "content": {
                "application/json": {
                    "examples": {"success": MEDIA_UPLOAD_EXAMPLE}
                }
            }
        },
        400: {"description": "Invalid file type or file too large"},
        401: {"description": "Authentication required"},
    },
)
async def upload_media(
    file: UploadFile = File(..., description="The file to upload"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file to the media library. Requires authentication.
    """
    service = MediaService(db)
    
    try:
        media = await service.upload_file(file)
    except ValueError as exc:
        return APIResponse.error(
            message=str(exc),
            status=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as exc:
        return APIResponse.error(
            message=str(exc),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return APIResponse.success(
        message="File uploaded successfully",
        status=status.HTTP_201_CREATED,
        data=_media_to_response(media),
    )


@router.get(
    "",
    summary="Get all media",
    description="""Get all media files with optional pagination and search.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all media files

**Filters:**
- `keyword`: Search in file name
- `sortBy`: Field to sort by (default: created_at)
- `sortOrder`: ASC or DESC (default: DESC)
""",
    responses={
        200: {
            "description": "Media retrieved successfully",
            "content": {
                "application/json": {
                    "examples": MEDIA_LIST_EXAMPLES
                }
            }
        }
    },
)
async def get_media_list(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all media without pagination"),
    sortBy: str = Query("created_at", description="Sort field"),
    sortOrder: str = Query("DESC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for file name"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all media files with optional pagination and search.
    """
    service = MediaService(db)
    result = await service.get_media_list(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )

    media_data = [_media_to_response(item) for item in result.items]

    if limit is None:
        return APIResponse.success(
            message="Media retrieved successfully",
            data=media_data,
        )

    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Media retrieved successfully",
        data=media_data,
        pagination=pagination,
    )


@router.get(
    "/{media_id}",
    summary="Get a media item by ID",
    responses={
        200: {
            "description": "Media retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {"success": MEDIA_DETAIL_EXAMPLE}
                }
            }
        },
        404: {"description": "Media not found"},
    },
)
async def get_media(
    media_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single media item by its UUID.
    """
    service = MediaService(db)
    media = await service.get_media_by_id(media_id)

    if not media:
        return APIResponse.error(
            message="Media not found",
            status=status.HTTP_404_NOT_FOUND,
        )

    return APIResponse.success(
        message="Media retrieved successfully",
        data=_media_to_response(media),
    )


@router.delete(
    "/{media_id}",
    summary="Delete a media item",
    responses={
        200: {"description": "Media deleted successfully"},
        404: {"description": "Media not found"},
        401: {"description": "Authentication required"},
    },
)
async def delete_media(
    media_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a media item by its UUID. Requires authentication.

    This removes both the database record AND the file from DigitalOcean Spaces.
    """
    service = MediaService(db)
    await service.delete_media(media_id)

    return APIResponse.success(
        message="Media deleted successfully",
    )
