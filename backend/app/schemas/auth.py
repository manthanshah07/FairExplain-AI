"""
FairExplain AI — Authentication Schemas
=========================================
Request and response models for user registration, login, and token exchange.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class RegisterRequest(BaseModel):
    """Payload for creating a new applicant account. Public registration always creates a student account."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=255, description="Full name of applicant")
    email: str = Field(..., pattern=EMAIL_REGEX, description="Institutional email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure user password")


class AdminCreateUserRequest(BaseModel):
    """Payload for administrative provisioning of privileged accounts (reviewer, admin, etc.)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=255, description="Full name of staff or officer")
    email: str = Field(..., pattern=EMAIL_REGEX, description="Institutional email address")
    password: str = Field(..., min_length=8, max_length=128, description="Initial secure password")
    role: UserRole = Field(..., description="Assigned institutional role")


class LoginRequest(BaseModel):
    """Payload for authenticating with email and password."""

    email: str = Field(..., pattern=EMAIL_REGEX, description="User's registered email")
    password: str = Field(..., min_length=1, description="User password")


class UserResponse(BaseModel):
    """Sanitized public profile of a user account."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Successful authentication response payload."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(description="Access token expiration in seconds")
    user: UserResponse
