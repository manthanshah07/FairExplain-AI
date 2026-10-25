"""
FairExplain AI — API v1 Router Registry
=========================================
Central registry that assembles all versioned API routes under `/api/v1`.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.routers.applications import router as applications_router
from app.routers.scholarship import router as scholarship_router
from app.routers.loan import router as loan_router
from app.routers.documents import router as documents_router
from app.routers.explanation import router as explanation_router
from app.routers.fairness import router as fairness_router

api_router = APIRouter(prefix="/api/v1")

# Feature routers
api_router.include_router(applications_router, prefix="/application")
api_router.include_router(scholarship_router, prefix="/scholarship")
api_router.include_router(loan_router, prefix="/loan")
api_router.include_router(documents_router, prefix="/documents")
api_router.include_router(explanation_router, prefix="/explanation")
api_router.include_router(fairness_router, prefix="/admin/fairness")
