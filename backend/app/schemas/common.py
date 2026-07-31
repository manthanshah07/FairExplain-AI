"""
FairExplain AI — Common Pydantic Schemas
==========================================
Shared response envelope and base schemas used across all endpoints.

Every API response follows the standard envelope defined in PROJECTCONTEXT.md:
    {
        "success": bool,
        "data":    <payload> | null,
        "message": str,
        "errors":  list[str]
    }
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    Standard API response envelope.

    All endpoints return this structure — never raw payloads — so the
    frontend can rely on a consistent contract.
    """

    success: bool
    data: T | None = None
    message: str = ""
    errors: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Response envelope for error cases (no generic payload needed)."""

    success: bool = False
    data: None = None
    message: str
    errors: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PaginatedData(BaseModel, Generic[T]):
    """Wrapper for paginated list responses."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    """Query-parameter schema for paginated list endpoints."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
