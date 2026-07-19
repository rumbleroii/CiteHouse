"""Business model pillar of the company intelligence report."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schema.common import Citation, ConfidenceLevel


class BusinessModelSection(BaseModel):
    """How the company makes money and who it serves."""

    sic_codes: list[str] = Field(
        default_factory=list,
        description="SIC codes grounding the activity classification",
    )
    revenue_model_tags: list[str] = Field(
        default_factory=list,
        description="Tags such as B2B, B2C, retail, services, SaaS, marketplace",
    )
    customer_segments: list[str] = Field(
        default_factory=list,
        description="Who pays — e.g. SMB, enterprise, consumer, government",
    )
    products_services: list[str] = Field(
        default_factory=list,
        description="Named products or services offered",
    )
    summary: str = Field(description="5–8 sentence grounded business-model summary")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Evidence for this section",
    )
    confidence: ConfidenceLevel = Field(description="Confidence in this section")
