"""Quality pillar of the company intelligence report."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schema.common import Citation, ConfidenceLevel, Polarity, TradePressTone


class CustomerRating(BaseModel):
    """Aggregate customer rating when found in public sources."""

    score: float | None = Field(default=None, description="Average rating score")
    scale: float | None = Field(default=None, description="Max scale, e.g. 5.0")
    n_reviews: int | None = Field(default=None, ge=0, description="Number of reviews")
    platforms: list[str] = Field(
        default_factory=list,
        description="Platforms contributing to the aggregate, e.g. Trustpilot",
    )


class ThemeSentiment(BaseModel):
    """A recurring theme from reviews or coverage."""

    theme: str = Field(description="Theme label, e.g. delivery, support, pricing")
    polarity: Polarity = Field(description="Overall polarity for this theme")
    evidence: str = Field(description="Short supporting quote or paraphrase")


class TradePress(BaseModel):
    """Trade / news press signal."""

    tone: TradePressTone = Field(description="Overall tone of trade/news coverage")
    notables: list[str] = Field(
        default_factory=list,
        description="Notable headlines or outlets",
    )


class QualityConfidenceFactors(BaseModel):
    """Deterministic signals used for quality confidence (pipeline-set)."""

    trustpilot: bool = Field(
        description=(
            "Attributable trustpilot.com/review/ page that names this company"
        ),
    )
    trade_press: bool = Field(
        description="web_search result URL is on a recognised trade/news domain and names the company",
    )
    profile_verify: bool = Field(
        description=(
            "Address/locality/number corroborated — only true when Trustpilot and "
            "trade press both already passed; otherwise treated as not found"
        ),
    )


class QualitySection(BaseModel):
    """Customer and trade-press quality profile."""

    customer_rating: CustomerRating | None = Field(
        default=None,
        description="Aggregate rating when evidence exists; null if not found",
    )
    theme_sentiment: list[ThemeSentiment] = Field(
        default_factory=list,
        description="Recurring themes from reviews/news snippets",
    )
    trade_press: TradePress = Field(description="Trade and news press signal")
    quality_score: int = Field(
        ge=1,
        le=5,
        description="Composite quality score 1 (poor) to 5 (strong)",
    )
    quality_rationale: str = Field(description="Short rationale for quality_score")
    summary: str = Field(
        description="2–3 sentence quality summary (keep brief)"
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="Evidence for this section",
    )
    confidence: ConfidenceLevel = Field(
        description="Overwritten by pipeline: medium if trustpilot.com + trade-press URL + profile verify, else low"
    )
    confidence_factors: QualityConfidenceFactors | None = Field(
        default=None,
        description="Pipeline ticks for Trustpilot, trade press, and profile corroboration",
    )
