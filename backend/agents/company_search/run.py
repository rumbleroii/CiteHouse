"""Run the company-search agent and return a simple API payload."""

from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from agents.company_search.agent import (
    AgentDecision,
    CompanyHit,
    get_agent,
    reset_search_tries,
)
from services.search_companies import search_by_company_number

_SEARCH_FAILED_MESSAGE = (
    "Search couldn’t be completed right now. Try again, or enter a Companies House number."
)
_NO_DECISION_MESSAGE = (
    "Couldn’t determine a matching company. Try a more specific name or Companies House number."
)


def _empty_not_found(message: str) -> dict:
    return {
        "status": "not_found",
        "message": message,
        "company": None,
        "candidates": [],
    }


def _build_prompt(
    message: str,
    *,
    prior_query: str | None = None,
    candidates: list[dict[str, Any]] | None = None,
) -> str:
    if not prior_query and not candidates:
        return message

    parts = [
        "This is a follow-up to refine a previous company search.",
    ]
    if prior_query:
        parts.append(f"Original query: {prior_query}")
    if candidates:
        parts.append(f"Previous candidates: {json.dumps(candidates)}")
    parts.append(f"User follow-up: {message}")
    return "\n".join(parts)


async def run_agentic_search(
    message: str,
    *,
    prior_query: str | None = None,
    candidates: list[dict[str, Any]] | None = None,
) -> dict:
    text = (message or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="message is required")

    try:
        agent = get_agent()
    except RuntimeError:
        return _empty_not_found(_SEARCH_FAILED_MESSAGE)

    prompt = _build_prompt(text, prior_query=prior_query, candidates=candidates)
    reset_search_tries()

    try:
        # Fresh run each time — no checkpointer (avoids INVALID_CHAT_HISTORY).
        # ~2 graph steps per tool call; budget for 5 search tries + get_company + decision.
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={"recursion_limit": 25},
        )
    except Exception:
        return _empty_not_found(_SEARCH_FAILED_MESSAGE)

    decision = result.get("structured_response")
    if not isinstance(decision, AgentDecision):
        return _empty_not_found(_NO_DECISION_MESSAGE)

    company: CompanyHit | None = None
    resolved_candidates: list[CompanyHit] = []

    if decision.status == "found" and decision.company_number:
        try:
            raw = await search_by_company_number(decision.company_number)
            company = CompanyHit(**raw)
        except HTTPException:
            return _empty_not_found(
                "Found a possible match but couldn’t load its details. "
                "Try again or enter the company number directly."
            )
    elif decision.status == "needs_clarification":
        for number in decision.candidates[:5]:
            try:
                raw = await search_by_company_number(number)
                resolved_candidates.append(CompanyHit(**raw))
            except HTTPException:
                continue
    elif decision.status == "not_found":
        if not decision.message.strip():
            decision.message = "No matching company found."

    return {
        "status": decision.status,
        "message": decision.message,
        "company": company.model_dump(exclude_none=True) if company else None,
        "candidates": [c.model_dump(exclude_none=True) for c in resolved_candidates],
    }
