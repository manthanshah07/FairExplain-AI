"""
FairExplain AI — Request Logging Middleware
============================================
Logs every incoming request and outgoing response at INFO level with:
- method, path, status_code, duration_ms
- request_id (generated per-request for tracing)

Sensitive headers (Authorization, Cookie) are redacted.
"""

from __future__ import annotations

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)

_REDACTED_HEADERS = frozenset({"authorization", "cookie", "x-api-key"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that logs request/response metadata for every call."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        # Bind request_id to the structlog context so it appears in all
        # log records emitted during this request.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info(
            "request_received",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) or None,
            client=request.client.host if request.client else None,
        )

        response: Response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-Id"] = request_id

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        structlog.contextvars.clear_contextvars()
        return response
