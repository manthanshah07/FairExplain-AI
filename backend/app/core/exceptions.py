"""
FairExplain AI — Global Exception Handlers
============================================
Registers application-level exception handlers on the FastAPI app.

All responses follow the standard envelope:
    {
        "success": false,
        "data": null,
        "message": "...",
        "errors": [...]
    }

Internal stack traces are NEVER exposed in production.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger
from app.schemas.common import ErrorResponse

logger = get_logger(__name__)


def _error_response(
    message: str,
    errors: list[str] | None = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> JSONResponse:
    """Build a standard error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            success=False,
            data=None,
            message=message,
            errors=errors or [],
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic / FastAPI request validation failures."""
        errors = [
            f"{' → '.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        ]
        logger.warning(
            "request_validation_failed",
            path=str(request.url),
            errors=errors,
        )
        return _error_response(
            message="Request validation failed.",
            errors=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle database-level errors without leaking internals."""
        logger.error(
            "database_error",
            path=str(request.url),
            error=str(exc),
        )
        return _error_response(
            message="A database error occurred. Please try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request, exc: ValueError
    ) -> JSONResponse:
        """Handle business-logic value errors surfaced from services."""
        logger.warning("value_error", path=str(request.url), error=str(exc))
        return _error_response(
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        request: Request, exc: PermissionError
    ) -> JSONResponse:
        """Handle authorisation failures from services."""
        logger.warning("permission_denied", path=str(request.url))
        return _error_response(
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all for any unhandled exception."""
        logger.exception("unhandled_exception", path=str(request.url), error=str(exc))
        return _error_response(
            message="An unexpected error occurred. Please contact support.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
