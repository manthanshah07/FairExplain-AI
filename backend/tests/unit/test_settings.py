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
