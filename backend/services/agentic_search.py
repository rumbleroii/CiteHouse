"""Run the company-search agent and return a simple API payload."""

from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from agents.company_search import AgentDecision, CompanyHit, get_agent
from services.search_companies import search_by_company_number


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
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    prompt = _build_prompt(text, prior_query=prior_query, candidates=candidates)

    try:
        # Fresh run each time — no checkpointer (avoids INVALID_CHAT_HISTORY).
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Agentic search failed: {exc}",
        ) from exc

    decision = result.get("structured_response")
    if not isinstance(decision, AgentDecision):
        raise HTTPException(status_code=502, detail="Agent returned no structured decision")

    company: CompanyHit | None = None
    resolved_candidates: list[CompanyHit] = []

    if decision.status == "found" and decision.company_number:
        raw = await search_by_company_number(decision.company_number)
        company = CompanyHit(**raw)
    elif decision.status == "needs_clarification":
        for number in decision.candidates[:5]:
            try:
                raw = await search_by_company_number(number)
                resolved_candidates.append(CompanyHit(**raw))
            except HTTPException:
                continue
    elif decision.status == "not_found":
        # Keep message explicit for the UI.
        if not decision.message.strip():
            decision.message = "No matching company found."

    return {
        "status": decision.status,
        "message": decision.message,
        "company": company.model_dump(exclude_none=True) if company else None,
        "candidates": [c.model_dump(exclude_none=True) for c in resolved_candidates],
    }
