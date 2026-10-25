"""
FairExplain AI — Test Configuration
======================================
pytest fixtures shared across all test modules.
Provides async clients, database sessions, and authenticated user tokens for RBAC & BOLA testing.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token, hash_password
from app.db.database import AsyncSessionFactory
from app.main import app
from app.middleware.rate_limit import limiter
from app.models.user import User, UserRole


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> None:
    """Disable rate limiting in test harness to avoid test flakiness."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client wired to the FastAPI test app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture
async def student_user() -> User:
    """Create a persistent student user for tests."""
    async with AsyncSessionFactory() as session:
        user = User(
            name="Test Student Priya",
            email=f"priya_{uuid.uuid4().hex[:8]}@nitk.edu.in",
            hashed_password=hash_password("StudentPassword123!"),
            role=UserRole.student,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
def student_auth_headers(student_user: User) -> dict[str, str]:
    """Authorization header with valid access token for student_user."""
    token = create_access_token(
        subject=str(student_user.id),
        email=student_user.email,
        role=UserRole.student.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_student_user() -> User:
    """Create a distinct second student for BOLA isolation testing."""
    async with AsyncSessionFactory() as session:
        user = User(
            name="Test Student Rahul",
            email=f"rahul_{uuid.uuid4().hex[:8]}@nitk.edu.in",
            hashed_password=hash_password("StudentPassword123!"),
            role=UserRole.student,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
def other_student_auth_headers(other_student_user: User) -> dict[str, str]:
    """Authorization header for second student user."""
    token = create_access_token(
        subject=str(other_student_user.id),
        email=other_student_user.email,
        role=UserRole.student.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def reviewer_user() -> User:
    """Create a financial aid reviewer user for tests."""
    async with AsyncSessionFactory() as session:
        user = User(
            name="Dr. Sarah Jenkins",
            email=f"sarah_{uuid.uuid4().hex[:8]}@nitk.edu.in",
            hashed_password=hash_password("ReviewerPassword123!"),
            role=UserRole.reviewer,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
def reviewer_auth_headers(reviewer_user: User) -> dict[str, str]:
    """Authorization header with valid access token for reviewer_user."""
    token = create_access_token(
        subject=str(reviewer_user.id),
        email=reviewer_user.email,
        role=UserRole.reviewer.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_user() -> User:
    """Create an administrator user for tests."""
    async with AsyncSessionFactory() as session:
        user = User(
            name="System Admin",
            email=f"admin_{uuid.uuid4().hex[:8]}@nitk.edu.in",
            hashed_password=hash_password("AdminPassword123!"),
            role=UserRole.admin,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict[str, str]:
    """Authorization header with valid access token for admin_user."""
    token = create_access_token(
        subject=str(admin_user.id),
        email=admin_user.email,
        role=UserRole.admin.value,
    )
    return {"Authorization": f"Bearer {token}"}
