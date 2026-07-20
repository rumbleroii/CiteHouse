"""Deterministic confidence rules for intelligence pillars.

Agents may still emit a confidence field; the graph overwrites it with these rules.
"""

from __future__ import annotations

from typing import Any, Sequence

from schema.common import ConfidenceLevel


def _has_values(items: Sequence[Any] | None) -> bool:
    return bool(items)


def business_model_confidence(*, sic_codes: Sequence[Any] | None) -> ConfidenceLevel:
    """Medium when SIC codes exist; otherwise Low."""
    return "medium" if _has_values(sic_codes) else "low"


def competition_confidence(
    *,
    has_peer_set: bool,
    has_web_company_refs: bool,
    has_profile_verify: bool,
) -> ConfidenceLevel:
    """High if peers + web name refs + profile corroboration; medium if peers only; else low."""
    if has_peer_set and has_web_company_refs and has_profile_verify:
        return "high"
    if has_peer_set:
        return "medium"
    return "low"


def quality_confidence(
    *,
    has_trustpilot: bool,
    has_trade_press: bool,
    has_profile_verify: bool,
) -> ConfidenceLevel:
    """Medium when Trustpilot + trade press mention the company and profile is corroborated once; else low."""
    if has_trustpilot and has_trade_press and has_profile_verify:
        return "medium"
    return "low"


def rivalry_score_from_peer_count(peer_count_estimate: int) -> int:
    """Map Companies House peer total_results to rivalry 1–5."""
    n = max(0, int(peer_count_estimate or 0))
    if n <= 10:
        return 1
    if n <= 50:
        return 2
    if n <= 200:
        return 3
    if n <= 1000:
        return 4
    return 5
