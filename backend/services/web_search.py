"""Normalize Tavily search results for agents and API consumers."""

from __future__ import annotations

import httpx
from fastapi import HTTPException

from utils import web_search as tavily

DEFAULT_MAX_RESULTS = 5


async def web_search(query: str, *, max_results: int = DEFAULT_MAX_RESULTS) -> dict:
    text = (query or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="q is required")

    if not tavily.api_key():
        raise HTTPException(status_code=500, detail="TAVILY_API_KEY is not configured")

    limit = max(1, min(max_results, 20))
    try:
        raw = await tavily.search(text, max_results=limit)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=503,
            detail="Web search timed out. Please try again.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Web search is unavailable. Please try again.",
        ) from exc

    status = raw["status_code"]
    body = raw.get("body") or {}

    if status == 401:
        raise HTTPException(status_code=502, detail="Tavily rejected the API key")
    if status == 429:
        raise HTTPException(
            status_code=503,
            detail="Web search rate limit exceeded. Please try again shortly.",
        )
    if status >= 400:
        detail = body.get("detail") or body.get("error") or f"Web search failed ({status})"
        if isinstance(detail, dict):
            detail = detail.get("error") or str(detail)
        raise HTTPException(status_code=502, detail=str(detail))

    results = []
    for item in body.get("results") or []:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        title = item.get("title")
        if not url or not title:
            continue
        hit = {
            "title": title,
            "url": url,
            "content": item.get("content") or item.get("snippet") or "",
        }
        if item.get("score") is not None:
            hit["score"] = item["score"]
        results.append(hit)

    payload: dict = {
        "query": body.get("query") or text,
        "results": results,
    }
    if body.get("answer"):
        payload["answer"] = body["answer"]
    return payload
