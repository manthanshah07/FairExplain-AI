"""
FairExplain AI — Application Router
=====================================
REST endpoints for submitting and inspecting applications.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponseData,
)
from app.schemas.common import BaseResponse
from app.services.application_service import ApplicationService

router = APIRouter(tags=["Application"])


@router.post(
    "",
    response_model=BaseResponse[ApplicationResponseData],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new scholarship & loan application",
)
async def create_application(
    request: ApplicationCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ApplicationResponseData]:
    """Submit applicant profile, academic record, and financial profile."""
    data = await ApplicationService.create_application(request, db)
    return BaseResponse[ApplicationResponseData](
        success=True,
        data=data,
        message="Application created successfully.",
    )


@router.get(
    "/{application_id}",
    response_model=BaseResponse[ApplicationResponseData],
    summary="Retrieve application profile by ID",
)
async def get_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ApplicationResponseData]:
    """Retrieve full application profile by UUID."""
    data = await ApplicationService.get_application(application_id, db)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found.",
        )
    return BaseResponse[ApplicationResponseData](
        success=True,
        data=data,
        message="Application retrieved successfully.",
    )
