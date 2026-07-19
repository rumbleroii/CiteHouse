from fastapi import APIRouter, Query

from services.search_companies import (
    advanced_search,
    search_by_company_name,
    search_by_company_number,
)
from services.search_peers import search_peers

router = APIRouter(tags=["search"])


@router.get("/search/by-company-name")
async def get_search_by_company_name(
    q: str = Query(..., min_length=1, description="Company name search term"),
    items_per_page: int | None = Query(None, ge=1, le=100),
    start_index: int | None = Query(None, ge=0),
    restrictions: str | None = None,
):
    return await search_by_company_name(
        q,
        items_per_page=items_per_page,
        start_index=start_index,
        restrictions=restrictions,
    )


@router.get("/search/advanced")
async def get_advanced_search(
    company_name_includes: str | None = None,
    company_name_excludes: str | None = None,
    company_status: str | None = None,
    company_subtype: str | None = None,
    company_type: str | None = None,
    dissolved_from: str | None = None,
    dissolved_to: str | None = None,
    incorporated_from: str | None = None,
    incorporated_to: str | None = None,
    location: str | None = None,
    sic_codes: str | None = None,
    size: int | None = Query(None, ge=1, le=5000),
    start_index: int | None = Query(None, ge=0),
):
    return await advanced_search(
        {
            "company_name_includes": company_name_includes,
            "company_name_excludes": company_name_excludes,
            "company_status": company_status,
            "company_subtype": company_subtype,
            "company_type": company_type,
            "dissolved_from": dissolved_from,
            "dissolved_to": dissolved_to,
            "incorporated_from": incorporated_from,
            "incorporated_to": incorporated_to,
            "location": location,
            "sic_codes": sic_codes,
            "size": size,
            "start_index": start_index,
        }
    )


@router.get("/search/by-company-number/{company_number}")
async def get_search_by_company_number(company_number: str):
    return await search_by_company_number(company_number)


@router.get("/search/peers")
async def get_search_peers(
    company_number: str | None = Query(
        None,
        description="Seed company — SIC and geography derived from its profile",
    ),
    sic_codes: str | None = Query(
        None,
        description="Comma-separated SIC codes (optional if company_number is set)",
    ),
    location: str | None = Query(
        None,
        description="Optional geography override (locality / region)",
    ),
    size: int = Query(10, ge=1, le=50),
):
    return await search_peers(
        company_number=company_number,
        sic_codes=sic_codes,
        location=location,
        size=size,
    )
