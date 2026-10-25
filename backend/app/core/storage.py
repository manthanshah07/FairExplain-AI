"""
FairExplain AI — Storage Backend
=================================
Pluggable file storage for uploaded documents (local disk development / S3 compatible).
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


class LocalStorageBackend:
    """Stores uploaded documents on the local filesystem."""

    def __init__(self, base_dir: str = "uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def compute_sha256(self, content: bytes) -> str:
        """Compute cryptographic SHA-256 hash of file contents."""
        return hashlib.sha256(content).hexdigest()

    async def save_file(
        self, filename: str, content: bytes, application_id: str
    ) -> tuple[str, str]:
        """
        Save file to disk under application directory.
        Returns (relative_file_url, sha256_hash).
        """
        app_dir = self.base_dir / application_id
        app_dir.mkdir(parents=True, exist_ok=True)

        sha256_hash = self.compute_sha256(content)
        # Use safe name
        ext = os.path.splitext(filename)[1].lower() or ".pdf"
        safe_filename = f"{sha256_hash[:16]}{ext}"
        destination = app_dir / safe_filename

        with open(destination, "wb") as f:
            f.write(content)

        relative_url = f"/uploads/{application_id}/{safe_filename}"
        return relative_url, sha256_hash


_storage_backend: LocalStorageBackend | None = None


def get_storage_backend() -> LocalStorageBackend:
    """Return singleton storage backend instance."""
    global _storage_backend
    if _storage_backend is None:
        _storage_backend = LocalStorageBackend()
    return _storage_backend
