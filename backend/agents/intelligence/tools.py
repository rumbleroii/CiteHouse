"""LangChain tools for the intelligence agents."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from services.search_companies import get_company_profile as fetch_company_profile
from services.search_peers import search_peers as fetch_peers
from services.web_search import web_search as fetch_web_search


@tool
async def get_company_profile(company_number: str) -> str:
    """Fetch enriched Companies House profile including SIC codes and address parts."""
    result = await fetch_company_profile(company_number)
    return json.dumps(result)


@tool
async def search_peers(
    company_number: str | None = None,
    sic_codes: str | None = None,
    location: str | None = None,
    size: int = 10,
) -> str:
    """Find active peer companies sharing SIC codes (± location).

    Prefer company_number so SIC/geo are taken from the profile. Or pass
    comma-separated sic_codes (and optional location) explicitly.
    """
    result = await fetch_peers(
        company_number=company_number,
        sic_codes=sic_codes,
        location=location,
        size=size,
    )
    return json.dumps(result)


@tool
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the public web for company, competitor, review, or news evidence.

    Returns titled snippets with URLs suitable for citations.
    """
    result = await fetch_web_search(query, max_results=max_results)
    return json.dumps(result)
