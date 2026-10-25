"""
FairExplain AI — Storage Backend
=================================
Pluggable file storage supporting:
  1. Local filesystem storage (development & fallback).
  2. S3-compatible object storage (AWS S3 with SSE-KMS / MinIO / Cloudflare R2).
"""

from __future__ import annotations

import abc
import hashlib
import os
from pathlib import Path
from typing import Any

from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageBackend(abc.ABC):
    """Abstract interface for document file storage."""

    @staticmethod
    def compute_sha256(content: bytes) -> str:
        """Compute cryptographic SHA-256 hash of byte content."""
        return hashlib.sha256(content).hexdigest()

    @abc.abstractmethod
    async def save_file(
        self,
        filename: str,
        content: bytes,
        application_id: str,
        content_type: str = "application/pdf",
    ) -> tuple[str, str]:
        """Save file bytes. Returns (storage_key_or_url, sha256_hash)."""

    @abc.abstractmethod
    async def get_download_url(self, file_key: str, expires_in: int = 900) -> str:
        """Generate short-lived (default 15-min) secure download URL."""

    @abc.abstractmethod
    async def read_file(self, file_key: str) -> bytes:
        """Read full file bytes from storage."""

    @abc.abstractmethod
    async def delete_file(self, file_key: str) -> bool:
        """Delete file from storage."""


class LocalStorageBackend(StorageBackend):
    """Stores uploaded documents on the local filesystem."""

    def __init__(self, base_dir: str = "uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        filename: str,
        content: bytes,
        application_id: str,
        content_type: str = "application/pdf",
    ) -> tuple[str, str]:
        app_dir = self.base_dir / application_id
        app_dir.mkdir(parents=True, exist_ok=True)

        sha256_hash = self.compute_sha256(content)
        ext = os.path.splitext(filename)[1].lower() or ".pdf"
        safe_filename = f"{sha256_hash[:16]}{ext}"
        destination = app_dir / safe_filename

        with open(destination, "wb") as f:
            f.write(content)

        relative_url = f"/uploads/{application_id}/{safe_filename}"
        return relative_url, sha256_hash

    async def get_download_url(self, file_key: str, expires_in: int = 900) -> str:
        # For local storage, returns the direct relative path
        return file_key

    async def read_file(self, file_key: str) -> bytes:
        path = self.base_dir / file_key.lstrip("/uploads/")
        if not path.exists():
            raise FileNotFoundError(f"File {file_key} not found on local disk.")
        with open(path, "rb") as f:
            return f.read()

    async def delete_file(self, file_key: str) -> bool:
        path = self.base_dir / file_key.lstrip("/uploads/")
        if path.exists():
            path.unlink()
            return True
        return False


class S3StorageBackend(StorageBackend):
    """Asynchronous S3-compatible storage backend (AWS S3 / MinIO / Cloudflare R2)."""

    def __init__(
        self,
        bucket_name: str,
        region_name: str = "ap-south-1",
        endpoint_url: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        kms_key_arn: str | None = None,
    ) -> None:
        import aioboto3

        self.bucket_name = bucket_name
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.kms_key_arn = kms_key_arn
        self.session = aioboto3.Session()

    def _get_client_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"region_name": self.region_name}
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        if self.access_key_id and self.secret_access_key:
            kwargs["aws_access_key_id"] = self.access_key_id
            kwargs["aws_secret_access_key"] = self.secret_access_key
        return kwargs

    async def save_file(
        self,
        filename: str,
        content: bytes,
        application_id: str,
        content_type: str = "application/pdf",
    ) -> tuple[str, str]:
        sha256_hash = self.compute_sha256(content)
        ext = os.path.splitext(filename)[1].lower() or ".pdf"
        safe_filename = f"{sha256_hash[:16]}{ext}"
        object_key = f"applications/{application_id}/{safe_filename}"

        extra_args: dict[str, Any] = {
            "ContentType": content_type,
            "Metadata": {
                "application_id": application_id,
                "sha256": sha256_hash,
            },
        }

        # Apply AWS KMS encryption if configured
        if self.kms_key_arn:
            extra_args["ServerSideEncryption"] = "aws:kms"
            extra_args["SSEKMSKeyId"] = self.kms_key_arn

        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                **extra_args,
            )

        logger.info(
            "document_saved_to_s3",
            bucket=self.bucket_name,
            object_key=object_key,
            sha256=sha256_hash,
        )
        return object_key, sha256_hash

    async def get_download_url(self, file_key: str, expires_in: int = 900) -> str:
        # Clean key if passed as path
        clean_key = file_key.lstrip("/")
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            url: str = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": clean_key},
                ExpiresIn=expires_in,
            )
            return url

    async def read_file(self, file_key: str) -> bytes:
        clean_key = file_key.lstrip("/")
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            resp = await s3.get_object(Bucket=self.bucket_name, Key=clean_key)
            async with resp["Body"] as stream:
                return await stream.read()

    async def delete_file(self, file_key: str) -> bool:
        clean_key = file_key.lstrip("/")
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=clean_key)
            return True


_storage_backend: StorageBackend | None = None


def get_storage_backend() -> StorageBackend:
    """Return storage backend instance according to configuration."""
    global _storage_backend
    settings = get_settings()

    if _storage_backend is None:
        if settings.storage_backend == "s3":
            _storage_backend = S3StorageBackend(
                bucket_name=settings.s3_bucket_name,
                region_name=settings.s3_region_name,
                endpoint_url=settings.s3_endpoint_url,
                access_key_id=settings.aws_access_key_id,
                secret_access_key=settings.aws_secret_access_key,
                kms_key_arn=settings.s3_kms_key_arn,
            )
        else:
            _storage_backend = LocalStorageBackend()
    return _storage_backend
