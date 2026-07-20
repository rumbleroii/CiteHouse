"""Sequential intelligence graph: profile → business model → competition → quality."""

from __future__ import annotations

import json
import logging
from typing import Any

from langgraph.graph import END, START, StateGraph

from agents.intelligence.business_model import get_business_model_agent
from agents.intelligence.citations import (
    apply_citation_filter,
    quality_web_evidence,
    web_search_mentions_company,
)
from agents.intelligence.competition import get_competition_agent
from agents.intelligence.confidence import (
    business_model_confidence,
    competition_confidence,
    quality_confidence,
    rivalry_score_from_peer_count,
)
from agents.intelligence.reputation import get_reputation_agent
from agents.intelligence.state import (
    IntelligenceState,
    dumps_section,
    merge_gaps,
    update_confidence,
)
from schema.business_model import BusinessModelSection
from schema.competition import CompetitionArena, CompetitionSection, PeerCompany
from schema.identity import CompanyIdentity
from schema.quality import CustomerRating, QualitySection, TradePress
from services.search_companies import get_company_profile
from services.search_peers import search_peers

logger = logging.getLogger("citehouse.agents.intelligence")


def _sanitize_quality_section(
    section: QualitySection,
    *,
    has_trustpilot: bool,
    has_trade_press: bool,
) -> QualitySection:
    """Drop invented Trustpilot/trade-press fields when URL evidence is missing."""
    updates: dict[str, Any] = {}

    if not has_trade_press:
        updates["trade_press"] = TradePress(tone="neutral", notables=[])

    rating = section.customer_rating
    if rating is not None:
        platforms = [
            p
            for p in rating.platforms
            if has_trustpilot or "trustpilot" not in p.lower()
        ]
        if not has_trustpilot and not platforms and rating.score is None:
            updates["customer_rating"] = None
        elif platforms != rating.platforms:
            updates["customer_rating"] = CustomerRating(
                score=rating.score,
                scale=rating.scale,
                n_reviews=rating.n_reviews,
                platforms=platforms,
            )

    return section.model_copy(update=updates) if updates else section


def _require_structured(result: dict[str, Any], model_cls: type):
    structured = result.get("structured_response")
    if isinstance(structured, model_cls):
        return structured
    if isinstance(structured, dict):
        return model_cls.model_validate(structured)
    raise RuntimeError(f"Agent returned no structured {model_cls.__name__}")


