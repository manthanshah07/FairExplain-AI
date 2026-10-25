"""
FairExplain AI — Refresh Token Rotation Concurrency & Family Resilience Tests
=============================================================================
SEC-04: Verifies PostgreSQL row-level locking (with_for_update), token family tracking,
and replay attack detection under both concurrent and sequential threat models.

Verifies:
  1. Concurrent refreshes: Exactly one request rotates the token; the competing lock-waiter
     is rejected gracefully (409) without destroying the active replacement session.
  2. Replacement usability: The token produced by the winning concurrent request is usable.
  3. Sequential replay: Replaying an ancestor token after session progression revokes the entire family.
  4. Delayed replay: Replaying a rotated token outside the concurrency leeway window revokes the family.
  5. Family isolation: Compromising one session family does NOT revoke independent sessions for the same user.
  6. Transaction rollback: Database state remains clean if an error occurs during rotation.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update

from app.db.database import AsyncSessionFactory
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User


@pytest.mark.anyio
async def test_concurrent_refreshes_preserve_replacement_usability() -> None:
    """SEC-04: Simultaneous refresh attempts must be serialized by PostgreSQL row locks.
    Exactly one request consumes the token (200); the competing request that waited on the lock
    is rejected (409) WITHOUT revoking the replacement token created by the winning request.
    The replacement token must remain active and fully usable.
    """
    email = f"concurrent_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "StrongPassword123!"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Register and login
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"name": "Concurrent User", "email": email, "password": password},
        )
        assert reg_resp.status_code == 201

        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_resp.status_code == 200
        cookie_header = login_resp.headers["set-cookie"]
        raw_token_0 = cookie_header.split("refresh_token=")[1].split(";")[0]
        assert raw_token_0 is not None

        # Execute two simultaneous refresh requests with the exact same initial refresh token
        results = await asyncio.gather(
            client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_0}),
            client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_0}),
            return_exceptions=True,
        )

        statuses = [r.status_code for r in results if not isinstance(r, Exception)]
        assert len(statuses) == 2, f"Exceptions occurred during concurrent refresh: {results}"

        # Winning request gets 200; losing request gets 409 (or 401)
        assert 200 in statuses, f"Expected winning request to succeed with 200, got: {statuses}"
        assert (409 in statuses or 401 in statuses), f"Expected competing request to be rejected, got: {statuses}"

        # Extract the replacement token issued to the winning request
        success_resp = next(r for r in results if r.status_code == 200)
        new_cookie_header = success_resp.headers["set-cookie"]
        raw_token_1 = new_cookie_header.split("refresh_token=")[1].split(";")[0]
        assert raw_token_1 != raw_token_0

        # PERSISTENCE CHECK: Verify PostgreSQL state
        async with AsyncSessionFactory() as session:
            user_res = await session.execute(select(User).where(User.email == email.lower()))
            user = user_res.scalar_one()

            tokens_res = await session.execute(
                select(RefreshToken).where(RefreshToken.user_id == user.id)
            )
            all_tokens = tokens_res.scalars().all()

            active_tokens = [t for t in all_tokens if not t.revoked]
            # Concurrency safety: Exactly one active token exists in PostgreSQL
            assert len(active_tokens) == 1, f"Expected exactly 1 active token in DB, found: {len(active_tokens)}"
            assert active_tokens[0].token_hash is not None

        # USABILITY CHECK: The client can immediately use the replacement token for its next refresh
        next_refresh_resp = await client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": raw_token_1},
        )
        assert next_refresh_resp.status_code == 200, (
            f"Replacement token should be valid and usable, got: {next_refresh_resp.status_code}"
        )


@pytest.mark.anyio
async def test_sequential_replay_revokes_entire_family() -> None:
    """SEC-04: Sequential progression (T0 -> T1 -> T2).
    If an attacker replays T0 after the session has moved to T2,
    replay detection identifies ancestor compromise and revokes the entire family.
    """
    email = f"sequential_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "StrongPassword123!"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Register and login -> T0
        await client.post(
            "/api/v1/auth/register",
            json={"name": "Sequential User", "email": email, "password": password},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        raw_token_0 = login_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Rotate T0 -> T1
        rot1_resp = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_0})
        assert rot1_resp.status_code == 200
        raw_token_1 = rot1_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Rotate T1 -> T2
        rot2_resp = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_1})
        assert rot2_resp.status_code == 200
        raw_token_2 = rot2_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Replay Attack: Replay initial ancestor token T0
        replay_resp = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_0})
        assert replay_resp.status_code == 401
        assert "Compromised refresh token replayed" in replay_resp.json().get("detail", "")

        # Verify T2 is now also revoked as part of the family revocation
        victim_resp = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_2})
        assert victim_resp.status_code == 401

        # Check DB: All tokens in this family are revoked
        async with AsyncSessionFactory() as session:
            user = (await session.execute(select(User).where(User.email == email.lower()))).scalar_one()
            tokens = (await session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))).scalars().all()
            assert len(tokens) == 3
            assert all(t.revoked for t in tokens)


@pytest.mark.anyio
async def test_delayed_replay_outside_leeway_revokes_family() -> None:
    """SEC-04: Delayed Replay.
    When a token was rotated to T1, but T0 is replayed AFTER the concurrency leeway window,
    it must be treated as a genuine stolen-token replay and revoke the family.
    """
    email = f"delayed_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "StrongPassword123!"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Register and login -> T0
        await client.post(
            "/api/v1/auth/register",
            json={"name": "Delayed User", "email": email, "password": password},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        raw_token_0 = login_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Rotate T0 -> T1
        rot_resp = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_0})
        assert rot_resp.status_code == 200
        raw_token_1 = rot_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Simulate time passage beyond the leeway window (set rotated_at = 60s ago in DB)
        async with AsyncSessionFactory() as session:
            await session.execute(
                update(RefreshToken)
                .where(RefreshToken.revoked.is_(True))
                .values(rotated_at=datetime.now(timezone.utc) - timedelta(seconds=60))
            )
            await session.commit()

        # Replay T0 outside leeway window
        delayed_replay = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_0})
        assert delayed_replay.status_code == 401
        assert "Compromised refresh token replayed" in delayed_replay.json().get("detail", "")

        # Verify T1 has also been revoked
        t1_resp = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token_1})
        assert t1_resp.status_code == 401


@pytest.mark.anyio
async def test_family_specific_revocation_preserves_independent_sessions() -> None:
    """SEC-04: Multi-session isolation.
    A user logs in from two separate devices (Browser A and Browser B), creating two distinct token families.
    If a replay attack compromises Family A, Family A is revoked, but Family B remains ACTIVE and functional.
    """
    email = f"multisession_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "StrongPassword123!"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Register
        await client.post(
            "/api/v1/auth/register",
            json={"name": "Multi User", "email": email, "password": password},
        )

        # 1. Device A login -> Family A
        login_a = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token_a0 = login_a.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # 2. Device B login -> Family B
        login_b = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token_b0 = login_b.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Rotate Device A: T_A0 -> T_A1
        rot_a = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": token_a0})
        assert rot_a.status_code == 200
        token_a1 = rot_a.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Simulate delayed replay attack on Device A by ageing T_A0
        async with AsyncSessionFactory() as session:
            await session.execute(
                update(RefreshToken)
                .where(RefreshToken.replaced_by.isnot(None))
                .values(rotated_at=datetime.now(timezone.utc) - timedelta(seconds=60))
            )
            await session.commit()

        # Replay T_A0 -> Family A is compromised and revoked
        replay_a = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": token_a0})
        assert replay_a.status_code == 401

        # Device A's descendant token T_A1 is now revoked
        check_a1 = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": token_a1})
        assert check_a1.status_code == 401

        # CRITICAL TEST: Device B's independent session (Family B) is STILL ACTIVE and can refresh!
        refresh_b = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": token_b0})
        assert refresh_b.status_code == 200, "Device B session should remain active despite Device A compromise!"


@pytest.mark.anyio
async def test_transaction_rollback_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """SEC-04: Transaction Rollback.
    If an unexpected failure or exception occurs during rotation (e.g. database error while storing replacement),
    the transaction rolls back cleanly, leaving no orphaned replacement tokens and leaving existing session state uncorrupted.
    """
    from app.repositories.auth_repository import AuthRepository

    email = f"rollback_{uuid.uuid4().hex[:8]}@nitk.edu.in"
    password = "StrongPassword123!"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"name": "Rollback User", "email": email, "password": password},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        raw_token = login_resp.headers["set-cookie"].split("refresh_token=")[1].split(";")[0]

        # Intercept store_refresh_token to simulate sudden DB failure on the replacement insert
        original_store = AuthRepository.store_refresh_token
        call_count = 0

        async def faulty_store(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count > 0:  # Fail during refresh rotation store
                raise RuntimeError("Simulated transient PostgreSQL disk write error during replacement insert")
            return await original_store(*args, **kwargs)

        monkeypatch.setattr(AuthRepository, "store_refresh_token", faulty_store)

        with pytest.raises(RuntimeError, match="Simulated transient PostgreSQL disk write error"):
            await client.post("/api/v1/auth/refresh", cookies={"refresh_token": raw_token})

    # VERIFY PERSISTENCE: Database rollback preserved state
    async with AsyncSessionFactory() as session:
        user = (await session.execute(select(User).where(User.email == email.lower()))).scalar_one()
        tokens = (await session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))).scalars().all()

        # Should only have the initial login token, still active because transaction rolled back
        assert len(tokens) == 1
        assert tokens[0].revoked is False
        assert tokens[0].replaced_by is None

