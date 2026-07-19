from fastapi import APIRouter, HTTPException

from utils.companies_house import fetch_company
from utils.company_number import normalize_company_number

router = APIRouter(tags=["company"])


@router.get("/company/{company_number}")
async def get_company(company_number: str):
    normalized = normalize_company_number(company_number)
    if not normalized:
        raise HTTPException(
            status_code=400,
            detail="Invalid company number. Use 8 digits or a 2-letter prefix + 6 digits.",
        )

    return await fetch_company(normalized)
