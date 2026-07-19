"""Root company intelligence report — dashboard / agent output contract."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schema.business_model import BusinessModelSection
from schema.common import ConfidenceLevel
from schema.competition import CompetitionSection
from schema.identity import CompanyIdentity
from schema.quality import QualitySection


class ReportConfidence(BaseModel):
    """Per-pillar and overall confidence for the report."""

    overall: ConfidenceLevel = Field(description="Overall report confidence")
    business_model: ConfidenceLevel = Field(description="Business-model pillar confidence")
    competition: ConfidenceLevel = Field(description="Competition pillar confidence")
    quality: ConfidenceLevel = Field(description="Quality pillar confidence")


class CompanyIntelligenceReport(BaseModel):
    """Full P0 intelligence report — source of truth for API and dashboard."""

    company: CompanyIdentity = Field(description="Resolved company identity")
    business_model: BusinessModelSection = Field(description="Business model pillar")
    competition: CompetitionSection = Field(description="Competition pillar")
    quality: QualitySection = Field(description="Quality pillar")
    confidence: ReportConfidence = Field(description="Confidence breakdown")
    gaps: list[str] = Field(
        default_factory=list,
        description="What could not be evidenced or was omitted",
    )
