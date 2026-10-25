"""
FairExplain AI — Application Router
=====================================
REST endpoints for submitting and inspecting applications with BOLA protection.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User, UserRole
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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ApplicationResponseData]:
    """Submit applicant profile, academic record, and financial profile tied to authenticated principal."""
    data = await ApplicationService.create_application(request, db, current_user=current_user)
    return BaseResponse[ApplicationResponseData](
        success=True,
        data=data,
        message="Application created successfully.",
    )


@router.get(
    "/{application_id}",
    response_model=BaseResponse[ApplicationResponseData],
    summary="Retrieve application profile by ID with BOLA protection",
)
async def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ApplicationResponseData]:
    """
    Retrieve full application profile by UUID.
    Enforces object-level authorization (BOLA prevention):
    Students may only view their own applications; reviewers/admins may view any.
    """
    data = await ApplicationService.get_application(application_id, db)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found.",
        )

    # BOLA ownership assertion
    user_role_str = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else str(current_user.role)
    )
    is_privileged = user_role_str in [
        UserRole.reviewer.value,
        UserRole.admin.value,
        UserRole.university.value,
    ]

    if data.user_id != current_user.id and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to requested application.",
        )

    return BaseResponse[ApplicationResponseData](
        success=True,
        data=data,
        message="Application retrieved successfully.",
    )
