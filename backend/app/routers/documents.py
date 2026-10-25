"""
FairExplain AI — Documents Router
===================================
REST endpoints for secure document intake, OCR processing, and verification.
Protected by BOLA authorization and private S3-compatible storage with pre-signed URLs.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.core.storage import get_storage_backend
from app.db.database import get_db
from app.models.application import Application
from app.models.uploaded_document import DocumentType, UploadedDocument
from app.models.user import User, UserRole
from app.schemas.common import BaseResponse
from app.services.ocr.extractor import DocumentKeyExtractor
from app.services.ocr.pypdf_provider import PyPDFOCRProvider
from app.services.verification_service import VerificationService

router = APIRouter(tags=["Documents"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "text/plain",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def _assert_application_access(
    application_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> None:
    """Ensure user is the owner of the application or an authorized reviewer/admin."""
    user_role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    if user_role_str in [UserRole.reviewer.value, UserRole.admin.value, UserRole.university.value]:
        return

    res = await db.execute(select(Application.user_id).where(Application.id == application_id))
    owner_id = res.scalar_one_or_none()
    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found.",
        )
    if owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to requested application documents.",
        )


@router.post(
    "/upload",
    response_model=BaseResponse[dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a verification document with OCR processing",
)
async def upload_document(
    application_id: uuid.UUID = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Secure document intake with BOLA validation, SHA-256 deduplication, and automated OCR."""
    # 1. Enforce BOLA access control
    await _assert_application_access(application_id, current_user, db)

    # 2. Validate MIME type
    content_type = file.content_type or "application/octet-stream"
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type}'. Allowed types: PDF, PNG, JPEG.",
        )

    # 3. Read bytes & validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum permissible size of 10 MB.",
        )

    # 4. Store file securely via pluggable storage backend (S3 / MinIO)
    storage = get_storage_backend()
    file_url, sha256_hash = await storage.save_file(
        filename=file.filename or "upload.pdf",
        content=content,
        application_id=str(application_id),
        content_type=content_type,
    )

    # 5. OCR Extraction
    ocr_provider = PyPDFOCRProvider()
    ocr_result = await ocr_provider.extract_text(content, content_type)
    extracted_fields = DocumentKeyExtractor.extract_document_fields(
        doc_type=doc_type, text=ocr_result.raw_text
    )

    # 6. Save UploadedDocument record
    try:
        norm_doc_type = DocumentType(doc_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid doc_type '{doc_type}'. Expected: marksheet, income_proof, id_proof.",
        )

    doc_record = UploadedDocument(
        application_id=application_id,
        doc_type=norm_doc_type,
        file_url=file_url,
        ocr_extracted_data=extracted_fields,
        mismatch_flag=False,
    )
    db.add(doc_record)
    await db.commit()
    await db.refresh(doc_record)

    return BaseResponse[dict[str, Any]](
        success=True,
        data={
            "document_id": str(doc_record.id),
            "application_id": str(application_id),
            "doc_type": norm_doc_type.value,
            "file_url": file_url,
            "sha256": sha256_hash,
            "extracted_fields": extracted_fields,
            "ocr_confidence": extracted_fields.get("confidence", ocr_result.confidence),
        },
        message="Document uploaded and processed successfully.",
    )


@router.get(
    "/application/{application_id}",
    response_model=BaseResponse[list[dict[str, Any]]],
    summary="List uploaded documents for an application with BOLA protection",
)
async def list_documents(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[list[dict[str, Any]]]:
    """Retrieve all uploaded documents and metadata for an authorized application."""
    await _assert_application_access(application_id, current_user, db)

    stmt = (
        select(UploadedDocument)
        .where(UploadedDocument.application_id == application_id)
        .order_by(UploadedDocument.created_at.desc())
    )
    res = await db.execute(stmt)
    docs = res.scalars().all()

    data = [
        {
            "id": str(d.id),
            "doc_type": d.doc_type.value if hasattr(d.doc_type, "value") else str(d.doc_type),
            "file_url": d.file_url,
            "mismatch_flag": d.mismatch_flag,
            "ocr_extracted_data": d.ocr_extracted_data,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]
    return BaseResponse[list[dict[str, Any]]](
        success=True,
        data=data,
        message="Documents retrieved successfully.",
    )


@router.get(
    "/{document_id}/download-url",
    response_model=BaseResponse[dict[str, Any]],
    summary="Generate time-limited secure pre-signed download URL for a document",
)
async def get_document_download_url(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Generate 15-minute secure pre-signed download URL after verifying document ownership."""
    stmt = select(UploadedDocument).where(UploadedDocument.id == document_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found.",
        )

    await _assert_application_access(doc.application_id, current_user, db)

    storage = get_storage_backend()
    download_url = await storage.get_download_url(doc.file_url, expires_in=900)

    return BaseResponse[dict[str, Any]](
        success=True,
        data={
            "document_id": str(doc.id),
            "download_url": download_url,
            "expires_in": 900,
        },
        message="Pre-signed download URL generated.",
    )


@router.post(
    "/verify/{application_id}",
    response_model=BaseResponse[dict[str, Any]],
    summary="Trigger cross-verification of uploaded documents against reported profile",
)
async def verify_documents(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Cross-check extracted document numbers with application record with access protection."""
    await _assert_application_access(application_id, current_user, db)
    result = await VerificationService.verify_application_documents(application_id, db)
    return BaseResponse[dict[str, Any]](
        success=True,
        data=result,
        message="Document verification check completed.",
    )
