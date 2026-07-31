"""
FairExplain AI — API v1 Router Registry
=========================================
Central registry that assembles all versioned API routes under `/api/v1`.

To add a new router:
1. Create `app/routers/<feature>.py`
2. Import its `router` here and call `api_router.include_router(...)`.

This keeps `main.py` clean and makes the full route list discoverable
in a single file.
"""

from __future__ import annotations

from fastapi import APIRouter

# --- Feature routers (uncomment as implemented in subsequent phases) ---
# from app.routers.auth import router as auth_router
# from app.routers.applications import router as applications_router
# from app.routers.documents import router as documents_router
# from app.routers.scholarship import router as scholarship_router
# from app.routers.loan import router as loan_router
# from app.routers.explanation import router as explanation_router
# from app.routers.report import router as report_router

api_router = APIRouter(prefix="/api/v1")

# --- Register feature routers here as phases progress ---
# api_router.include_router(auth_router, prefix="/auth")
# api_router.include_router(applications_router, prefix="/application")
# api_router.include_router(documents_router, prefix="/documents")
# api_router.include_router(scholarship_router, prefix="/scholarship")
# api_router.include_router(loan_router, prefix="/loan")
# api_router.include_router(explanation_router, prefix="/explanation")
# api_router.include_router(report_router, prefix="/report")
