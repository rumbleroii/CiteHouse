"""Competition pillar of the company intelligence report."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schema.common import Citation, ConfidenceLevel


class CompetitionArena(BaseModel):
    """Defined competitive slice: SIC cluster × geography."""

    sic_codes: list[str] = Field(description="SIC codes defining the arena")
    geography: str | None = Field(
        default=None,
        description="Locality, region, or country used for the peer search",
    )


class PeerCompany(BaseModel):
    """A peer competitor from Companies House or web evidence."""

    company_name: str = Field(description="Peer company name")
    company_number: str | None = Field(
        default=None,
        description="Companies House number when known",
    )


class CompetitionConfidenceFactors(BaseModel):
    """Deterministic signals used for competition confidence (pipeline-set)."""

    peer_set: bool = Field(description="True when Companies House returned peers")
    web_company_refs: bool = Field(
        description="True when web_search hits mention the company name",
    )
    profile_verify: bool = Field(
        default=False,
        description="At least one web hit also matches address/locality/number from the profile",
    )


class CompetitionSection(BaseModel):
    """Structured view of rivalry intensity in the defined arena."""

    arena: CompetitionArena = Field(description="SIC × geography slice used for peers")
    peer_set: list[PeerCompany] = Field(
        default_factory=list,
        description="All peer companies from Companies House for the arena",
    )
    peer_count_estimate: int = Field(
        ge=0,
        description="Companies House advanced-search total_results for the arena",
    )
    peer_count_confidence: ConfidenceLevel = Field(
        description="Confidence in the peer count estimate",
    )
    rivalry_score: int = Field(
        ge=1,
        le=5,
        description="Overwritten by pipeline from peer_count_estimate (1–5)",
    )
    rivalry_evidence: list[str] = Field(
        default_factory=list,
        description="Short evidence bullets supporting rivalry_score",
    )
    summary: str = Field(
        description="2–3 sentence competition summary (keep brief)"
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="Evidence for this section",
    )
    confidence: ConfidenceLevel = Field(
        description="Overwritten by pipeline: high if peers+web+profile verify, medium if peers only, else low"
    )
    confidence_factors: CompetitionConfidenceFactors | None = Field(
        default=None,
        description="Pipeline ticks for peer set and web company-name references",
    )
