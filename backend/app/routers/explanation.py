"""
FairExplain AI — Explanation Router
=====================================
REST endpoints for generating and retrieving grounded plain-English explanations.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.common import BaseResponse
from app.services.explanation_service import ExplanationService

router = APIRouter(tags=["Explanation"])


class GenerateExplanationRequest(BaseModel):
    application_id: uuid.UUID


@router.post(
    "/generate",
    response_model=BaseResponse[dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Generate a grounded explainable AI report for an application",
)
async def generate_explanation(
    request: GenerateExplanationRequest,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """
    Translates pre-computed deterministic domain evaluations into objective,
    plain-English reasoning per PROMPTS.md.
    """
    data = await ExplanationService.generate_explanation(request.application_id, db)
    return BaseResponse[dict[str, Any]](
        success=True,
        data=data,
        message="Explanation generated and audited successfully.",
    )


@router.get(
    "/{application_id}",
    response_model=BaseResponse[dict[str, Any]],
    summary="Retrieve previously generated explanation report",
)
async def get_explanation(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Fetch stored explanation report by application ID."""
    data = await ExplanationService.get_explanation(application_id, db)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No explanation found for application {application_id}.",
        )
    return BaseResponse[dict[str, Any]](
        success=True,
        data=data,
        message="Explanation retrieved successfully.",
    )
