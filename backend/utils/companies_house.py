import os

import httpx
from fastapi import HTTPException

BASE_URL = os.getenv(
    "COMPANIES_HOUSE_BASE_URL",
    "https://api.company-information.service.gov.uk",
)


def _api_key() -> str:
    key = os.getenv("COMPANIES_HOUSE_API_KEY", "").strip()
    if not key:
        raise HTTPException(
            status_code=500,
            detail="COMPANIES_HOUSE_API_KEY is not configured",
        )
    return key


async def fetch_company(company_number: str) -> dict:
    """Fetch company profile (includes company_name) and registered office address."""
    key = _api_key()
    auth = (key, "")

    async with httpx.AsyncClient(timeout=20.0) as client:
        address_res = await client.get(
            f"{BASE_URL}/company/{company_number}/registered-office-address",
            auth=auth,
        )
        profile_res = await client.get(
            f"{BASE_URL}/company/{company_number}",
            auth=auth,
        )

    if address_res.status_code == 401 or profile_res.status_code == 401:
        raise HTTPException(
            status_code=502,
            detail="Companies House API rejected the API key",
        )

    if address_res.status_code == 404 or profile_res.status_code == 404:
        raise HTTPException(status_code=404, detail="Company not found")

    if address_res.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Companies House address lookup failed ({address_res.status_code})",
        )

    if profile_res.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Companies House company lookup failed ({profile_res.status_code})",
        )

    profile = profile_res.json()
    address = address_res.json()
    company_name = profile.get("company_name")
    if not company_name:
        raise HTTPException(
            status_code=502,
            detail="Companies House response missing company_name",
        )

    return {
        "company_number": company_number,
        "company_name": company_name,
        "registered_office_address": address,
    }
