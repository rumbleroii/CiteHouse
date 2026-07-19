from fastapi import APIRouter

from services.search_companies import get_company_profile

router = APIRouter(tags=["company"])


@router.get("/company/{company_number}")
async def get_company(company_number: str):
    """Enriched Companies House profile including SIC codes."""
    return await get_company_profile(company_number)
