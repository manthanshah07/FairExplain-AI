"""
FairExplain AI — Cryptographic Audit Hash Engine
==================================================
Generates SHA-256 checksums binding evaluation state, accounting balances,
and audit logs into tamper-evident digests.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_audit_hash(payload: dict[str, Any]) -> str:
    """
    Generate SHA-256 digest over normalized JSON payload.
    Ensures sorted keys for byte-level determinism.
    """
    normalized_json = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(normalized_json.encode("utf-8")).hexdigest()
