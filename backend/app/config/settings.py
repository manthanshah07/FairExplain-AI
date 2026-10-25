"""
FairExplain AI — Application Settings
======================================
Centralises all environment-driven configuration using Pydantic Settings.
Every value is typed and validated at startup; the application will fail
fast with a clear error if a required variable is missing or malformed.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, field_validator
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
    # Security
    # ------------------------------------------------------------------
    secret_key: str = Field(default="change-me-to-a-secure-random-string")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60, ge=1)

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
        # libpq / psql parameters unsupported by asyncpg keyword arguments
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

        # When connecting to cloud Postgres (Neon/Supabase) via SSL, pass ssl=require to asyncpg
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

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        """Allow comma-separated string from env var or a proper list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the application settings singleton.

    Using lru_cache ensures this is constructed exactly once, making it safe
    to call at module import time without repeatedly parsing the .env file.
    """
    return Settings()
