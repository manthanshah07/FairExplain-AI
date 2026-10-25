"""
FairExplain AI — Models Package
=================================
Imports all ORM models so that:
1. Alembic autogenerate can discover every table.
2. SQLAlchemy relationship resolution works without circular import errors.

Always add new models to this file.
"""

from app.models.user import User, UserRole  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.application import Application, ApplicationStatus  # noqa: F401
from app.models.academic_record import AcademicRecord  # noqa: F401
from app.models.financial_profile import FinancialProfile  # noqa: F401
from app.models.uploaded_document import UploadedDocument, DocumentType  # noqa: F401
from app.models.scholarship_assessment import ScholarshipAssessment, AssessmentOutcome  # noqa: F401
from app.models.loan_assessment import LoanAssessment  # noqa: F401
from app.models.explanation_report import ExplanationReport, AssessmentType  # noqa: F401
from app.models.audit_log import AuditLogEntry, AuditEventType  # noqa: F401
from app.models.policy import ScholarshipPolicyModel, EligibilityCriterionModel  # noqa: F401
from app.models.award import AwardSpecificationModel, InstitutionalCapModel  # noqa: F401
from app.models.evaluation import (  # noqa: F401
    ScholarshipEvaluationModel,
    CriterionEvaluationSnapshotModel,
    TuitionAccountSummaryModel,
    AwardAllocationModel,
)

__all__ = [
    "User",
    "UserRole",
    "RefreshToken",
    "Application",
    "ApplicationStatus",
    "AcademicRecord",
    "FinancialProfile",
    "UploadedDocument",
    "DocumentType",
    "ScholarshipAssessment",
    "AssessmentOutcome",
    "LoanAssessment",
    "ExplanationReport",
    "AssessmentType",
    "AuditLogEntry",
    "AuditEventType",
    "ScholarshipPolicyModel",
    "EligibilityCriterionModel",
    "AwardSpecificationModel",
    "InstitutionalCapModel",
    "ScholarshipEvaluationModel",
    "CriterionEvaluationSnapshotModel",
    "TuitionAccountSummaryModel",
    "AwardAllocationModel",
]
