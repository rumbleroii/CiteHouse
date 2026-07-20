"""Post-agent citation allowlisting: tool URLs + Companies House source_refs."""

from __future__ import annotations

import json
from typing import Any, Sequence
from urllib.parse import urlsplit, urlunsplit

from schema.common import Citation

ALLOWED_CH_SOURCE_REFS = frozenset(
    {
        "companies_house:profile",
        "companies_house:profile.sic_codes",
        "companies_house:profile.company_type",
        "companies_house:profile.company_status",
        "companies_house:profile.address",
        "companies_house:search_peers",
        "companies_house:advanced-search.total_results",
    }
)


def normalize_url(url: str) -> str:
    text = (url or "").strip()
    if not text:
        return ""
    parts = urlsplit(text)
    scheme = (parts.scheme or "https").lower()
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or ""
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def _message_text(content: Any) -> str | None:
    if isinstance(content, str) and content.strip():
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text") or ""))
            elif isinstance(block, str):
                parts.append(block)
        text = "".join(parts)
        return text if text.strip() else None
    return None


def _iter_web_search_payloads(messages: Sequence[Any] | None):
    """Only real web_search tool messages (not prompts / model text)."""
    for msg in messages or []:
        name = getattr(msg, "name", None) or (
            msg.get("name") if isinstance(msg, dict) else None
        )
        if name != "web_search":
            continue
        content = getattr(msg, "content", None)
        if content is None and isinstance(msg, dict):
            content = msg.get("content")
        text = _message_text(content)
        if not text:
            continue
        try:
            payload = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            yield payload


def extract_tool_urls(messages: Sequence[Any] | None) -> set[str]:
    """Collect URLs from web_search tool message JSON payloads."""
    urls: set[str] = set()
    for payload in _iter_web_search_payloads(messages):
        for item in payload.get("results") or []:
            if not isinstance(item, dict):
                continue
            raw = item.get("url")
            if isinstance(raw, str) and raw.strip():
                urls.add(normalize_url(raw))
    return urls


def _company_name_needles(company_name: str) -> list[str]:
    name = (company_name or "").strip().lower()
    if not name:
        return []
    needles = [name]
    # Also match without common legal suffixes.
    for suffix in (
        " limited",
        " ltd",
        " ltd.",
        " plc",
        " llp",
        " inc",
        " inc.",
        " company",
    ):
        if name.endswith(suffix):
            trimmed = name[: -len(suffix)].strip(" .,")
            if trimmed and trimmed not in needles:
                needles.append(trimmed)
            break
    return needles


def web_search_mentions_company(
    messages: Sequence[Any] | None,
    company_name: str,
) -> bool:
    """True if any web_search hit title/content/url mentions the company name."""
    needles = _company_name_needles(company_name)
    if not needles:
        return False
    for payload in _iter_web_search_payloads(messages):
        for item in payload.get("results") or []:
            if not isinstance(item, dict):
                continue
            blob = " ".join(
                str(item.get(k) or "")
                for k in ("title", "content", "url", "snippet")
            ).lower()
            if any(n in blob for n in needles):
                return True
    return False


# Host checks only — avoids false ticks from query text like '"{name}" Trustpilot'
# appearing in titles/snippets of unrelated pages.
_TRUSTPILOT_DOMAINS = ("trustpilot.com",)

_TRADE_PRESS_DOMAINS = (
    "thegrocer.co.uk",
    "ft.com",
    "reuters.com",
    "bloomberg.com",
    "bbc.co.uk",
    "theguardian.com",
    "telegraph.co.uk",
    "independent.co.uk",
    "cityam.com",
    "retailgazette.co.uk",
)


def _hit_blob(item: dict[str, Any]) -> str:
    return " ".join(
        str(item.get(k) or "") for k in ("title", "content", "url", "snippet")
    ).lower()


