"""
FairExplain AI — Unit Tests for Settings & Database URL Sanitization
======================================================================
Tests normalization of cloud PostgreSQL (Neon, Supabase) connection strings,
verifying removal of unsupported asyncpg arguments such as `channel_binding` and `sslmode`.
"""

from __future__ import annotations

import unittest
from app.config.settings import Settings


class TestSettingsDatabaseUrlSanitizer(unittest.TestCase):
    """Verify that Neon connection strings with channel_binding and sslmode are cleaned."""

    def test_strip_channel_binding_and_normalize_ssl(self) -> None:
        raw_url = (
            "postgresql://neondb_owner:npg_secret@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb"
            "?sslmode=require&channel_binding=prefer"
        )
        settings = Settings(database_url=raw_url)
        self.assertTrue(settings.database_url.startswith("postgresql+asyncpg://"))
        self.assertNotIn("channel_binding", settings.database_url)
        self.assertNotIn("sslmode", settings.database_url)
        self.assertIn("ssl=require", settings.database_url)

    def test_strip_channel_binding_require(self) -> None:
        raw_url = (
            "postgres://user:pass@ep-cool-fog.neon.tech/neondb"
            "?channel_binding=require&sslmode=require&endpoint=ep-cool-fog"
        )
        settings = Settings(database_url=raw_url)
        self.assertTrue(settings.database_url.startswith("postgresql+asyncpg://"))
        self.assertNotIn("channel_binding", settings.database_url)
        self.assertNotIn("sslmode", settings.database_url)
        self.assertNotIn("endpoint", settings.database_url)
        self.assertIn("ssl=require", settings.database_url)

    def test_plain_asyncpg_url_untouched(self) -> None:
        raw_url = "postgresql+asyncpg://user:pass@localhost:5432/fairexplain"
        settings = Settings(database_url=raw_url)
        self.assertEqual(settings.database_url, raw_url)


class TestProductionSettingsSecurityValidation(unittest.TestCase):
    """SEC-03: Enforce fail-closed production settings validation."""

    def test_production_fails_with_default_jwt_secret(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="change-me-to-a-secure-jwt-secret-key-at-least-32-bytes",
                secret_key="strong-secret-key-that-is-at-least-32-characters-long",
                cookie_secure=True,
                storage_backend="s3",
                s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
            )
        self.assertIn("JWT_SECRET_KEY must be set to a strong random secret", str(ctx.exception))
        # Ensure secret is not printed in exception
        self.assertNotIn("change-me-to-a-secure-jwt-secret-key", str(ctx.exception))

    def test_production_fails_with_short_jwt_secret(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="too-short-secret",
                secret_key="strong-secret-key-that-is-at-least-32-characters-long",
                cookie_secure=True,
                storage_backend="s3",
                s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
            )
        self.assertIn("JWT_SECRET_KEY must be set to a strong random secret", str(ctx.exception))

    def test_production_fails_with_local_storage(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="strong-jwt-secret-key-that-is-at-least-32-characters-long",
                secret_key="strong-secret-key-that-is-at-least-32-characters-long",
                cookie_secure=True,
                storage_backend="local",
                s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
            )
        self.assertIn("STORAGE_BACKEND must be 's3' in production", str(ctx.exception))

    def test_production_fails_with_insecure_cookies(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="strong-jwt-secret-key-that-is-at-least-32-characters-long",
                secret_key="strong-secret-key-that-is-at-least-32-characters-long",
                cookie_secure=False,
                storage_backend="s3",
                s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
            )
        self.assertIn("COOKIE_SECURE must be True", str(ctx.exception))

    def test_production_fails_without_kms_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="strong-jwt-secret-key-that-is-at-least-32-characters-long",
                secret_key="strong-secret-key-that-is-at-least-32-characters-long",
                cookie_secure=True,
                storage_backend="s3",
                s3_kms_key_arn=None,
            )
        self.assertIn("S3_KMS_KEY_ARN must be configured", str(ctx.exception))

    def test_production_succeeds_with_valid_secure_config(self) -> None:
        settings = Settings(
            app_env="production",
            jwt_secret_key="strong-jwt-secret-key-that-is-at-least-32-characters-long",
            secret_key="strong-secret-key-that-is-at-least-32-characters-long",
            cookie_secure=True,
            storage_backend="s3",
            s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
        )
        self.assertTrue(settings.is_production)
        self.assertEqual(settings.storage_backend, "s3")
        self.assertFalse(settings.enable_public_registration)

    def test_production_fails_with_weak_secret_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="strong-jwt-secret-key-that-is-at-least-32-characters-long",
                secret_key="short",
                cookie_secure=True,
                storage_backend="s3",
                s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
            )
        self.assertIn("SECRET_KEY must be set to a strong random secret", str(ctx.exception))

    def test_production_fails_with_public_registration_without_email_verification(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Settings(
                app_env="production",
                jwt_secret_key="strong-jwt-secret-key-that-is-at-least-32-characters-long",
                secret_key="strong-secret-key-that-is-at-least-32-characters-long",
                cookie_secure=True,
                storage_backend="s3",
                s3_kms_key_arn="arn:aws:kms:ap-south-1:123456789012:key/test",
                enable_public_registration=True,
                require_email_verification=False,
            )
        self.assertIn("Public registration cannot be enabled in production without mandatory email verification", str(ctx.exception))

    def test_environment_variable_alias_production_activates_validation(self) -> None:
        import os
        old_env = os.environ.get("ENVIRONMENT")
        old_app_env = os.environ.get("APP_ENV")
        try:
            os.environ["ENVIRONMENT"] = "production"
            if "APP_ENV" in os.environ:
                del os.environ["APP_ENV"]
            with self.assertRaises(ValueError) as ctx:
                Settings()  # Has default insecure secrets
            self.assertIn("Production configuration error", str(ctx.exception))
        finally:
            if old_env is not None:
                os.environ["ENVIRONMENT"] = old_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            if old_app_env is not None:
                os.environ["APP_ENV"] = old_app_env

    def test_environment_variable_alias_conflict_rejected(self) -> None:
        import os
        old_env = os.environ.get("ENVIRONMENT")
        old_app_env = os.environ.get("APP_ENV")
        try:
            os.environ["APP_ENV"] = "production"
            os.environ["ENVIRONMENT"] = "development"
            with self.assertRaises(ValueError) as ctx:
                Settings()
            self.assertIn("Conflicting environment configurations", str(ctx.exception))
        finally:
            if old_env is not None:
                os.environ["ENVIRONMENT"] = old_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            if old_app_env is not None:
                os.environ["APP_ENV"] = old_app_env
            elif "APP_ENV" in os.environ:
                del os.environ["APP_ENV"]

    def test_development_allows_defaults(self) -> None:
        settings = Settings(app_env="development")
        self.assertTrue(settings.is_development)
        self.assertEqual(settings.storage_backend, "local")
