"""Tavily web search HTTP client."""

from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com").rstrip("/")


def api_key() -> str:
    return os.getenv("TAVILY_API_KEY", "").strip()


async def search(
    query: str,
    *,
    max_results: int = 5,
    include_answer: bool = False,
) -> dict[str, Any]:
    """POST /search — returns the raw Tavily JSON payload."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key()}",
    }
    payload = {
        "query": query,
        "max_results": max_results,
        "include_answer": include_answer,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{BASE_URL}/search",
            headers=headers,
            json=payload,
        )
    return {"status_code": response.status_code, "body": response.json() if response.content else {}}
