"""
FairExplain AI — Storage Backend Unit Tests
============================================
Tests:
1. Cryptographic SHA-256 verification.
2. Local filesystem storage lifecycle (save, read, download url, delete).
3. S3StorageBackend configuration and client kwargs generation.
4. S3 async operations (put_object with KMS, generate_presigned_url, read_file stream, delete_object).
"""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.storage import LocalStorageBackend, S3StorageBackend, StorageBackend


def test_sha256_computation() -> None:
    """StorageBackend must compute standard SHA-256 hex digest."""
    payload = b"FairExplain Document Content Verification"
    expected = hashlib.sha256(payload).hexdigest()
    assert StorageBackend.compute_sha256(payload) == expected


@pytest.mark.anyio
async def test_local_storage_backend_lifecycle(tmp_path: any) -> None:
    """LocalStorageBackend should store, read, and delete files on disk."""
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    content = b"%PDF-1.4 Mock Income Certificate Document"
    app_id = "test-app-123"

    # Save
    file_key, sha256_hash = await backend.save_file(
        filename="income.pdf",
        content=content,
        application_id=app_id,
        content_type="application/pdf",
    )
    assert file_key.startswith(f"/uploads/{app_id}/")
    assert sha256_hash == hashlib.sha256(content).hexdigest()

    # Download URL (for local storage, returns the relative path)
    url = await backend.get_download_url(file_key)
    assert url == file_key

    # Read
    retrieved = await backend.read_file(file_key)
    assert retrieved == content

    # Delete
    deleted = await backend.delete_file(file_key)
    assert deleted is True

    # Read after delete should fail
    with pytest.raises(FileNotFoundError):
        await backend.read_file(file_key)


def test_s3_storage_backend_kwargs() -> None:
    """S3StorageBackend kwargs builder should correctly handle endpoint, credentials, and region."""
    backend = S3StorageBackend(
        bucket_name="my-bucket",
        region_name="ap-south-1",
        endpoint_url="http://localhost:9000",
        access_key_id="minioadmin",
        secret_access_key="minioadmin",
        kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test-key",
    )
    kwargs = backend._get_client_kwargs()
    assert kwargs["region_name"] == "ap-south-1"
    assert kwargs["endpoint_url"] == "http://localhost:9000"
    assert kwargs["aws_access_key_id"] == "minioadmin"
    assert kwargs["aws_secret_access_key"] == "minioadmin"


@pytest.mark.anyio
async def test_s3_storage_save_with_kms_and_presigned_url() -> None:
    """S3StorageBackend should attach SSE-KMS headers and issue pre-signed download URLs."""
    backend = S3StorageBackend(
        bucket_name="secure-bucket",
        region_name="ap-south-1",
        kms_key_arn="arn:aws:kms:ap-south-1:12345:key/secure-key",
    )

    mock_s3_client = AsyncMock()
    mock_s3_client.put_object = AsyncMock(return_value={"ETag": "test-etag"})
    mock_s3_client.generate_presigned_url = AsyncMock(
        return_value="https://secure-bucket.s3.ap-south-1.amazonaws.com/doc.pdf?signature=xyz"
    )

    mock_stream = AsyncMock()
    mock_stream.read = AsyncMock(return_value=b"decrypted s3 file content")
    mock_body_cm = AsyncMock()
    mock_body_cm.__aenter__.return_value = mock_stream
    mock_body_cm.__aexit__.return_value = None

    mock_s3_client.get_object = AsyncMock(return_value={"Body": mock_body_cm})
    mock_s3_client.delete_object = AsyncMock(return_value={"DeleteMarker": True})

    # Mock client context manager
    client_cm = AsyncMock()
    client_cm.__aenter__.return_value = mock_s3_client
    client_cm.__aexit__.return_value = None

    with patch.object(backend.session, "client", return_value=client_cm):
        content = b"Confidential income statement"
        app_id = "app-uuid-999"

        # 1. Save
        key, sha = await backend.save_file(
            filename="income_cert.pdf",
            content=content,
            application_id=app_id,
        )
        assert key.startswith(f"applications/{app_id}/")
        assert sha == hashlib.sha256(content).hexdigest()

        # Verify KMS header was passed
        mock_s3_client.put_object.assert_awaited_once()
        put_kwargs = mock_s3_client.put_object.call_args[1]
        assert put_kwargs["Bucket"] == "secure-bucket"
        assert put_kwargs["Key"] == key
        assert put_kwargs["ServerSideEncryption"] == "aws:kms"
        assert put_kwargs["SSEKMSKeyId"] == "arn:aws:kms:ap-south-1:12345:key/secure-key"

        # 2. Get Presigned URL
        presigned_url = await backend.get_download_url(key, expires_in=900)
        assert "signature=xyz" in presigned_url
        mock_s3_client.generate_presigned_url.assert_awaited_once_with(
            "get_object",
            Params={"Bucket": "secure-bucket", "Key": key},
            ExpiresIn=900,
        )

        # 3. Read
        read_bytes = await backend.read_file(key)
        assert read_bytes == b"decrypted s3 file content"

        # 4. Delete
        del_result = await backend.delete_file(key)
        assert del_result is True
        mock_s3_client.delete_object.assert_awaited_once_with(
            Bucket="secure-bucket",
            Key=key,
        )
