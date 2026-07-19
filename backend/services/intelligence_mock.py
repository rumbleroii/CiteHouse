"""Load schema-valid mock intelligence reports for pre-agent UI demos."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException

from schema.identity import CompanyIdentity
from schema.report import CompanyIntelligenceReport
from services.search_companies import get_company_profile

_FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_intelligence_report.json"
)


@lru_cache(maxsize=1)
def load_fixture() -> CompanyIntelligenceReport:
    if not _FIXTURE_PATH.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Intelligence fixture missing at {_FIXTURE_PATH}",
        )
    raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return CompanyIntelligenceReport.model_validate(raw)


def _identity_from_profile(profile: dict) -> CompanyIdentity:
    return CompanyIdentity.model_validate(profile)


async def get_mock_report(company_number: str) -> CompanyIntelligenceReport:
    """Return fixture pillars with `company` overwritten from Companies House when possible."""
    number = company_number.strip().upper()
    if not number:
        raise HTTPException(status_code=400, detail="company_number is required")

    report = load_fixture().model_copy(deep=True)

    try:
        profile = await get_company_profile(number)
        report.company = _identity_from_profile(profile)
    except HTTPException:
        # Keep fixture identity; still stamp the requested number when CH fails.
        report.company = report.company.model_copy(update={"company_number": number})

    return report
