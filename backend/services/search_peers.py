"""Find peer companies by shared SIC (± geography) via Companies House advanced search."""

from __future__ import annotations

from fastapi import HTTPException

from services.search_companies import advanced_search, get_company_profile

# Page size for each CH request (API paging), not a cap on total peers returned.
_PAGE_SIZE = 100


def _geography_from_profile(profile: dict) -> str | None:
    return profile.get("locality") or profile.get("region") or profile.get("country")


async def search_peers(
    *,
    company_number: str | None = None,
    sic_codes: str | None = None,
    location: str | None = None,
) -> dict:
    """Return all active peers sharing SIC codes, optionally narrowed by location.

    Provide either `company_number` (SIC/geo derived from profile) or explicit
    `sic_codes` (comma-separated). The seed company is excluded from `items`.
    """
    exclude_number: str | None = None
    arena_codes: list[str] = []
    geography = (location or "").strip() or None

    if company_number:
        profile = await get_company_profile(company_number)
        exclude_number = profile["company_number"]
        profile_codes = profile.get("sic_codes") or []
        if not isinstance(profile_codes, list):
            profile_codes = []
        if not sic_codes:
            if not profile_codes:
                raise HTTPException(
                    status_code=400,
                    detail="Company has no SIC codes; cannot search peers",
                )
            arena_codes = [str(c) for c in profile_codes]
            sic_codes = ",".join(arena_codes)
        if not geography:
            geography = _geography_from_profile(profile)

    if not sic_codes or not str(sic_codes).strip():
        raise HTTPException(
            status_code=400,
            detail="sic_codes or company_number with SIC codes is required",
        )

    if not arena_codes:
        arena_codes = [c.strip() for c in str(sic_codes).split(",") if c.strip()]

    base_filters = {
        "sic_codes": ",".join(arena_codes),
        "location": geography,
        "company_status": "active",
    }

    collected: list[dict] = []
    start_index = 0
    total_results = 0

    while True:
        result = await advanced_search(
            {
                **base_filters,
                "size": _PAGE_SIZE,
                "start_index": start_index,
            }
        )
        if start_index == 0:
            total_results = int(result.get("total_results") or 0)
        page = [item for item in (result.get("items") or []) if isinstance(item, dict)]
        if not page:
            break
        collected.extend(page)
        start_index += len(page)
        if start_index >= total_results or len(page) < _PAGE_SIZE:
            break

    items = [
        item
        for item in collected
        if not exclude_number
        or str(item.get("company_number", "")).upper() != exclude_number.upper()
    ]

    return {
        "arena": {
            "sic_codes": arena_codes,
            "geography": geography,
        },
        "seed_company_number": exclude_number,
        "total_results": total_results,
        "items": items,
    }
