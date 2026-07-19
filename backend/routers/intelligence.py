import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services.intelligence_run import (
    get_latest_report_for_company,
    get_run,
    start_run,
    stream_run_events,
)

router = APIRouter(tags=["intelligence"])


@router.post("/intelligence/{company_number}/runs")
async def create_intelligence_run(company_number: str):
    """Start sequential BusinessModel → Competition → Quality agents."""
    number = company_number.strip().upper()
    if not number:
        raise HTTPException(status_code=400, detail="company_number is required")
    try:
        run_id = start_run(number)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"run_id": run_id, "company_number": number}


@router.get("/intelligence/runs/{run_id}/stream")
async def stream_intelligence_run(run_id: str):
    """SSE stream of stage/report/error/done events for a run."""
    if not get_run(run_id):
        raise HTTPException(status_code=404, detail="Unknown run_id")

    async def event_generator():
        async for item in stream_run_events(run_id):
            event = item.get("event", "message")
            data = item.get("data", {})
            yield f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/intelligence/runs/{run_id}")
async def get_intelligence_run(run_id: str):
    record = get_run(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown run_id")
    state = record.get("state") or {}
    return {
        "run_id": run_id,
        "company_number": record.get("company_number"),
        "stage": state.get("stage"),
        "error": state.get("error"),
        "report": record.get("report") or state,
    }


@router.get("/intelligence/{company_number}")
async def get_intelligence_report(company_number: str):
    """Latest completed report for a company, if any."""
    report = get_latest_report_for_company(company_number)
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No completed intelligence report for this company yet",
        )
    return report
