"""LangGraph agent that finds the right UK company from natural language."""

from __future__ import annotations

import json
import os
from typing import Literal

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from services.search_companies import (
    advanced_search,
    search_by_company_name,
    search_by_company_number,
)

SYSTEM_PROMPT = """You help users find the correct UK company on Companies House.

Use the search tools. Results are already slim (name, number, status, type, dates, address).

Rules:
- Prefer active companies unless the user asks for dissolved/closed ones.
- Start with search_companies for a plain name. Use filter_companies when the user gives
  filters: location, status, legal type/subtype, SIC/business activity, incorporation or
  dissolution dates, or name includes/excludes.
- If one result clearly matches, set status=found and fill company_number.
- If several could match, set status=needs_clarification, put likely company_numbers in candidates, and ask a short clarifying question (location, status, year, SIC, etc.).
- If nothing useful is found, set status=not_found and clearly say no matching company was found. Do not ask for follow-up details when nothing matched.
- When the user sends a follow-up with prior candidates, use that context and search again to resolve to one company.
- Never invent company numbers. Only use numbers returned by tools.
"""


class CompanyHit(BaseModel):
    company_number: str
    company_name: str
    company_status: str | None = None
    company_type: str | None = None
    date_of_creation: str | None = None
    date_of_cessation: str | None = None
    address_snippet: str | None = None
    locality: str | None = None
    region: str | None = None
    country: str | None = None
    sic_codes: list[str] | None = None


class AgentDecision(BaseModel):
    status: Literal["found", "needs_clarification", "not_found"]
    message: str = Field(description="Short message for the user")
    company_number: str | None = Field(
        default=None,
        description="Selected company number when status is found",
    )
    candidates: list[str] = Field(
        default_factory=list,
        description="Candidate company numbers when clarifying",
    )


@tool
async def search_companies(query: str) -> str:
    """Search Companies House by company name or free-text query."""
    result = await search_by_company_name(query, items_per_page=10)
    return json.dumps(result)


@tool
async def filter_companies(
    company_name_includes: str | None = None,
    company_name_excludes: str | None = None,
    company_status: str | None = None,
    company_subtype: str | None = None,
    company_type: str | None = None,
    location: str | None = None,
    sic_codes: str | None = None,
    incorporated_from: str | None = None,
    incorporated_to: str | None = None,
    dissolved_from: str | None = None,
    dissolved_to: str | None = None,
) -> str:
    """Advanced Companies House search with optional filters.

    Use for refining by location, status, legal type/subtype, SIC codes
    (business activity), incorporation/dissolution date ranges (YYYY-MM-DD),
    or name includes/excludes. Comma-separate multiple statuses, types, or SIC codes.
    """
    result = await advanced_search(
        {
            "company_name_includes": company_name_includes,
            "company_name_excludes": company_name_excludes,
            "company_status": company_status,
            "company_subtype": company_subtype,
            "company_type": company_type,
            "location": location,
            "sic_codes": sic_codes,
            "incorporated_from": incorporated_from,
            "incorporated_to": incorporated_to,
            "dissolved_from": dissolved_from,
            "dissolved_to": dissolved_to,
            "size": 10,
        }
    )
    return json.dumps(result)


@tool
async def get_company(company_number: str) -> str:
    """Fetch one company by exact Companies House registration number (includes SIC)."""
    result = await search_by_company_number(company_number)
    return json.dumps(result)


_agent = None


def get_agent():
    global _agent
    if _agent is not None:
        return _agent

    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is not configured")

    model_name = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip() or "gpt-5.6-luna"
    # Luna rejects function tools on chat completions unless reasoning is off.
    model = ChatOpenAI(model=model_name, reasoning_effort="none")
    _agent = create_react_agent(
        model,
        tools=[search_companies, filter_companies, get_company],
        prompt=SYSTEM_PROMPT,
        response_format=AgentDecision,
    )
    return _agent
