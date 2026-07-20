"""Companies House HTTP client."""

import os
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_none,
)

BASE_URL = os.getenv(
    "COMPANIES_HOUSE_BASE_URL",
    "https://api.company-information.service.gov.uk",
)

_RETRYABLE_STATUS = {429, 502, 503}


def api_key() -> str:
    return os.getenv("COMPANIES_HOUSE_API_KEY", "").strip()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_none(),
    retry=(
        retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError),
        )
        | retry_if_result(lambda r: r.status_code in _RETRYABLE_STATUS)
    ),
    reraise=True,
)
async def get(path: str, params: dict[str, Any] | None = None) -> httpx.Response:
    clean = {k: v for k, v in (params or {}).items() if v is not None and v != ""}
    async with httpx.AsyncClient(timeout=20.0) as client:
        return await client.get(
            f"{BASE_URL}{path}",
            auth=(api_key(), ""),
            params=clean or None,
        )
