"""
FairExplain AI — Integration Tests for Authentication & Session Lifecycle
===========================================================================
Tests end-to-end HTTP requests against `/api/v1/auth/register`,
`/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/logout`, and `/api/v1/auth/me`.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient

from app.models.user import UserRole


@pytest.mark.anyio
async def test_register_success(client: AsyncClient) -> None:
    """Test standard student account registration."""
    email = f"student_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    payload = {
        "name": "Priya Sharma",
        "email": email,
        "password": "StrongPassword123!",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == email.lower()
    assert body["data"]["role"] == "student"
    assert "password" not in body["data"]


@pytest.mark.anyio
async def test_register_duplicate_email_fails(client: AsyncClient) -> None:
    """Test that duplicate registrations return HTTP 409 Conflict."""
    email = f"dup_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    payload = {
        "name": "User One",
        "email": email,
        "password": "Password123!",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409


@pytest.mark.anyio
async def test_login_success_and_cookie_attributes(client: AsyncClient) -> None:
    """Test login issues access token and sets secure HttpOnly refresh cookie."""
    email = f"login_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "CorrectPassword123!"

    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Login User", "email": email, "password": password},
    )

    # Login
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["expires_in"] == 900  # 15 minutes

    # Inspect Set-Cookie header
    set_cookie = resp.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Path=/api/v1/auth" in set_cookie


@pytest.mark.anyio
async def test_login_invalid_password_returns_401(client: AsyncClient) -> None:
    """Test that invalid password returns generic 401 Unauthorized."""
    email = f"login_fail_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "CorrectPassword123!"

    await client.post(
        "/api/v1/auth/register",
        json={"name": "User", "email": email, "password": password},
    )

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword999!"},
    )
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


@pytest.mark.anyio
async def test_refresh_token_rotation_and_replay_detection(client: AsyncClient) -> None:
    """
    Test Refresh Token Rotation (RTR):
    1. Login returns Refresh Token A.
    2. Refresh with Token A returns new Token B and invalidates A.
    3. Replaying Token A triggers Token Family Revocation and returns 401.
    """
    email = f"rtr_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "Password123!"

    await client.post(
        "/api/v1/auth/register",
        json={"name": "RTR User", "email": email, "password": password},
    )

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    cookie_header = login_resp.headers["set-cookie"]
    # Extract refresh_token cookie value
    raw_token_a = cookie_header.split("refresh_token=")[1].split(";")[0]

    # 1. First refresh with Token A -> Success, returns Token B
    refresh_resp1 = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": raw_token_a},
    )
    assert refresh_resp1.status_code == 200
    token_b_cookie = refresh_resp1.headers["set-cookie"]
    raw_token_b = token_b_cookie.split("refresh_token=")[1].split(";")[0]
    assert raw_token_b != raw_token_a

    # 2. REPLAY ATTACK: Attacker attempts to reuse Token A -> Must be detected and rejected!
    replay_resp = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": raw_token_a},
    )
    assert replay_resp.status_code == 401
    assert "Compromised refresh token replayed" in replay_resp.json()["detail"]

    # 3. Verify that Token B was also revoked as part of the family revocation!
    refresh_resp2 = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": raw_token_b},
    )
    assert refresh_resp2.status_code == 401


@pytest.mark.anyio
async def test_logout_invalidates_session(client: AsyncClient) -> None:
    """Test logout clears cookie and invalidates the active refresh token."""
    email = f"logout_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "Password123!"

    await client.post(
        "/api/v1/auth/register",
        json={"name": "Logout User", "email": email, "password": password},
    )

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    raw_token = login_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

    # Logout
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        cookies={"refresh_token": raw_token},
    )
    assert logout_resp.status_code == 200
    assert "refresh_token=" in logout_resp.headers.get("set-cookie", "")

    # Attempting to refresh after logout returns 401
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": raw_token},
    )
    assert refresh_resp.status_code == 401


@pytest.mark.anyio
async def test_get_me_endpoint(client: AsyncClient) -> None:
    """Test /api/v1/auth/me returns profile when authenticated and 401 when missing."""
    email = f"me_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "Password123!"

    await client.post(
        "/api/v1/auth/register",
        json={"name": "Me User", "email": email, "password": password},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    access_token = login_resp.json()["data"]["access_token"]

    # Unauthenticated call -> 401
    unauth_resp = await client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401

    # Authenticated call -> 200
    auth_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert auth_resp.status_code == 200
    assert auth_resp.json()["data"]["email"] == email.lower()
    assert auth_resp.json()["data"]["role"] == "student"


@pytest.mark.anyio
async def test_public_registration_rejects_client_supplied_role(client: AsyncClient) -> None:
    """SEC-01: Public registration must reject client-supplied role fields and prevent privilege escalation."""
    email = f"attacker_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    # Attempting to assign admin role
    payload_admin = {
        "name": "Malicious Actor",
        "email": email,
        "password": "Password123!",
        "role": "admin",
    }
    resp = await client.post("/api/v1/auth/register", json=payload_admin)
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert any("role" in err.lower() for err in body.get("errors", []))

    # Attempting to assign reviewer role
    payload_reviewer = {
        "name": "Malicious Actor",
        "email": f"attacker2_{uuid.uuid4().hex[:8]}@nitk.edu.in",
        "password": "Password123!",
        "role": "reviewer",
    }
    resp2 = await client.post("/api/v1/auth/register", json=payload_reviewer)
    assert resp2.status_code == 422


@pytest.mark.anyio
async def test_privileged_user_provisioning_access_controls(
    client: AsyncClient,
    student_auth_headers: dict[str, str],
    admin_auth_headers: dict[str, str],
) -> None:
    """SEC-01: Only authenticated administrators can provision reviewer/admin accounts."""
    email = f"reviewer_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    payload = {
        "name": "Officer David",
        "email": email,
        "password": "OfficerPassword123!",
        "role": "reviewer",
    }

    # 1. Unauthenticated request -> 401
    unauth_resp = await client.post("/api/v1/admin/users", json=payload)
    assert unauth_resp.status_code == 401

    # 2. Student caller -> 403 Forbidden
    student_resp = await client.post(
        "/api/v1/admin/users",
        json=payload,
        headers=student_auth_headers,
    )
    assert student_resp.status_code == 403

    # 3. Authorized Administrator -> 201 Created
    admin_resp = await client.post(
        "/api/v1/admin/users",
        json=payload,
        headers=admin_auth_headers,
    )
    assert admin_resp.status_code == 201
    data = admin_resp.json()["data"]
    assert data["email"] == email.lower()
    assert data["role"] == "reviewer"

    # Verify newly provisioned reviewer can log in and receives reviewer token
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "OfficerPassword123!"},
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["data"]["user"]["role"] == "reviewer"


@pytest.mark.anyio
async def test_disabled_public_registration_returns_403(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SEC-05: When public registration is disabled (default in production), /register returns 403."""
    from app.config.settings import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "enable_public_registration", False)

    email = f"blocked_reg_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    resp = await client.post(
        "/api/v1/auth/register",
        json={"name": "Blocked User", "email": email, "password": "Password123!"},
    )
    assert resp.status_code == 403
    assert "Public self-service registration is disabled" in resp.json().get("detail", "")


