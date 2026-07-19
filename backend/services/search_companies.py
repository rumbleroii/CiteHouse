"""Slim Companies House search — only the fields an agent needs."""

from typing import Any

from fastapi import HTTPException

from utils import search_companies as ch

DEFAULT_PAGE_SIZE = 10


async def _fetch(path: str, params: dict[str, Any] | None = None, *, not_found: str = "Not found") -> dict:
    if not ch.api_key():
        raise HTTPException(status_code=500, detail="COMPANIES_HOUSE_API_KEY is not configured")

    response = await ch.get(path, params)
    if response.status_code == 401:
        raise HTTPException(status_code=502, detail="Companies House API rejected the API key")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=not_found)
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Companies House request failed for {path} ({response.status_code})",
        )
    return response.json()


def _slim(item: dict) -> dict:
    name = item.get("title") or item.get("company_name")
    number = item.get("company_number")
    if not name or not number:
        raise HTTPException(
            status_code=502,
            detail="Companies House response missing company name or number",
        )

    snippet = item.get("address_snippet")
    if not snippet:
        address = item.get("address") or item.get("registered_office_address") or {}
        if isinstance(address, dict):
            parts = [
                address[k]
                for k in (
                    "care_of",
                    "address_line_1",
                    "address_line_2",
                    "locality",
                    "region",
                    "postal_code",
                    "country",
                )
                if address.get(k)
            ]
            snippet = ", ".join(parts) if parts else None

    slim = {
        "company_number": number,
        "company_name": name,
        "company_status": item.get("company_status"),
        "company_type": item.get("company_type") or item.get("type"),
        "date_of_creation": item.get("date_of_creation"),
        "date_of_cessation": item.get("date_of_cessation"),
        "address_snippet": snippet,
    }
    return {k: v for k, v in slim.items() if v}


def _as_list(data: dict) -> dict:
    items = [_slim(item) for item in data.get("items") or [] if isinstance(item, dict)]
    return {
        "total_results": data.get("total_results", len(items)),
        "items": items,
    }


async def search_by_company_name(
    q: str,
    *,
    items_per_page: int | None = None,
    start_index: int | None = None,
    restrictions: str | None = None,
) -> dict:
    data = await _fetch(
        "/search/companies",
        {
            "q": q,
            "items_per_page": items_per_page or DEFAULT_PAGE_SIZE,
            "start_index": start_index,
            "restrictions": restrictions,
        },
    )
    return _as_list(data)


async def advanced_search(filters: dict[str, Any]) -> dict:
    params = {**filters, "size": filters.get("size") or DEFAULT_PAGE_SIZE}
    data = await _fetch("/advanced-search/companies", params)
    return _as_list(data)


async def search_by_company_number(company_number: str) -> dict:
    number = company_number.strip().upper()
    data = await _fetch("/search/companies", {"q": number, "items_per_page": 20})

    for item in data.get("items") or []:
        if str(item.get("company_number", "")).upper() == number:
            return _slim(item)

    profile = await _fetch(f"/company/{number}", not_found="Company not found")
    return _slim(profile)
