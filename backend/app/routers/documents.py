"""
FairExplain AI — Documents Router
===================================
REST endpoints for secure document intake, OCR processing, and verification.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import get_storage_backend
from app.db.database import get_db
from app.models.uploaded_document import DocumentType, UploadedDocument
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
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Secure document intake with validation, SHA-256 deduplication, and automated OCR."""
    # 1. Validate MIME type
    content_type = file.content_type or "application/octet-stream"
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type}'. Allowed types: PDF, PNG, JPEG.",
        )

    # 2. Read bytes & validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum permissible size of 10 MB.",
        )

    # 3. Store file securely
    storage = get_storage_backend()
    file_url, sha256_hash = await storage.save_file(
        filename=file.filename or "upload.pdf",
        content=content,
        application_id=str(application_id),
    )

    # 4. OCR Extraction
    ocr_provider = PyPDFOCRProvider()
    ocr_result = await ocr_provider.extract_text(content, content_type)
    extracted_fields = DocumentKeyExtractor.extract_document_fields(
        doc_type=doc_type, text=ocr_result.raw_text
    )

    # 5. Save UploadedDocument record
    # Validate doc_type enum
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
    summary="List uploaded documents for an application",
)
async def list_documents(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[list[dict[str, Any]]]:
    """Retrieve all uploaded documents and their extracted metadata."""
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


@router.post(
    "/verify/{application_id}",
    response_model=BaseResponse[dict[str, Any]],
    summary="Trigger cross-verification of uploaded documents against reported profile",
)
async def verify_documents(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Cross-check extracted document numbers with application record."""
    result = await VerificationService.verify_application_documents(application_id, db)
    return BaseResponse[dict[str, Any]](
        success=True,
        data=result,
        message="Document verification check completed.",
    )
