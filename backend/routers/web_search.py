from fastapi import APIRouter, Query

from services.web_search import web_search

router = APIRouter(tags=["web-search"])


@router.get("/web-search")
async def get_web_search(
    q: str = Query(..., min_length=1, description="Search query"),
    max_results: int = Query(5, ge=1, le=20),
):
    return await web_search(q, max_results=max_results)
