"""Reputation / quality ReAct agent — web reviews and trade press."""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from agents.intelligence.llm import build_model
from agents.intelligence.prompts import REPUTATION_PROMPT
from schema.quality import QualitySection
from agents.intelligence.tools import get_company_profile, web_search

_agent = None


def get_reputation_agent():
    global _agent
    if _agent is not None:
        return _agent
    _agent = create_react_agent(
        build_model(),
        tools=[web_search, get_company_profile],
        prompt=REPUTATION_PROMPT,
        response_format=QualitySection,
    )
    return _agent
