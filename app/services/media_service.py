"""
Media service for media-related business logic
"""
import uuid
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.other import Media
from app.repositories.media_repository import MediaRepository
from app.utils.media_upload import spaces_uploader
from app.utils.pagination import PaginatedResult


class MediaService:
    """Service for media-related business logic"""

    # Maximum file size: 50 MB
    MAX_FILE_SIZE = 50 * 1024 * 1024

    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "application/x-zip-compressed",
        "video/mp4",
        "video/webm",
        "video/quicktime",
        "video/x-msvideo",
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.media_repository = MediaRepository(db)

    def validate_file(self, file: UploadFile) -> None:
        """Validate file size and MIME type before upload."""
        if file.content_type and file.content_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(
                f"File type '{file.content_type}' is not allowed. "
                f"Allowed types: {', '.join(sorted(self.ALLOWED_MIME_TYPES))}"
            )

    async def upload_file(self, file: UploadFile) -> Media:
        """
        Upload a file to DigitalOcean Spaces and save metadata to database.

        Args:
            file: The uploaded file from FastAPI.

        Returns:
            The created Media record.

        Raises:
            ValueError: If the file type is not allowed or the file is too large.
            RuntimeError: If the upload to Spaces fails.
        """
        self.validate_file(file)

        # Read file content to check size
        file.file.seek(0)
        file_bytes = file.file.read()

        if len(file_bytes) > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE // (1024 * 1024)
            raise ValueError(f"File size exceeds the maximum allowed size of {max_mb} MB")

        # Reset file pointer for the uploader to read again
        file.file.seek(0)

        # Upload to DigitalOcean Spaces
        public_url, unique_filename = spaces_uploader.upload(file)

        # Save metadata to database
        media = Media(
            id=str(uuid.uuid4()),
            file_name=unique_filename,
            file_path=public_url,
            mime_type=file.content_type,
            size=len(file_bytes),
        )

        return await self.media_repository.create(media)

    async def get_media_by_id(self, media_id: str) -> Optional[Media]:
        """Get a single media record by ID."""
        return await self.media_repository.get_by_id(media_id)

    async def get_media_list(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        """Get paginated list of media records."""
        return await self.media_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    async def delete_media(self, media_id: str) -> bool:
        """Delete a media record and its corresponding file from DigitalOcean Spaces."""
        media = await self.media_repository.get_by_id(media_id)
        if not media:
            raise NotFoundError("Media not found")

        # Delete the file from DigitalOcean Spaces
        spaces_uploader.delete(media.file_path)

        return await self.media_repository.delete(media_id)
