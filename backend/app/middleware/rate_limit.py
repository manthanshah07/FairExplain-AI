"""
FairExplain AI — Rate Limiting Middleware
===========================================
SlowAPI rate limiting configuration to protect endpoints from abuse
and denial-of-service, especially for LLM explanations and cryptographic PDF generation.
"""

from __future__ import annotations

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

# Create centralized rate limiter keyed by client IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    headers_enabled=True,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Return JSON response conforming to the platform error format when rate limit is exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Too many requests. Rate limit exceeded: {exc.detail}",
                "details": None,
            },
        },
    )
