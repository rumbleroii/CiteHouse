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


class CompetitionSection(BaseModel):
    """Structured view of rivalry intensity in the defined arena."""

    arena: CompetitionArena = Field(description="SIC × geography slice used for peers")
    peer_set: list[PeerCompany] = Field(
        default_factory=list,
        description="5–10 peer companies in the arena",
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
        description="Rivalry intensity 1 (low) to 5 (high)",
    )
    rivalry_evidence: list[str] = Field(
        default_factory=list,
        description="Short evidence bullets supporting rivalry_score",
    )
    summary: str = Field(description="Short competition summary")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Evidence for this section",
    )
    confidence: ConfidenceLevel = Field(description="Confidence in this section")