@pytest.mark.anyio
async def test_registration_creates_unverified_account_in_database(client: AsyncClient) -> None:
    """SEC-05: Public registration must create an unverified account (is_verified=False) in PostgreSQL."""
    from sqlalchemy import select
    from app.db.database import AsyncSessionFactory
    from app.models.user import User

    email = f"unverified_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    resp = await client.post(
        "/api/v1/auth/register",
        json={"name": "Unverified User", "email": email, "password": "Password123!"},
    )
    assert resp.status_code == 201

    async with AsyncSessionFactory() as session:
        user_res = await session.execute(select(User).where(User.email == email.lower()))
        user = user_res.scalar_one()
        assert user.is_verified is False, "Newly registered user must not be marked verified unconditionally!"


@pytest.mark.anyio
async def test_email_verification_policy_enforcement(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SEC-05: When require_email_verification=True, unverified users are blocked at login and protected routes."""
    from app.config.settings import get_settings
    from app.core.security import create_access_token

    settings = get_settings()
    email = f"gate_check_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "Password123!"

    # 1. Register unverified user
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Gate User", "email": email, "password": password},
    )

    # 2. Turn on mandatory email verification
    monkeypatch.setattr(settings, "require_email_verification", True)

    # 3. Login attempt should be blocked with 403 Forbidden
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 403
    assert "Account email is not verified" in login_resp.json().get("detail", "")

    # 4. Attempting to access protected route with an unverified user's token should also return 403
    from sqlalchemy import select
    from app.db.database import AsyncSessionFactory
    from app.models.user import User
    async with AsyncSessionFactory() as session:
        user = (await session.execute(select(User).where(User.email == email.lower()))).scalar_one()

    token = create_access_token(subject=str(user.id), email=user.email, role="student")
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 403
    assert "Account email is not verified" in me_resp.json().get("detail", "")

