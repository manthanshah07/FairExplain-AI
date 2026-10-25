"""
FairExplain AI — Core Security & Cryptography Engine
======================================================
Cryptographic operations:
  1. Direct bcrypt password hashing and verification.
  2. RFC 7519 JWT creation and verification (access and refresh tokens).
  3. Email domain whitelist verification.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config.settings import get_settings
class AuthenticationError(Exception):
    """Raised when authentication credentials or tokens fail verification."""

    def __init__(
        self,
        message: str = "Could not validate credentials",
        code: str = "AUTHENTICATION_FAILED",
        detail: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.detail = detail


class TokenExpiredError(AuthenticationError):
    """Raised when an access or refresh token has expired."""

    def __init__(self, message: str = "Token has expired") -> None:
        super().__init__(message=message, code="TOKEN_EXPIRED")


class InvalidTokenError(AuthenticationError):
    """Raised when a token signature or claims are invalid."""

    def __init__(self, message: str = "Invalid token claims or signature") -> None:
        super().__init__(message=message, code="TOKEN_INVALID")


# ---------------------------------------------------------------------------
# Password Management (Direct bcrypt work factor 12)
# ---------------------------------------------------------------------------


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using direct bcrypt with cost factor 12.
    Ensures safe byte encoding and returns a UTF-8 string for DB storage.
    """
    if not plain_password:
        raise ValueError("Password cannot be empty.")
    # Direct bcrypt to avoid passlib 1.7.4 / bcrypt 4.x __about__ attribute bug
    pwd_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    Safe against timing attacks.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Domain Whitelisting
# ---------------------------------------------------------------------------


def is_email_domain_allowed(email: str, allowed_domains: list[str]) -> bool:
    """
    Check if an email address belongs to one of the configured institutional domains.
    If allowed_domains is empty, all valid email domains are permitted.
    """
    if not allowed_domains:
        return True
    if "@" not in email:
        return False
    domain = email.split("@")[-1].strip().lower()
    for allowed in allowed_domains:
        allowed_clean = allowed.strip().lower()
        if allowed_clean.startswith("*."):
            suffix = allowed_clean[1:]  # e.g. .ac.in
            if domain.endswith(suffix):
                return True
        elif domain == allowed_clean:
            return True
    return False


# ---------------------------------------------------------------------------
# JWT Token Lifecycle
# ---------------------------------------------------------------------------


def create_access_token(
    subject: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generate an RFC 7519 JWT access token with 15-minute default TTL.
    Carries subject (user_id), email, role, jti, type='access'.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    jti = uuid.uuid4().hex
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "type": "access",
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    subject: str,
    family_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> tuple[str, str, datetime]:
    """
    Generate a cryptographically random refresh token.
    Returns (token_string, jti, expires_at).
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    jti = uuid.uuid4().hex
    payload = {
        "sub": subject,
        "type": "refresh",
        "jti": jti,
        "family_id": family_id or uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token_str = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token_str, jti, expire


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """
    Decode and validate a JWT token's signature, algorithm, expiration, and type.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired.") from e
    except JWTError as e:
        raise InvalidTokenError(f"Could not validate token: {e}") from e

    token_type = payload.get("type")
    if token_type != expected_type:
        raise InvalidTokenError(f"Expected token type '{expected_type}', got '{token_type}'.")

    if not payload.get("sub"):
        raise InvalidTokenError("Token payload missing subject ('sub').")

    return payload
