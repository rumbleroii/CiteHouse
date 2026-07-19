from pydantic import BaseModel, Field

from fastapi import APIRouter

from agents.company_search import run_agentic_search
from services.search_companies import search_by_company_number

router = APIRouter(tags=["search"])


class CandidateContext(BaseModel):
    company_number: str
    company_name: str
    company_status: str | None = None
    address_snippet: str | None = None


class AgenticSearchRequest(BaseModel):
    message: str = Field(..., min_length=1)
    prior_query: str | None = None
    candidates: list[CandidateContext] | None = None


@router.get("/search/by-company-number/{company_number}")
async def get_search_by_company_number(company_number: str):
    return await search_by_company_number(company_number)


@router.post("/search/agentic")
async def post_agentic_search(body: AgenticSearchRequest):
    return await run_agentic_search(
        body.message,
        prior_query=body.prior_query,
        candidates=[c.model_dump(exclude_none=True) for c in body.candidates]
        if body.candidates
        else None,
    )
