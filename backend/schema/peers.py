"""Peer evidence from Companies House advanced search (not rivalry scores)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schema.competition import CompetitionArena, PeerCompany


class PeerEvidence(BaseModel):
    """Active peers sharing SIC (± geography) from Companies House."""

    arena: CompetitionArena = Field(description="SIC × geography slice used")
    total_results: int = Field(ge=0, description="CH advanced-search total_results")
    items: list[PeerCompany] = Field(default_factory=list, description="Peer company hits")
    seed_company_number: str | None = Field(
        default=None,
        description="Company excluded from the peer list",
    )
