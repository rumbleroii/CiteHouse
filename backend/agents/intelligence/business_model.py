"""Business model ReAct agent — Companies House profile only."""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from agents.intelligence.llm import build_model
from agents.intelligence.prompts import BUSINESS_MODEL_PROMPT
from schema.business_model import BusinessModelSection
from agents.intelligence.tools import get_company_profile

_agent = None


def get_business_model_agent():
    global _agent
    if _agent is not None:
        return _agent
    _agent = create_react_agent(
        build_model(),
        tools=[get_company_profile],
        prompt=BUSINESS_MODEL_PROMPT,
        response_format=BusinessModelSection,
    )
    return _agent
