"""Find peer companies by shared SIC (± geography) via Companies House advanced search."""

from __future__ import annotations

from fastapi import HTTPException

from services.search_companies import advanced_search, get_company_profile

DEFAULT_PEER_SIZE = 10


def _geography_from_profile(profile: dict) -> str | None:
    return profile.get("locality") or profile.get("region") or profile.get("country")


async def search_peers(
    *,
    company_number: str | None = None,
    sic_codes: str | None = None,
    location: str | None = None,
    size: int = DEFAULT_PEER_SIZE,
) -> dict:
    """Return active peers sharing SIC codes, optionally narrowed by location.

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

    # Fetch a few extras so excluding the seed still fills `size`.
    fetch_size = min(max(size + (3 if exclude_number else 0), size), 100)
    result = await advanced_search(
        {
            "sic_codes": ",".join(arena_codes),
            "location": geography,
            "company_status": "active",
            "size": fetch_size,
        }
    )

    items = [
        item
        for item in result.get("items") or []
        if not exclude_number
        or str(item.get("company_number", "")).upper() != exclude_number.upper()
    ][:size]

    return {
        "arena": {
            "sic_codes": arena_codes,
            "geography": geography,
        },
        "seed_company_number": exclude_number,
        "total_results": result.get("total_results", len(items)),
        "items": items,
    }
