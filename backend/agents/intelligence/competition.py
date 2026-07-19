"""Competition analysis ReAct agent — peers + web search."""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from agents.intelligence.llm import build_model
from agents.intelligence.prompts import COMPETITION_PROMPT
from schema.competition import CompetitionSection
from tools.intelligence import get_company_profile, search_peers, web_search

_agent = None


def get_competition_agent():
    global _agent
    if _agent is not None:
        return _agent
    _agent = create_react_agent(
        build_model(),
        tools=[get_company_profile, search_peers, web_search],
        prompt=COMPETITION_PROMPT,
        response_format=CompetitionSection,
    )
    return _agent
