from fastapi import APIRouter

from services.intelligence_mock import get_mock_report

router = APIRouter(tags=["intelligence"])


@router.get("/intelligence/{company_number}")
async def get_intelligence_report(company_number: str):
    """Return a schema-valid intelligence report (mock pillars; live CH identity when available)."""
    report = await get_mock_report(company_number)
    return report.model_dump(exclude_none=True)
