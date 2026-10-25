"""
FairExplain AI — Admin Review & Analytics Router
==================================================
REST endpoints for human review queue, override determinations, and institutional metrics.
Protected by Role-Based Access Control (RBAC).
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminAnalyticsResponse,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewQueueResponse,
)
from app.schemas.auth import AdminCreateUserRequest, UserResponse
from app.schemas.common import BaseResponse
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService

router = APIRouter(tags=["Admin"])

# Require reviewer or admin role across general review routes
_reviewer_guard = require_role([
    UserRole.reviewer,
    UserRole.admin,
    UserRole.university,
])

# Strictly require admin role for sensitive user provisioning
_admin_guard = require_role([UserRole.admin])


@router.get(
    "/review-queue",
    response_model=BaseResponse[ReviewQueueResponse],
    summary="List applications pending review or filtered by status",
)
async def get_review_queue(
    status: str | None = Query(default=None, description="Filter by status (all, needs_review, submitted, etc.)"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(_reviewer_guard),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ReviewQueueResponse]:
    """Retrieve prioritized queue of applications awaiting human inspection."""
    data = await AdminService.get_review_queue(
        db=db,
        status_filter=status,
        page=page,
        page_size=page_size,
    )
    return BaseResponse[ReviewQueueResponse](
        success=True,
        data=data,
        message="Review queue retrieved successfully.",
    )


@router.get(
    "/application/{application_id}/review-context",
    response_model=BaseResponse[dict[str, Any]],
    summary="Get complete assessment dossier for an application",
)
async def get_review_context(
    application_id: uuid.UUID,
    current_user: User = Depends(_reviewer_guard),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Retrieve consolidated applicant dossier, document verification flags, evaluations, and audit trail."""
    data = await AdminService.get_review_context(
        application_id=application_id,
        db=db,
    )
    return BaseResponse[dict[str, Any]](
        success=True,
        data=data,
        message="Review context retrieved successfully.",
    )


@router.post(
    "/application/{application_id}/decision",
    response_model=BaseResponse[ReviewDecisionResponse],
    summary="Record reviewer approval, override, rejection, or evidence request",
)
async def record_decision(
    application_id: uuid.UUID,
    request: ReviewDecisionRequest,
    current_user: User = Depends(_reviewer_guard),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ReviewDecisionResponse]:
    """
    Record human determination with mandatory rationale and create immutable audit log entry.
    Reviewer identity is derived strictly from the authenticated principal.
    """
    data = await AdminService.record_decision(
        application_id=application_id,
        request=request,
        db=db,
        reviewer=current_user,
    )
    return BaseResponse[ReviewDecisionResponse](
        success=True,
        data=data,
        message=f"Determination '{request.decision}' recorded successfully.",
    )


@router.get(
    "/analytics",
    response_model=BaseResponse[AdminAnalyticsResponse],
    summary="Retrieve real-time institutional analytics and cohort metrics",
)
async def get_admin_analytics(
    current_user: User = Depends(_reviewer_guard),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AdminAnalyticsResponse]:
    """Retrieve institutional volume, eligibility rate, waiver aggregates, and fairness flag rates."""
    data = await AdminService.get_analytics(db=db)
    return BaseResponse[AdminAnalyticsResponse](
        success=True,
        data=data,
        message="Institutional analytics retrieved successfully.",
    )


@router.post(
    "/users",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Provision a privileged user account (reviewer, university, admin)",
)
async def admin_create_user(
    request: AdminCreateUserRequest,
    current_user: User = Depends(_admin_guard),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserResponse]:
    """Provision a privileged staff account. Restricted strictly to administrators."""
    user = await AuthService.admin_create_user(req=request, db=db, admin=current_user)
    return BaseResponse[UserResponse](
        success=True,
        data=user,
        message=f"User account with role '{request.role.value}' provisioned successfully.",
    )
