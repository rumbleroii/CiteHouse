"""LangChain tools for the intelligence agents."""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException
from langchain_core.tools import tool

from services.search_companies import get_company_profile as fetch_company_profile
from services.search_peers import search_peers as fetch_peers
from services.web_search import web_search as fetch_web_search

logger = logging.getLogger("citehouse.agents.intelligence.tools")


def _tool_error(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        detail = exc.detail
        message = detail if isinstance(detail, str) else str(detail)
    else:
        message = str(exc) or exc.__class__.__name__
    return json.dumps({"error": "tool_failed", "message": message})


@tool
async def get_company_profile(company_number: str) -> str:
    """Fetch enriched Companies House profile including SIC codes and address parts."""
    try:
        result = await fetch_company_profile(company_number)
        return json.dumps(result)
    except Exception as exc:  # noqa: BLE001
        logger.warning("get_company_profile failed: %s", exc)
        return _tool_error(exc)


@tool
async def search_peers(
    company_number: str | None = None,
    sic_codes: str | None = None,
    location: str | None = None,
) -> str:
    """Find all active peer companies sharing SIC codes (± location).

    Prefer company_number so SIC/geo are taken from the profile. Or pass
    comma-separated sic_codes (and optional location) explicitly.
    Returns every matching peer (paginated under the hood).
    """
    try:
        result = await fetch_peers(
            company_number=company_number,
            sic_codes=sic_codes,
            location=location,
        )
        return json.dumps(result)
    except Exception as exc:  # noqa: BLE001
        logger.warning("search_peers failed: %s", exc)
        return _tool_error(exc)


@tool
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the public web for company, competitor, review, or news evidence.

    Returns titled snippets with URLs suitable for citations.
    """
    try:
        result = await fetch_web_search(query, max_results=max_results)
        return json.dumps(result)
    except Exception as exc:  # noqa: BLE001
        logger.warning("web_search failed query=%r: %s", query[:80], exc)
        return _tool_error(exc)
