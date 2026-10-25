"""
FairExplain AI — Unit Tests for Security and Cryptography
===========================================================
Validates:
  1. Bcrypt password hashing and verification.
  2. JWT access token and refresh token creation and claims.
  3. Token expiration and type enforcement.
  4. Email domain whitelisting.
"""

from __future__ import annotations

from datetime import timedelta
import pytest

from app.core.security import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_email_domain_allowed,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    raw_pwd = "CorrectHorseBatteryStaple123!"
    hashed = hash_password(raw_pwd)

    assert hashed != raw_pwd
    assert hashed.startswith("$2b$12$")
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_hashing_empty_fails() -> None:
    with pytest.raises(ValueError):
        hash_password("")


def test_access_token_creation_and_decoding() -> None:
    user_id = "user-123e4567-e89b-12d3-a456-426614174000"
    email = "sarah@nitk.edu.in"
    role = "reviewer"

    token = create_access_token(subject=user_id, email=email, role=role)
    payload = decode_token(token, expected_type="access")

    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert payload["role"] == role
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "jti" in payload


def test_refresh_token_creation_and_decoding() -> None:
    user_id = "user-123e4567-e89b-12d3-a456-426614174000"

    token_str, jti, expire = create_refresh_token(subject=user_id)
    payload = decode_token(token_str, expected_type="refresh")

    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_token_type_mismatch_fails() -> None:
    token = create_access_token(subject="u1", email="test@nitk.edu.in", role="student")
    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="refresh")


def test_expired_token_fails() -> None:
    # Token expired 1 minute ago
    token = create_access_token(
        subject="u1",
        email="test@nitk.edu.in",
        role="student",
        expires_delta=timedelta(minutes=-1),
    )
    with pytest.raises(TokenExpiredError):
        decode_token(token, expected_type="access")


def test_tampered_token_fails() -> None:
    token = create_access_token(subject="u1", email="test@nitk.edu.in", role="student")
    tampered = token[:-4] + "abcd"
    with pytest.raises(InvalidTokenError):
        decode_token(tampered, expected_type="access")


def test_email_domain_whitelist() -> None:
    allowed = ["nitk.edu.in", "*.ac.in"]

    assert is_email_domain_allowed("priya@nitk.edu.in", allowed) is True
    assert is_email_domain_allowed("student@dept.iitb.ac.in", allowed) is True
    assert is_email_domain_allowed("attacker@gmail.com", allowed) is False
    assert is_email_domain_allowed("hacker@malicious.com", allowed) is False

    # Empty whitelist allows all
    assert is_email_domain_allowed("anyone@example.com", []) is True
