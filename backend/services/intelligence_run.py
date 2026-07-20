"""Start / track / stream sequential intelligence graph runs."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, AsyncIterator

from agents.intelligence.graph import get_intelligence_graph
from agents.intelligence.state import (
    IntelligenceState,
    initial_state,
    state_to_partial_report,
)

_RUNS: dict[str, dict[str, Any]] = {}
_RUNS_DIR = Path(__file__).resolve().parent.parent / ".runs"


def _persist(run_id: str, state: IntelligenceState) -> None:
    _RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = _RUNS_DIR / f"{run_id}.json"
    path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    record = _RUNS.get(run_id) or {}
    record["state"] = state
    record["report"] = state_to_partial_report(state)
    _RUNS[run_id] = record


def get_run(run_id: str) -> dict[str, Any] | None:
    return _RUNS.get(run_id)


async def _execute_run(run_id: str, company_number: str) -> None:
    record = _RUNS[run_id]
    queue: asyncio.Queue = record["queue"]
    graph = get_intelligence_graph()
    state = initial_state(company_number)
    _persist(run_id, state)
    await queue.put({"event": "stage", "data": {"stage": state["stage"]}})

    try:
        async for update in graph.astream(state, stream_mode="updates"):
            for _node, partial in update.items():
                if not isinstance(partial, dict):
                    continue
                state = {**state, **partial}  # type: ignore[misc]
                _persist(run_id, state)
                stage = state.get("stage")
                await queue.put({"event": "stage", "data": {"stage": stage}})
                if state.get("error"):
                    await queue.put(
                        {"event": "run_error", "data": {"detail": state["error"]}},
                    )
                    await queue.put(None)
                    return
                report = state_to_partial_report(state)
                await queue.put({"event": "report", "data": report})
                if stage == "done":
                    await queue.put({"event": "done", "data": report})
                    await queue.put(None)
                    return

        # If stream ended without done
        if state.get("stage") == "done":
            report = state_to_partial_report(state)
            await queue.put({"event": "done", "data": report})
        elif state.get("stage") != "error":
            await queue.put(
                {
                    "event": "run_error",
                    "data": {"detail": "Graph ended before completion"},
                },
            )
    except Exception as exc:  # noqa: BLE001
        state = {**state, "stage": "error", "error": str(exc)}  # type: ignore[misc]
        _persist(run_id, state)
        await queue.put({"event": "run_error", "data": {"detail": str(exc)}})
    finally:
        await queue.put(None)


def start_run(company_number: str) -> str:
    number = company_number.strip().upper()
    run_id = uuid.uuid4().hex
    queue: asyncio.Queue = asyncio.Queue()
    _RUNS[run_id] = {
        "company_number": number,
        "queue": queue,
        "state": initial_state(number),
        "report": None,
    }
    asyncio.create_task(_execute_run(run_id, number))
    return run_id


async def stream_run_events(run_id: str) -> AsyncIterator[dict[str, Any]]:
    record = _RUNS.get(run_id)
    if not record:
        yield {"event": "run_error", "data": {"detail": "Unknown run_id"}}
        return

    # Replay current snapshot first so late subscribers see progress
    state = record.get("state")
    if state:
        yield {"event": "stage", "data": {"stage": state.get("stage")}}
        if state.get("company"):
            yield {"event": "report", "data": state_to_partial_report(state)}
        if state.get("stage") == "done":
            yield {"event": "done", "data": state_to_partial_report(state)}
            return
        if state.get("stage") == "error":
            yield {"event": "run_error", "data": {"detail": state.get("error") or "error"}}
            return

    queue: asyncio.Queue = record["queue"]
    while True:
        item = await queue.get()
        if item is None:
            break
        yield item
