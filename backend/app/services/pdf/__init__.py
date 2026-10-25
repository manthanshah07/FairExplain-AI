"""
FairExplain AI — PDF Reporting Services
=========================================
"""

from app.services.pdf.hasher import compute_audit_hash
from app.services.pdf.report_generator import generate_assessment_pdf

__all__ = [
    "compute_audit_hash",
    "generate_assessment_pdf",
]