async def load_profile(state: IntelligenceState) -> dict[str, Any]:
    number = state["company_number"]
    logger.info("pillar=load_profile start company_number=%s", number)
    try:
        profile = await get_company_profile(number)
        company = CompanyIdentity.model_validate(profile).model_dump(exclude_none=True)
        gaps = list(state.get("gaps") or [])
        if not company.get("sic_codes"):
            gaps = merge_gaps(gaps, ["No SIC codes on Companies House profile"])
        logger.info("pillar=load_profile done company_number=%s", number)
        return {
            "company": company,
            "stage": "business_model",
            "gaps": gaps,
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("pillar=load_profile failed company_number=%s", number)
        return {
            "stage": "error",
            "error": f"Failed to load company profile: {exc}",
        }


async def business_model_node(state: IntelligenceState) -> dict[str, Any]:
    if state.get("stage") == "error":
        return {}
    company = state.get("company") or {}
    number = state["company_number"]
    logger.info("pillar=business_model start company_number=%s", number)
    prompt = (
        f"Analyse business model for company_number={number}.\n"
        f"Known profile JSON:\n{json.dumps(company)}\n"
        "Use get_company_profile, then return BusinessModelSection."
    )
    try:
        agent = get_business_model_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        section = _require_structured(result, BusinessModelSection)
        sic_codes = section.sic_codes or company.get("sic_codes") or []
        level = business_model_confidence(sic_codes=sic_codes)
        section = section.model_copy(update={"confidence": level})
        section, citation_gaps = apply_citation_filter(
            section,
            company=company,
            messages=result.get("messages"),
            pillar_label="Business model",
            peers_ok=False,
        )
        gaps = list(state.get("gaps") or [])
        if level == "low":
            gaps = merge_gaps(
                gaps,
                [
                    "Business model confidence is low (no SIC codes)",
                    "Business model lacks SIC grounding",
                ],
            )
        gaps = merge_gaps(gaps, citation_gaps)
        conf = update_confidence(state.get("confidence"), business_model=level)
        logger.info(
            "pillar=business_model done company_number=%s confidence=%s",
            number,
            level,
        )
        return {
            "business_model": dumps_section(section),
            "confidence": conf,
            "gaps": gaps,
            "stage": "competition",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("pillar=business_model failed company_number=%s", number)
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
    logger.info("pillar=competition start company_number=%s", number)
    prompt = (
        f"Assess competition for company_number={number}.\n"
        f"Profile:\n{json.dumps(company)}\n"
        f"Business model section:\n{json.dumps(bm)}\n"
        "Use search_peers first, then web_search with competitor queries and at least one "
        "query that includes the company name plus address or locality to confirm identity. "
        "Return CompetitionSection."
    )
    try:
        agent = get_competition_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        section = _require_structured(result, CompetitionSection)
        peers = await search_peers(company_number=number)
        peer_set = [
            PeerCompany(
                company_name=item["company_name"],
                company_number=item.get("company_number"),
            )
            for item in peers.get("items") or []
            if item.get("company_name")
        ]
        peer_count = int(peers.get("total_results") or len(peer_set))
        arena_raw = peers.get("arena") or {}
        score = rivalry_score_from_peer_count(peer_count)
        section = section.model_copy(
            update={
                "arena": CompetitionArena(
                    sic_codes=list(arena_raw.get("sic_codes") or section.arena.sic_codes),
                    geography=arena_raw.get("geography") or section.arena.geography,
                ),
                "peer_set": peer_set,
                "peer_count_estimate": peer_count,
                "rivalry_score": score,
            }
        )
        section, citation_gaps = apply_citation_filter(
            section,
            company=company,
            messages=result.get("messages"),
            pillar_label="Competition",
            peers_ok=True,
        )
        has_peer_set = len(peer_set) > 0
        has_web_refs = web_search_mentions_company(
            result.get("messages"),
            str(company.get("company_name") or ""),
        )
        evidence = quality_web_evidence(result.get("messages"), company)
        has_profile_verify = evidence["profile_verify"]
        level = competition_confidence(
            has_peer_set=has_peer_set,
            has_web_company_refs=has_web_refs,
            has_profile_verify=has_profile_verify,
        )
        section = section.model_copy(
            update={
                "confidence": level,
                "confidence_factors": {
                    "peer_set": has_peer_set,
                    "web_company_refs": has_web_refs,
                    "profile_verify": has_profile_verify,
                },
            }
        )
        gaps = list(state.get("gaps") or [])
        if peers.get("empty_reason") == "no_sic_codes":
            gaps = merge_gaps(
                gaps,
                ["Company has no SIC codes; peer set unavailable"],
            )
        if level == "low":
            gaps = merge_gaps(gaps, ["Competition confidence is low (no peer set)"])
        gaps = merge_gaps(gaps, citation_gaps)
        conf = update_confidence(state.get("confidence"), competition=level)
        logger.info(
            "pillar=competition done company_number=%s peers=%s confidence=%s",
            number,
            peer_count,
            level,
        )
        return {
            "competition": dumps_section(section),
            "confidence": conf,
            "gaps": gaps,
            "stage": "quality",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("pillar=competition failed company_number=%s", number)
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
    logger.info("pillar=quality start company_number=%s", number)
    prompt = (
        f"Assess reputation/quality for company_number={number}.\n"
        f"Profile:\n{json.dumps(company)}\n"
        f"Competition arena (context):\n{json.dumps((competition or {}).get('arena'))}\n"
        "Mandatory: web_search site:trustpilot.com and a trade/news press query for this "
        "company, plus at least one query with name + address/locality. Return QualitySection."
    )
    try:
        agent = get_reputation_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        section = _require_structured(result, QualitySection)
        section, citation_gaps = apply_citation_filter(
            section,
            company=company,
            messages=result.get("messages"),
            pillar_label="Quality",
            peers_ok=False,
        )
        evidence = quality_web_evidence(
            result.get("messages"),
            company,
            citations=section.citations,
        )
        level = quality_confidence(
            has_trustpilot=evidence["trustpilot"],
            has_trade_press=evidence["trade_press"],
            has_profile_verify=evidence["profile_verify"],
        )
        section = _sanitize_quality_section(
            section,
            has_trustpilot=evidence["trustpilot"],
            has_trade_press=evidence["trade_press"],
        )
        section = section.model_copy(
            update={
                "confidence": level,
                "confidence_factors": {
                    "trustpilot": evidence["trustpilot"],
                    "trade_press": evidence["trade_press"],
                    "profile_verify": evidence["profile_verify"],
                },
            }
        )
        gaps = list(state.get("gaps") or [])
        if section.customer_rating is None:
            gaps = merge_gaps(gaps, ["No numeric customer rating found in web snippets"])
        if not evidence["trustpilot"]:
            gaps = merge_gaps(
                gaps,
                [
                    "No Trustpilot URL naming this company in web search results",
                ],
            )
        if not evidence["trustpilot"] and not evidence["trade_press"]:
            gaps = merge_gaps(
                gaps,
                [
                    "Neither Trustpilot.com nor a recognised trade-press URL "
                    "named this company in web search"
                ],
            )
        elif level == "low":
            gaps = merge_gaps(
                gaps,
                [
                    "Quality confidence is low (need attributable Trustpilot + a "
                    "trade-press domain naming the company, and profile corroboration)"
                ],
            )
        gaps = merge_gaps(gaps, citation_gaps)
        conf = update_confidence(state.get("confidence"), quality=level)
        logger.info(
            "pillar=quality done company_number=%s confidence=%s",
            number,
            level,
        )
        return {
            "quality": dumps_section(section),
            "confidence": conf,
            "gaps": gaps,
            "stage": "done",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("pillar=quality failed company_number=%s", number)
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
