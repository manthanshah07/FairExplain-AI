"""
FairExplain AI — Admin Review & Analytics Router
==================================================
REST endpoints for human review queue, override determinations, and institutional metrics.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.admin import (
    AdminAnalyticsResponse,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewQueueResponse,
)
from app.schemas.common import BaseResponse
from app.services.admin_service import AdminService

router = APIRouter(tags=["Admin"])


@router.get(
    "/review-queue",
    response_model=BaseResponse[ReviewQueueResponse],
    summary="List applications pending review or filtered by status",
)
async def get_review_queue(
    status: str | None = Query(default=None, description="Filter by status (all, needs_review, submitted, etc.)"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
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
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ReviewDecisionResponse]:
    """Record human determination with mandatory rationale and create immutable audit log entry."""
    data = await AdminService.record_decision(
        application_id=application_id,
        request=request,
        db=db,
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
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AdminAnalyticsResponse]:
    """Retrieve institutional volume, eligibility rate, waiver aggregates, and fairness flag rates."""
    data = await AdminService.get_analytics(db=db)
    return BaseResponse[AdminAnalyticsResponse](
        success=True,
        data=data,
        message="Institutional analytics retrieved successfully.",
    )
