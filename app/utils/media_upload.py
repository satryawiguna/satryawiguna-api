"""
Media upload utility for DigitalOcean Spaces (S3-compatible)
"""
import uuid
import mimetypes
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings


class SpacesUploader:
    """Handles file uploads to DigitalOcean Spaces with UUID-based renaming."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                region_name=settings.SPACES_REGION,
                endpoint_url=settings.SPACES_ENDPOINT_URL,
                aws_access_key_id=settings.SPACES_ACCESS_KEY,
                aws_secret_access_key=settings.SPACES_SECRET_KEY,
            )
        return self._client

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """
        Generate a UUID-based filename while preserving the original extension.

        Example: 'photo.jpg' → 'a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg'
        """
        ext = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4()}{ext}"

    def upload(
        self,
        file: UploadFile,
        folder: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Upload a file to DigitalOcean Spaces.

        Args:
            file: The uploaded file from FastAPI.
            folder: Optional subfolder path (e.g., 'dev' or 'prod').

        Returns:
            A tuple of (file_path, file_name) where file_path is the public URL
            and file_name is the UUID-renamed filename.
        """
        if folder is None:
            folder = settings.SPACES_UPLOAD_FOLDER

        unique_filename = self.generate_filename(file.filename or "file")
        object_key = f"{folder}/{unique_filename}"

        # Determine content type – fall back to binary stream
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        # Read the file bytes (UploadFile from FastAPI needs seek to start)
        file.file.seek(0)
        file_bytes = file.file.read()

        try:
            self.client.put_object(
                Bucket=settings.SPACES_BUCKET_NAME,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type,
                ACL="public-read",
            )
        except ClientError as exc:
            raise RuntimeError(f"Failed to upload file to Spaces: {exc}") from exc

        public_url = f"{settings.SPACES_ORIGIN_ENDPOINT}/{object_key}"
        return public_url, unique_filename

    def delete(self, file_path: str) -> bool:
        """
        Delete a file from DigitalOcean Spaces.

        Args:
            file_path: The full public URL or object key of the file to delete.

        Returns:
            True if the file was deleted (or didn't exist), False on unexpected error.
        """
        # Extract object key from the public URL
        object_key = file_path.replace(f"{settings.SPACES_ORIGIN_ENDPOINT}/", "")

        try:
            self.client.delete_object(
                Bucket=settings.SPACES_BUCKET_NAME,
                Key=object_key,
            )
            return True
        except ClientError as exc:
            # Log and swallow – don't block DB deletion if Spaces fails
            print(f"[WARNING] Failed to delete file from Spaces: {object_key} – {exc}")
            return False


# Singleton instance for reuse
spaces_uploader = SpacesUploader()
