"""
FairExplain AI — Schemas Package
=================================
"""

from app.schemas.common import BaseResponse, ErrorResponse, PaginatedData
from app.schemas.application import (
    AcademicRecordInput,
    FinancialProfileInput,
    ApplicationCreateRequest,
    ApplicationResponseData,
)
from app.schemas.scholarship import (
    AwardInputDTO,
    ScholarshipEvaluateRequest,
    CriterionEvaluationDTO,
    AwardAllocationDTO,
    TuitionAccountingDTO,
    ScholarshipEvaluateResponseData,
)
from app.schemas.loan import LoanAssessRequest, LoanAssessResponseData
from app.schemas.admin import (
    ReviewQueueItem,
    ReviewQueueResponse,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    AdminAnalyticsResponse,
)

__all__ = [
    "BaseResponse",
    "ErrorResponse",
    "PaginatedData",
    "AcademicRecordInput",
    "FinancialProfileInput",
    "ApplicationCreateRequest",
    "ApplicationResponseData",
    "AwardInputDTO",
    "ScholarshipEvaluateRequest",
    "CriterionEvaluationDTO",
    "AwardAllocationDTO",
    "TuitionAccountingDTO",
    "ScholarshipEvaluateResponseData",
    "LoanAssessRequest",
    "LoanAssessResponseData",
    "ReviewQueueItem",
    "ReviewQueueResponse",
    "ReviewDecisionRequest",
    "ReviewDecisionResponse",
    "AdminAnalyticsResponse",
]