def _url_host(url: str) -> str:
    host = urlsplit((url or "").strip()).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _host_is_domain(host: str, domains: tuple[str, ...]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def _profile_corroborators(company: dict[str, Any]) -> list[str]:
    """Address / locality / number tokens used to confirm the right company."""
    out: list[str] = []
    for key in (
        "address_snippet",
        "locality",
        "region",
        "company_number",
        "country",
    ):
        val = company.get(key)
        if not val:
            continue
        text = str(val).strip().lower()
        if len(text) < 3:
            continue
        out.append(text)
        # Also use comma-separated address parts when long.
        if key == "address_snippet":
            for part in text.split(","):
                part = part.strip()
                if len(part) >= 4 and part not in out:
                    out.append(part)
    return out


def quality_web_evidence(
    messages: Sequence[Any] | None,
    company: dict[str, Any],
    *,
    citations: Sequence[Any] | None = None,
) -> dict[str, bool]:
    """Trustpilot and trade press use the same rule: allowed domain + company name.

    Also counts allowlisted citations so the UI tick cannot disagree with a
    shown Trustpilot/trade-press citation.
    """
    name_needles = _company_name_needles(str(company.get("company_name") or ""))
    profile_needles = _profile_corroborators(company)

    has_trustpilot = False
    has_trade_press = False
    has_profile_verify = False

    if not name_needles:
        return {
            "trustpilot": False,
            "trade_press": False,
            "profile_verify": False,
        }

    def _consider(blob: str, host: str) -> None:
        nonlocal has_trustpilot, has_trade_press, has_profile_verify
        names_company = any(n in blob for n in name_needles)
        if not names_company:
            return
        if _host_is_domain(host, _TRUSTPILOT_DOMAINS):
            has_trustpilot = True
        if _host_is_domain(host, _TRADE_PRESS_DOMAINS):
            has_trade_press = True
        if profile_needles and any(p in blob for p in profile_needles):
            has_profile_verify = True

    for payload in _iter_web_search_payloads(messages):
        for item in payload.get("results") or []:
            if not isinstance(item, dict):
                continue
            _consider(_hit_blob(item), _url_host(str(item.get("url") or "")))

    # Keep confidence ticks aligned with citations the pipeline already kept.
    for citation in citations or []:
        url = getattr(citation, "url", None)
        if url is None and isinstance(citation, dict):
            url = citation.get("url")
        url_text = str(url or "").strip()
        if not url_text:
            continue
        title = getattr(citation, "title", None)
        snippet = getattr(citation, "snippet", None)
        if isinstance(citation, dict):
            title = citation.get("title")
            snippet = citation.get("snippet")
        blob = " ".join(str(x or "") for x in (title, snippet, url_text)).lower()
        _consider(blob, _url_host(url_text))

    # Profile/address only counts once both mandatory sources are present;
    # if either Trustpilot or trade press failed, treat profile as not found.
    if not (has_trustpilot and has_trade_press):
        has_profile_verify = False

    return {
        "trustpilot": has_trustpilot,
        "trade_press": has_trade_press,
        "profile_verify": has_profile_verify,
    }


def _source_ref_ok(
    source_ref: str,
    *,
    company: dict[str, Any],
    peers_ok: bool,
) -> bool:
    ref = source_ref.strip()
    if ref not in ALLOWED_CH_SOURCE_REFS:
        return False

    if ref == "companies_house:profile":
        return bool(company.get("company_number") or company.get("company_name"))
    if ref.endswith(".sic_codes"):
        codes = company.get("sic_codes") or []
        return isinstance(codes, list) and len(codes) > 0
    if ref.endswith(".company_type"):
        return bool(company.get("company_type"))
    if ref.endswith(".company_status"):
        return bool(company.get("company_status"))
    if ref.endswith(".address"):
        return bool(
            company.get("address_snippet")
            or company.get("locality")
            or company.get("region")
            or company.get("country")
        )
    if ref in (
        "companies_house:search_peers",
        "companies_house:advanced-search.total_results",
    ):
        return peers_ok
    return False


def _citation_ok(
    citation: Citation,
    *,
    company: dict[str, Any],
    tool_urls: set[str],
    peers_ok: bool,
) -> bool:
    url = (citation.url or "").strip() or None
    source_ref = (citation.source_ref or "").strip() or None
    if not url and not source_ref:
        return False

    if source_ref and not _source_ref_ok(
        source_ref, company=company, peers_ok=peers_ok
    ):
        return False

    if url:
        if normalize_url(url) not in tool_urls:
            return False

    return True


def filter_citations(
    citations: Sequence[Citation] | None,
    *,
    company: dict[str, Any],
    tool_urls: set[str],
    peers_ok: bool = False,
) -> tuple[list[Citation], int]:
    """Return (kept, dropped_count)."""
    kept: list[Citation] = []
    dropped = 0
    for citation in citations or []:
        if _citation_ok(
            citation,
            company=company,
            tool_urls=tool_urls,
            peers_ok=peers_ok,
        ):
            kept.append(citation)
        else:
            dropped += 1
    return kept, dropped


def apply_citation_filter(
    section: Any,
    *,
    company: dict[str, Any],
    messages: Sequence[Any] | None,
    pillar_label: str,
    peers_ok: bool = False,
) -> tuple[Any, list[str]]:
    """Filter section.citations; return updated section and gap notes."""
    tool_urls = extract_tool_urls(messages)
    kept, dropped = filter_citations(
        getattr(section, "citations", None),
        company=company,
        tool_urls=tool_urls,
        peers_ok=peers_ok,
    )
    updated = section.model_copy(update={"citations": kept})
    gaps: list[str] = []
    if dropped:
        gaps.append(f"{pillar_label}: removed {dropped} ungrounded citation(s)")
    return updated, gaps
