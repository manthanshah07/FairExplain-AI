"""
FairExplain AI — Authentication Router
========================================
REST endpoints for registration, login, token refresh (RTR), logout, and current user profile.
"""

from typing import Any

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import BaseResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new applicant account",
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserResponse]:
    """Register an applicant account. Subject to institutional domain checks and environment registration policy."""
    from app.config.settings import get_settings
    settings = get_settings()
    if not settings.enable_public_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public self-service registration is disabled in this environment. Contact your institution administrator for account provisioning.",
        )

    user = await AuthService.register(request, db)
    return BaseResponse[UserResponse](
        success=True,
        data=user,
        message="User account registered successfully.",
    )


@router.post(
    "/login",
    response_model=BaseResponse[TokenResponse],
    summary="Authenticate with credentials and obtain access token & refresh cookie",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginRequest = Body(...),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[TokenResponse]:
    """
    Authenticate email and password.
    Returns short-lived (15-min) access token in response body,
    and sets HttpOnly; SameSite=Strict refresh token in response cookie.
    """
    data = await AuthService.login(
        email=payload.email,
        password=payload.password,
        response=response,
        db=db,
    )
    return BaseResponse[TokenResponse](
        success=True,
        data=TokenResponse(**data),
        message="Authentication successful.",
    )


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenResponse],
    summary="Rotate refresh token and obtain new access token",
)
async def refresh_tokens(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[TokenResponse]:
    """
    Single-use Refresh Token Rotation (RTR).
    Invalidates used refresh token; issues new access token and new refresh cookie.
    Detects replay attacks and revokes token family if reused.
    """
    data = await AuthService.refresh_tokens(
        raw_refresh_token=refresh_token,
        response=response,
        db=db,
    )
    return BaseResponse[TokenResponse](
        success=True,
        data=TokenResponse(**data),
        message="Token refreshed successfully.",
    )


@router.post(
    "/logout",
    response_model=BaseResponse[dict[str, Any]],
    summary="Log out and invalidate session refresh token",
)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Revoke active refresh token in database and clear the HttpOnly session cookie."""
    await AuthService.logout(
        raw_refresh_token=refresh_token,
        response=response,
        db=db,
    )
    return BaseResponse[dict[str, Any]](
        success=True,
        data={"logged_out": True},
        message="Logged out successfully.",
    )


@router.get(
    "/me",
    response_model=BaseResponse[UserResponse],
    summary="Retrieve authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> BaseResponse[UserResponse]:
    """Return identity and role profile of the requesting authenticated principal."""
    role_str = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return BaseResponse[UserResponse](
        success=True,
        data=UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            role=role_str,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
        ),
        message="Profile retrieved.",
    )
