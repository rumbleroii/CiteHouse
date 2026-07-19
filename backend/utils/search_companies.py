"""Companies House HTTP client."""

import os
from typing import Any

import httpx

BASE_URL = os.getenv(
    "COMPANIES_HOUSE_BASE_URL",
    "https://api.company-information.service.gov.uk",
)


def api_key() -> str:
    return os.getenv("COMPANIES_HOUSE_API_KEY", "").strip()


async def get(path: str, params: dict[str, Any] | None = None) -> httpx.Response:
    clean = {k: v for k, v in (params or {}).items() if v is not None and v != ""}
    async with httpx.AsyncClient(timeout=20.0) as client:
        return await client.get(
            f"{BASE_URL}{path}",
            auth=(api_key(), ""),
            params=clean or None,
        )
