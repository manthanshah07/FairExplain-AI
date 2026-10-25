"""
FairExplain AI — Application Settings
======================================
Centralises all environment-driven configuration using Pydantic Settings.
Every value is typed and validated at startup; the application will fail
fast with a clear error if a required variable is missing or malformed.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide settings loaded from environment variables / .env file.
    Prefer accessing settings via the module-level `get_settings()` factory so
    that the object is constructed only once (cached) per process.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application identity
    # ------------------------------------------------------------------
    app_name: str = Field(default="FairExplain AI")
    app_version: str = Field(default="1.0.0")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development"
    )
    debug: bool = Field(default=False)

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost/fairexplain"
    )

    # ------------------------------------------------------------------
    # Security & Authentication (Milestone 1)
    # ------------------------------------------------------------------
    secret_key: str = Field(default="change-me-to-a-secure-random-string")
    jwt_secret_key: str = Field(default="change-me-to-a-secure-jwt-secret-key-at-least-32-bytes")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    refresh_token_concurrency_leeway_seconds: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Leeway window in seconds to allow in-flight concurrent requests on rotated tokens without invalidating the token family.",
    )
    allowed_email_domains: list[str] = Field(default=[])

    enable_public_registration: bool = Field(
        default=True,
        description="Allow self-service applicant registration. Disabled by default in production.",
    )
    require_email_verification: bool = Field(
        default=False,
        description="Require email confirmation before allowing account login or access to protected endpoints.",
    )

    cookie_secure: bool = Field(default=False)
    cookie_samesite: Literal["lax", "strict", "none"] = Field(default="lax")

    # ------------------------------------------------------------------
    # Object Storage (S3 / MinIO / Local)
    # ------------------------------------------------------------------
    storage_backend: Literal["local", "s3"] = Field(default="local")
    s3_bucket_name: str = Field(default="fairexplain-documents")
    s3_region_name: str = Field(default="ap-south-1")
    s3_endpoint_url: str | None = Field(default=None)
    aws_access_key_id: str | None = Field(default=None)
    aws_secret_access_key: str | None = Field(default=None)
    s3_kms_key_arn: str | None = Field(default=None)

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    allowed_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: Literal["json", "text"] = Field(default="json")

    # ------------------------------------------------------------------
    # Computed helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """
        Ensure asyncpg driver is specified and strip query parameters unsupported by asyncpg
        (e.g., channel_binding, sslmode, endpoint from Neon / Supabase connection strings).
        """
        from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

        if not isinstance(value, str):
            return value
        url = value.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        parsed = urlparse(url)
        if not parsed.query:
            return url

        params = parse_qs(parsed.query, keep_blank_values=True)
        unsupported = {
            "channel_binding",
            "sslmode",
            "endpoint",
            "gssencmode",
            "sslcert",
            "sslkey",
            "sslrootcert",
        }
        clean_params: dict[str, list[str]] = {}
        needs_ssl = "sslmode" in params or "ssl" in params

        for k, v in params.items():
            if k in unsupported:
                continue
            clean_params[k] = v

        if needs_ssl and "ssl" not in clean_params:
            clean_params["ssl"] = ["require"]

        new_query = urlencode(clean_params, doseq=True)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

    @field_validator("allowed_origins", "allowed_email_domains", mode="before")
    @classmethod
    def parse_string_list(cls, value: str | list[str]) -> list[str]:
        """Allow JSON string, comma-separated string, or a proper list."""
        if isinstance(value, str):
            val = value.strip()
            if val.startswith("[") and val.endswith("]"):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
            return [x.strip() for x in val.split(",") if x.strip()]
        return value

    @model_validator(mode="before")
    @classmethod
    def resolve_environment_aliases(cls, data: Any) -> Any:
        """
        Normalize environment variable aliases (APP_ENV vs ENVIRONMENT).
        Rejects conflicting definitions and defaults enable_public_registration to False in production.
        """
        if isinstance(data, dict):
            import os
            # Check explicit process environment variables first
            os_app_env = os.environ.get("APP_ENV")
            os_env = os.environ.get("ENVIRONMENT")

            if os_app_env and os_env:
                if os_app_env.strip().lower() != os_env.strip().lower():
                    raise ValueError(
                        f"Conflicting environment configurations: APP_ENV='{os_app_env}' vs ENVIRONMENT='{os_env}'."
                    )

            # Determine canonical environment: explicit os.environ takes precedence over .env file
            canonical_env = os_app_env or os_env or data.get("app_env") or data.get("environment")
            if canonical_env:
                clean_env = canonical_env.strip().lower()
                data["app_env"] = clean_env
                if clean_env == "production" and "enable_public_registration" not in data:
                    data["enable_public_registration"] = False
        return data

    @model_validator(mode="after")
    def validate_production_configuration(self) -> Settings:
        """
        Enforce fail-closed security invariants when running in production:
        1. JWT secret must be present, non-default, and >= 32 chars.
        2. Application secret must be present, non-default, and >= 32 chars.
        3. Secure cookies must be strictly enabled.
        4. Storage backend must be durable S3 (never ephemeral local disk).
        5. SSE-KMS customer-managed encryption key ARN must be configured.
        6. Public self-service registration cannot be enabled without mandatory email verification.
        """
        if self.app_env == "production":
            insecure_jwt_defaults = {
                "change-me-to-a-secure-jwt-secret-key-at-least-32-bytes",
                "dev-secret-key-fairexplain-ai-local-testing-key-32chars",
                "secret",
                "changeme",
                "test-jwt-secret-key-for-ci-pipeline-only-32bytes",
            }
            if (
                not self.jwt_secret_key
                or self.jwt_secret_key in insecure_jwt_defaults
                or len(self.jwt_secret_key) < 32
            ):
                raise ValueError(
                    "Production configuration error: JWT_SECRET_KEY must be set to a strong random secret of at least 32 characters."
                )

            insecure_secret_defaults = {
                "change-me-to-a-secure-random-string",
                "dev-secret-key-fairexplain-ai-local-testing-key-32chars",
                "secret",
                "changeme",
                "test-secret-key-for-ci-pipeline-only",
            }
            if (
                not self.secret_key
                or self.secret_key in insecure_secret_defaults
                or len(self.secret_key) < 32
            ):
                raise ValueError(
                    "Production configuration error: SECRET_KEY must be set to a strong random secret of at least 32 characters."
                )

            if not self.cookie_secure:
                raise ValueError(
                    "Production configuration error: COOKIE_SECURE must be True in production."
                )

            if self.storage_backend != "s3":
                raise ValueError(
                    f"Production configuration error: STORAGE_BACKEND must be 's3' in production; got '{self.storage_backend}'. Silent fallback to ephemeral local storage is disallowed."
                )

            if not self.s3_kms_key_arn:
                raise ValueError(
                    "Production configuration error: S3_KMS_KEY_ARN must be configured for SSE-KMS customer-managed key encryption."
                )

            if self.enable_public_registration and not self.require_email_verification:
                raise ValueError(
                    "Production configuration error: Public registration cannot be enabled in production without mandatory email verification (require_email_verification=True)."
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the application settings singleton."""
    return Settings()
