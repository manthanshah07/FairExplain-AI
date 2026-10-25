"""
FairExplain AI — Admin Schemas
================================
Pydantic schemas for review queue, reviewer determinations, and analytics.
"""

from __future__ import annotations

import uuid
from typing import Any, Literal
from pydantic import BaseModel, Field


class ReviewQueueItem(BaseModel):
    application_id: uuid.UUID
    applicant_name: str
    applicant_email: str
    submission_date: str
    status: str
    program_id: str | None = None
    flags: list[str] = Field(default_factory=list)
    priority: Literal["high", "medium", "low"] = "low"


class ReviewQueueResponse(BaseModel):
    items: list[ReviewQueueItem]
    total: int
    page: int
    page_size: int


class ReviewDecisionRequest(BaseModel):
    decision: Literal["approve", "override", "reject", "request_evidence"]
    rationale: str = Field(..., min_length=3, description="Mandatory human justification")
    reviewer_id: str = Field(default="admin-reviewer")
    override_details: dict[str, Any] | None = None


class ReviewDecisionResponse(BaseModel):
    application_id: uuid.UUID
    status: str
    decision: str
    rationale: str
    audit_log_id: uuid.UUID


class AdminAnalyticsResponse(BaseModel):
    total_applications: int
    pending_review_count: int
    approved_count: int
    rejected_count: int
    eligibility_rate_percent: float
    average_tuition_reduction: float
    fairness_flag_incidence_rate: float
    average_turnaround_hours: float
    status_distribution: dict[str, int]
    recent_activity: list[dict[str, Any]]
