"""Tavily web search HTTP client."""

from __future__ import annotations

import os
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_none,
)

BASE_URL = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com").rstrip("/")

_RETRYABLE_STATUS = {429, 502, 503}


def api_key() -> str:
    return os.getenv("TAVILY_API_KEY", "").strip()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_none(),
    retry=(
        retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError),
        )
        | retry_if_result(
            lambda r: int(r.get("status_code") or 0) in _RETRYABLE_STATUS,
        )
    ),
    reraise=True,
)
async def search(
    query: str,
    *,
    max_results: int = 5,
    include_answer: bool = False,
) -> dict[str, Any]:
    """POST /search — returns status_code + parsed body."""
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
    try:
        body = response.json() if response.content else {}
    except ValueError:
        body = {}
    return {"status_code": response.status_code, "body": body}
