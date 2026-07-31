"""
FairExplain AI — Models Package
=================================
Imports all ORM models so that:
1. Alembic autogenerate can discover every table.
2. SQLAlchemy relationship resolution works without circular import errors.

Always add new models to this file.
"""

from app.models.user import User, UserRole  # noqa: F401
from app.models.application import Application, ApplicationStatus  # noqa: F401
from app.models.academic_record import AcademicRecord  # noqa: F401
from app.models.financial_profile import FinancialProfile  # noqa: F401
from app.models.uploaded_document import UploadedDocument, DocumentType  # noqa: F401
from app.models.scholarship_assessment import ScholarshipAssessment, AssessmentOutcome  # noqa: F401
from app.models.loan_assessment import LoanAssessment  # noqa: F401
from app.models.explanation_report import ExplanationReport, AssessmentType  # noqa: F401
from app.models.audit_log import AuditLogEntry, AuditEventType  # noqa: F401

__all__ = [
    "User",
    "UserRole",
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
]
