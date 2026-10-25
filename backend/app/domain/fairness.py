"""
FairExplain AI — Deterministic Fairness & Proxy Screening Engine
==================================================================
Pure Python implementation of proxy screening, demographic leakage detection,
and disparate impact analysis per RULE_ENGINE.md and ROADMAP.md §4 (Phase 5).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Mapping, Sequence

PROHIBITED_DEMOGRAPHIC_TERMS: frozenset[str] = frozenset({
    "caste",
    "dalit",
    "brahmin",
    "kshatriya",
    "vaishya",
    "shudra",
    "reservation",
    "quota",
    "religion",
    "muslim",
    "hindu",
    "christian",
    "sikh",
    "jain",
    "gender",
    "female",
    "male",
    "disabled",
    "handicapped",
})

# Sample high-risk socio-economic proxy geographical markers/pincodes
FLAGGED_POSTAL_PROXIES: frozenset[str] = frozenset({
    "110006",  # Historic walled city proxy
    "400017",  # High-density informal settlement proxy
    "700024",  # Flagged municipal postal proxy
})


@dataclass(frozen=True)
class FairnessViolation:
    """Detailed record of an identified fairness or proxy violation."""

    violation_type: str
    detected_token: str
    position_start: int
    position_end: int
    snippet: str


@dataclass(frozen=True)
class FairnessAuditReport:
    """Outcome report of a fairness screening pass."""

    is_clean: bool
    violations: list[FairnessViolation]
    sanitized_text: str
    total_violations_count: int


def screen_text_for_proxies(text: str) -> FairnessAuditReport:
    """
    Scan text for prohibited demographic terms and geographical proxies.
    Replaces violations with [REDACTED_DEMOGRAPHIC_PROXY] for safety.
    """
    violations: list[FairnessViolation] = []
    sanitized = text

    # 1. Screen demographic keywords
    for term in sorted(PROHIBITED_DEMOGRAPHIC_TERMS, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        for match in pattern.finditer(text):
            start, end = match.span()
            snippet_start = max(0, start - 20)
            snippet_end = min(len(text), end + 20)
            violations.append(
                FairnessViolation(
                    violation_type="demographic_leakage",
                    detected_token=match.group(0),
                    position_start=start,
                    position_end=end,
                    snippet=text[snippet_start:snippet_end],
                )
            )

    # 2. Screen postal/geographical proxies
    for proxy in FLAGGED_POSTAL_PROXIES:
        pattern = re.compile(rf"\b{re.escape(proxy)}\b")
        for match in pattern.finditer(text):
            start, end = match.span()
            snippet_start = max(0, start - 15)
            snippet_end = min(len(text), end + 15)
            violations.append(
                FairnessViolation(
                    violation_type="geographic_proxy",
                    detected_token=match.group(0),
                    position_start=start,
                    position_end=end,
                    snippet=text[snippet_start:snippet_end],
                )
            )

    # Sort violations in reverse order of appearance to cleanly redact without index shifts
    sorted_violations = sorted(violations, key=lambda v: v.position_start, reverse=True)
    for v in sorted_violations:
        sanitized = (
            sanitized[: v.position_start]
            + "[REDACTED_DEMOGRAPHIC_PROXY]"
            + sanitized[v.position_end :]
        )

    return FairnessAuditReport(
        is_clean=len(violations) == 0,
        violations=violations,
        sanitized_text=sanitized,
        total_violations_count=len(violations),
    )


def compute_disparate_impact_ratio(
    protected_pass_rate: float, baseline_pass_rate: float
) -> float:
    """
    Calculate disparate impact ratio using the 4/5ths (80%) rule.
    Returns 1.0 if baseline is zero.
    """
    if baseline_pass_rate <= 0.0:
        return 1.0
    return round(protected_pass_rate / baseline_pass_rate, 4)
