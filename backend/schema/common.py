"""Shared types for company intelligence schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ConfidenceLevel = Literal["high", "medium", "low"]
Polarity = Literal["positive", "neutral", "negative", "mixed"]
TradePressTone = Literal["positive", "neutral", "negative", "mixed"]


class Citation(BaseModel):
    """Provenance for a claim. Prefer URL; use source_ref for CH field paths."""

    title: str | None = Field(default=None, description="Page or document title")
    url: str | None = Field(default=None, description="Public URL when from web search")
    source_ref: str | None = Field(
        default=None,
        description="Non-URL provenance, e.g. companies_house:profile.sic_codes",
    )
    snippet: str | None = Field(default=None, description="Short supporting excerpt")
