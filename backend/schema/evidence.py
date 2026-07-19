"""Web search evidence item (raw tool output, not agent judgment)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WebEvidenceItem(BaseModel):
    title: str = Field(description="Result title")
    url: str = Field(description="Result URL")
    content: str = Field(default="", description="Snippet / content from search")
    score: float | None = Field(default=None, description="Provider relevance score if any")
    query: str | None = Field(default=None, description="Search query that produced this hit")
