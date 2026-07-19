"""Company identity fields for the intelligence report."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompanyIdentity(BaseModel):
    """Enriched Companies House identity for the report header."""

    company_number: str = Field(description="Companies House registration number")
    company_name: str = Field(description="Registered company name")
    company_status: str | None = Field(default=None, description="e.g. active, dissolved")
    company_type: str | None = Field(default=None, description="Legal form / company type")
    date_of_creation: str | None = Field(default=None, description="Incorporation date YYYY-MM-DD")
    date_of_cessation: str | None = Field(default=None, description="Dissolution date if any")
    address_snippet: str | None = Field(default=None, description="Registered office summary")
    locality: str | None = Field(default=None, description="Town / city from registered address")
    region: str | None = Field(default=None, description="Region / county from registered address")
    country: str | None = Field(default=None, description="Country from registered address")
    sic_codes: list[str] | None = Field(
        default=None,
        description="SIC activity codes from Companies House profile",
    )
