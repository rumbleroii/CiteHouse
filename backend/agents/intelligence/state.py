"""Shared state and helpers for the intelligence graph."""

from __future__ import annotations

import json
from typing import Any, Literal, TypedDict

from schema.common import ConfidenceLevel

Stage = Literal[
    "profile",
    "business_model",
    "competition",
    "quality",
    "done",
    "error",
]


class IntelligenceState(TypedDict):
    company_number: str
    company: dict[str, Any]
    business_model: dict[str, Any] | None
    competition: dict[str, Any] | None
    quality: dict[str, Any] | None
    confidence: dict[str, Any] | None
    gaps: list[str]
    stage: Stage
    error: str | None


_CONFIDENCE_RANK: dict[str, int] = {"low": 0, "medium": 1, "high": 2}


def initial_state(company_number: str) -> IntelligenceState:
    return {
        "company_number": company_number.strip().upper(),
        "company": {},
        "business_model": None,
        "competition": None,
        "quality": None,
        "confidence": None,
        "gaps": [],
        "stage": "profile",
        "error": None,
    }


def merge_gaps(existing: list[str], extra: list[str] | None) -> list[str]:
    out = list(existing)
    for item in extra or []:
        text = (item or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def update_confidence(
    current: dict[str, Any] | None,
    *,
    business_model: ConfidenceLevel | None = None,
    competition: ConfidenceLevel | None = None,
    quality: ConfidenceLevel | None = None,
) -> dict[str, Any]:
    base = {
        "overall": "low",
        "business_model": "low",
        "competition": "low",
        "quality": "low",
        **(current or {}),
    }
    if business_model is not None:
        base["business_model"] = business_model
    if competition is not None:
        base["competition"] = competition
    if quality is not None:
        base["quality"] = quality

    pillars = [
        base.get("business_model", "low"),
        base.get("competition", "low"),
        base.get("quality", "low"),
    ]
    base["overall"] = min(pillars, key=lambda c: _CONFIDENCE_RANK.get(str(c), 0))
    return base


def overall_from_completed(state: IntelligenceState) -> ConfidenceLevel:
    levels: list[str] = []
    conf = state.get("confidence") or {}
    if state.get("business_model"):
        levels.append(str(conf.get("business_model", "low")))
    if state.get("competition"):
        levels.append(str(conf.get("competition", "low")))
    if state.get("quality"):
        levels.append(str(conf.get("quality", "low")))
    if not levels:
        return "low"
    return min(levels, key=lambda c: _CONFIDENCE_RANK.get(c, 0))  # type: ignore[return-value]


def state_to_partial_report(state: IntelligenceState) -> dict[str, Any]:
    """JSON-serializable partial report: only completed pillars + company when present."""
    payload: dict[str, Any] = {
        "stage": state.get("stage"),
        "gaps": list(state.get("gaps") or []),
    }
    if state.get("company"):
        payload["company"] = state["company"]
    if state.get("business_model"):
        payload["business_model"] = state["business_model"]
    if state.get("competition"):
        payload["competition"] = state["competition"]
    if state.get("quality"):
        payload["quality"] = state["quality"]
    if state.get("confidence"):
        conf = dict(state["confidence"])
        conf["overall"] = overall_from_completed(state)
        payload["confidence"] = conf
    return payload


def dumps_section(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_none=True)
    if isinstance(model, dict):
        return model
    return json.loads(json.dumps(model))
