"""Sequential intelligence graph: profile → business model → competition → quality."""

from __future__ import annotations

import json
from typing import Any

from langgraph.graph import END, START, StateGraph

from agents.intelligence.business_model import get_business_model_agent
from agents.intelligence.competition import get_competition_agent
from agents.intelligence.reputation import get_reputation_agent
from agents.intelligence.state import (
    IntelligenceState,
    dumps_section,
    merge_gaps,
    update_confidence,
)
from schema.business_model import BusinessModelSection
from schema.competition import CompetitionSection
from schema.identity import CompanyIdentity
from schema.quality import QualitySection
from services.search_companies import get_company_profile


def _require_structured(result: dict[str, Any], model_cls: type):
    structured = result.get("structured_response")
    if isinstance(structured, model_cls):
        return structured
    if isinstance(structured, dict):
        return model_cls.model_validate(structured)
    raise RuntimeError(f"Agent returned no structured {model_cls.__name__}")


async def load_profile(state: IntelligenceState) -> dict[str, Any]:
    number = state["company_number"]
    try:
        profile = await get_company_profile(number)
        company = CompanyIdentity.model_validate(profile).model_dump(exclude_none=True)
        gaps = list(state.get("gaps") or [])
        if not company.get("sic_codes"):
            gaps = merge_gaps(gaps, ["No SIC codes on Companies House profile"])
        return {
            "company": company,
            "stage": "business_model",
            "gaps": gaps,
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "stage": "error",
            "error": f"Failed to load company profile: {exc}",
        }


async def business_model_node(state: IntelligenceState) -> dict[str, Any]:
    if state.get("stage") == "error":
        return {}
    company = state.get("company") or {}
    number = state["company_number"]
    prompt = (
        f"Analyse business model for company_number={number}.\n"
        f"Known profile JSON:\n{json.dumps(company)}\n"
        "Use get_company_profile, then return BusinessModelSection."
    )
    try:
        agent = get_business_model_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        section = _require_structured(result, BusinessModelSection)
        gaps = list(state.get("gaps") or [])
        if section.confidence == "low":
            gaps = merge_gaps(gaps, ["Business model evidence is thin (low confidence)"])
        if not section.sic_codes and not company.get("sic_codes"):
            gaps = merge_gaps(gaps, ["Business model lacks SIC grounding"])
        conf = update_confidence(state.get("confidence"), business_model=section.confidence)
        return {
            "business_model": dumps_section(section),
            "confidence": conf,
            "gaps": gaps,
            "stage": "competition",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "stage": "error",
            "error": f"Business model agent failed: {exc}",
        }


async def competition_node(state: IntelligenceState) -> dict[str, Any]:
    if state.get("stage") == "error":
        return {}
    company = state.get("company") or {}
    bm = state.get("business_model") or {}
    number = state["company_number"]
    prompt = (
        f"Assess competition for company_number={number}.\n"
        f"Profile:\n{json.dumps(company)}\n"
        f"Business model section:\n{json.dumps(bm)}\n"
        "Use search_peers first, then web_search with the required query patterns. "
        "Return CompetitionSection."
    )
    try:
        agent = get_competition_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        section = _require_structured(result, CompetitionSection)
        gaps = list(state.get("gaps") or [])
        if section.confidence == "low":
            gaps = merge_gaps(gaps, ["Competition evidence is thin (low confidence)"])
        conf = update_confidence(state.get("confidence"), competition=section.confidence)
        return {
            "competition": dumps_section(section),
            "confidence": conf,
            "gaps": gaps,
            "stage": "quality",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "stage": "error",
            "error": f"Competition agent failed: {exc}",
        }


async def quality_node(state: IntelligenceState) -> dict[str, Any]:
    if state.get("stage") == "error":
        return {}
    company = state.get("company") or {}
    competition = state.get("competition") or {}
    number = state["company_number"]
    prompt = (
        f"Assess reputation/quality for company_number={number}.\n"
        f"Profile:\n{json.dumps(company)}\n"
        f"Competition arena (context):\n{json.dumps((competition or {}).get('arena'))}\n"
        "Use web_search with Trustpilot/reviews/trade-press queries. Return QualitySection."
    )
    try:
        agent = get_reputation_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        section = _require_structured(result, QualitySection)
        gaps = list(state.get("gaps") or [])
        if section.customer_rating is None:
            gaps = merge_gaps(gaps, ["No numeric customer rating found in web snippets"])
        if section.confidence == "low":
            gaps = merge_gaps(gaps, ["Quality evidence is thin (low confidence)"])
        conf = update_confidence(state.get("confidence"), quality=section.confidence)
        return {
            "quality": dumps_section(section),
            "confidence": conf,
            "gaps": gaps,
            "stage": "done",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "stage": "error",
            "error": f"Reputation agent failed: {exc}",
        }


def _route_after_profile(state: IntelligenceState) -> str:
    if state.get("stage") == "error":
        return "end"
    return "business_model"


def _route_after_bm(state: IntelligenceState) -> str:
    if state.get("stage") == "error":
        return "end"
    return "competition"


def _route_after_comp(state: IntelligenceState) -> str:
    if state.get("stage") == "error":
        return "end"
    return "quality"


def build_intelligence_graph():
    graph = StateGraph(IntelligenceState)
    graph.add_node("load_profile", load_profile)
    graph.add_node("business_model", business_model_node)
    graph.add_node("competition", competition_node)
    graph.add_node("quality", quality_node)

    graph.add_edge(START, "load_profile")
    graph.add_conditional_edges(
        "load_profile",
        _route_after_profile,
        {"business_model": "business_model", "end": END},
    )
    graph.add_conditional_edges(
        "business_model",
        _route_after_bm,
        {"competition": "competition", "end": END},
    )
    graph.add_conditional_edges(
        "competition",
        _route_after_comp,
        {"quality": "quality", "end": END},
    )
    graph.add_edge("quality", END)

    return graph.compile()


_graph = None


def get_intelligence_graph():
    global _graph
    if _graph is None:
        _graph = build_intelligence_graph()
    return _graph
