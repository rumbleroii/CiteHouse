# Citehouse — System Design

This document describes the architectural approach and key design decisions for Citehouse, an agentic UK company intelligence system aligned with the Senior Product Engineer home-task brief:

- Accept a UK company name or Companies House registration number  
- Correctly identify the intended legal entity  
- Gather public data, extract structured evidence, and synthesise underwriting-relevant insights  
- Produce an explainable, citation-backed intelligence report  
- Demonstrate agent orchestration, data grounding, and uncertainty handling  

**Final report pillars required by the brief**

1. Business-model summary  
2. Structured view of competitive intensity (sector / geography as relevant)  
3. Structured view of company quality (customer / trade press signals)  

---

## 1. Goals and non-goals

### Goals

- Resolve ambiguous company names to a single Companies House legal entity before analysis.  
- Run a multi-step agent pipeline that lands evidence progressively for an underwriter-style review.  
- Prefer **deterministic** post-processing for confidence, rivalry, peers, and citation provenance over trusting the LLM alone.  
- Keep the UI explainable: structured fields, citations, and hoverable confidence criteria.

### Non-goals (current scope)

- Full financial statement underwriting or private data rooms.  
- Claim-level natural-language entailment (each sentence proven by a citation).  
- Multi-tenant auth, long-term warehouse storage, or production SLA hardening.  
- Scraping full web pages beyond search-snippet evidence.

---

## 2. High-level architecture

```
┌─────────────────────┐         ┌──────────────────────────────────────────┐
│  Next.js frontend   │  HTTP   │  FastAPI backend                         │
│  (App Router)       │────────▶│  /api/search/*                           │
│                     │  SSE    │  /api/intelligence/*                     │
│  Lookup  →  Report  │◀────────│                                          │
└─────────────────────┘         │  ┌────────────┐    ┌───────────────────┐ │
                                │  │ Company    │    │ Intelligence      │ │
                                │  │ search     │    │ LangGraph         │ │
                                │  │ ReAct agent│    │ profile→BM→comp→Q │ │
                                │  └─────┬──────┘    └─────────┬─────────┘ │
                                │        │                     │           │
                                │  ┌─────▼─────────────────────▼─────────┐ │
                                │  │ Services: CH search/profile/peers,  │ │
                                │  │ Tavily web search, run store         │ │
                                │  └─────┬─────────────────────┬─────────┘ │
                                └────────┼─────────────────────┼───────────┘
                                         │                     │
                              Companies House API        Tavily Search API
                              OpenAI Chat Completions    (web evidence)
```

| Layer | Role | Primary locations |
|--------|------|-------------------|
| **Frontend** | Entity lookup UX; progressive report dashboard | `frontend/` |
| **API** | Thin HTTP surface for search + intelligence runs | `backend/routers/` |
| **Agents** | ReAct tools + structured outputs | `backend/agents/` |
| **Services** | External I/O and normalisation | `backend/services/` |
| **Schemas** | Pydantic contracts for report pillars | `backend/schema/` |

**Why this split**

- Entity resolution is a distinct product problem from report synthesis — separate agents and UX.  
- Pillars run **sequentially** so later agents can use earlier structured context (e.g. competition sees business-model JSON).  
- The API stays thin; grounding rules live next to the graph, not scattered in the UI.

---

## 3. End-to-end user flows

### 3.1 Entity identification (Page 1)

1. User enters a **name** or **Companies House number**.  
2. If the input is a valid registration number, the API resolves it via Companies House profile (no LLM).  
3. Otherwise `POST /api/search/agentic` runs the **company-search** ReAct agent with tools:  
   - `search_companies` — name / free-text search  
   - `filter_companies` — advanced filters (location, status, type, SIC, dates)  
   - `get_company` — exact number lookup  
4. Structured decision:  
   - `found` — single company  
   - `needs_clarification` — short question + candidate list (clickable in UI; follow-up or direct select)  
   - `not_found` — user-facing message (soft failure, not a raw 502 where avoidable)  
5. Search attempts on name/filter tools are capped (max 5) so the agent retries with varied queries before giving up.

### 3.2 Intelligence report (Page 2)

1. User confirms a company → `POST /api/intelligence/{company_number}/runs`.  
2. Backend starts an async LangGraph run; frontend opens SSE  
   `GET /api/intelligence/runs/{run_id}/stream`.  
3. Events stream `stage` + partial `report` as each pillar completes.  
4. Dashboard renders **Profile → Business model → Competition → Reputation & quality** as data arrives.

---

## 4. Agent orchestration

### 4.1 Company-search agent

| Item | Choice |
|------|--------|
| Framework | LangGraph `create_react_agent` |
| Output | Structured `AgentDecision` (`found` / `needs_clarification` / `not_found`) |
| Tools | Companies House only (no web in this stage) |
| Budget | Max 5 search/filter tries per request; soft errors returned as JSON to the model |

**Design decision:** Keep identification on statutory registry data so the “right legal entity” is never invented from a web page.

### 4.2 Intelligence graph (sequential)

```
START → load_profile → business_model → competition → quality → END
```

| Node | Agent / logic | Tools | Structured output |
|------|----------------|-------|-------------------|
| `load_profile` | Deterministic service call | Companies House profile | `CompanyIdentity` |
| `business_model` | ReAct agent | `get_company_profile` only | `BusinessModelSection` |
| `competition` | ReAct agent + pipeline overwrite | profile, `search_peers`, `web_search` | `CompetitionSection` |
| `quality` | ReAct agent + pipeline overwrite | `web_search` (+ profile for context) | `QualitySection` |

**Design decisions**

- **Sequential, not fan-out:** Matches the brief’s three outputs and keeps provenance clearer for underwriting review.  
- **Pipeline overwrites** after each agent for peers, rivalry score, confidence, and citations — the LLM proposes; deterministic code confirms.  
- **SSE:** Assessors and users see evidence land pillar-by-pillar rather than waiting for a single bulk response.

---

## 5. LLM usage

| Workload | Default model | Env var | Reasoning effort |
|----------|---------------|---------|------------------|
| Agentic company search | `gpt-5.6-luna` | `OPENAI_MODEL` | `none` |
| Intelligence pillars (BM, competition, quality) | `gpt-5.6-terra` | `OPENAI_INTELLIGENCE_MODEL` | `none` |

**Why two models**

- **Luna** — cheaper / high-volume tool loops for name disambiguation.  
- **Terra** — stronger synthesis for underwriting-facing sections.

**Why `reasoning_effort=none`**

- Agents use **Chat Completions + function tools** (LangGraph ReAct).  
- For `gpt-5.6-luna` / `gpt-5.6-terra`, function tools on `/v1/chat/completions` require `reasoning_effort` set to `none`. Higher effort would need the Responses API, which this stack does not use yet.

**Structured outputs**

- Each intelligence agent uses Pydantic `response_format` matching the report schemas so the UI and validators share one contract.

---

## 6. Data sources and gathering

| Source | Used for | Access |
|--------|----------|--------|
| **Companies House** Public Data API | Profile, search, advanced search, peer discovery | API key (`COMPANIES_HOUSE_*`) |
| **Tavily** web search | Competition / quality evidence snippets + URLs | API key (`TAVILY_*`) |
| **OpenAI** | Tool-using agents + structured section fill | API key (`OPENAI_*`) |

**Business model** deliberately uses **Companies House only** so commercial tags are not invented from unverified websites. Competition and quality use web search with identity-oriented queries (company name, and name + locality/address for corroboration).

**Peers:** Active companies sharing SIC (± geography) via advanced search; the graph re-fetches the **full peer set** after the competition agent so the UI list is not truncated by the model.

---

## 7. Grounding techniques

Grounding is layered: schema → tools → post-agent filters → UI provenance.

### 7.1 Schema-level grounding

Report pillars are typed (`backend/schema/`). Agents must fill fields such as SIC lists, peer companies, citations, and confidence — not free-form essays alone.

### 7.2 Tool-level grounding

- Company numbers in peers / decisions must come from tool returns (prompt + pipeline peer overwrite).  
- Web citations must originate from Tavily results for that run.  
- Business-model agent is forbidden from inventing web sources.

### 7.3 Citation allowlisting (post-agent)

Implemented in `backend/agents/intelligence/citations.py`, applied in every intelligence pillar node:

1. **URL allowlist** — `citation.url` must match a URL from that run’s `web_search` tool payloads (normalised host/path).  
2. **CH `source_ref` allowlist** — only known paths such as `companies_house:profile.sic_codes`, `companies_house:search_peers`, etc.  
3. **Field presence** — e.g. SIC citation only if the profile has SIC codes; peer citations only after peers loaded.  

Invalid citations are **stripped**; the section still completes. A gap note records how many were removed.

**What this does *not* claim:** that every sentence is entailed by a citation. It proves **provenance of sources**, not NL entailment.

### 7.4 Deterministic field overwrites

| Field | Source of truth |
|-------|-----------------|
| `competition.peer_set` / `peer_count_estimate` / arena | Fresh `search_peers` call in the graph |
| `competition.rivalry_score` | Peer-count banding (1–5) |
| Pillar `confidence` | Rules in `confidence.py` (see §8) |
| `confidence_factors` | Boolean ticks stored for UI tooltips |

---

## 8. Uncertainty handling

### 8.1 Entity resolution uncertainty

- Ambiguous names → `needs_clarification` with candidates, not a forced guess.  
- Soft failure messages when agents/tools fail instead of opaque HTTP errors where possible.  
- Search try budget forces multiple query strategies before `not_found`.

### 8.2 Report-level confidence (deterministic)

Agent-emitted confidence is **overwritten** by code.

| Pillar | Medium / High rule | Low |
|--------|--------------------|-----|
| **Business model** | SIC codes present → **medium** | No SIC → **low** |
| **Competition** | Peers + web mentions company name + profile/address corroboration → **high**; peers only → **medium** | No peer set → **low** |
| **Quality** | **Mandatory sites:** an **attributable** `trustpilot.com/review/...` page (legal name **and** address/locality/number on the **same** hit) **and** a recognised trade/news domain URL naming the company, **plus** profile/address corroboration → **medium**. Profile/address ticks **only if both** Trustpilot and trade press already passed; if either fails, profile is treated as not found (✗) | Either mandatory site missing, or no profile corroboration → **low**. Unrelated Trustpilot businesses / parent-brand / product-platform pages → **hard fail** Trustpilot (no tick, no invented rating) |

**Overall report confidence** = weakest completed pillar.

Quality site ticks require the **result URL host** (not query text in titles/snippets). Trustpilot additionally requires a `/review/` path and same-hit CH identity corroboration so brand collisions (e.g. GOOGLE ADS LTD vs Google Ads) do not count. Company-name and address checks still use substring matching over tool snippets. The reputation agent must search Trustpilot and trade press; the pipeline strips invented Trustpilot platforms / empty “Trade press · neutral” when URL evidence is absent.

### 8.3 Explainability in the UI

Confidence labels expose a checklist tooltip:

- Criteria with ✓ / unmet  
- Short reasoning line under the criteria  

Competition and quality also persist `confidence_factors` on the section payload so the UI mirrors the same ticks the pipeline used.

### 8.4 Gaps

Pipeline appends human-readable `gaps` (missing SIC, dropped citations, thin quality evidence, etc.). These travel with the report payload for assessors and future UI surfacing.

### 8.5 Still model-judged (acknowledged)

- Free-text summaries and thematic bullets  
- Business-model revenue/segment/product tags (cautious inference from SIC + name)  
- Quality composite `quality_score` (1–5) — not overwritten by the pipeline today  

These sit beside deterministic confidence so uncertainty is visible even when narrative is generative.

---

## 9. Final report mapping to the brief

| Brief deliverable | Citehouse artefact |
|-------------------|--------------------|
| Business-model summary | `BusinessModelSection`: summary, revenue tags, segments, products/services, citations, confidence |
| Competition (sector / geography) | `CompetitionSection`: arena (SIC × geography), peer set, peer count, rivalry score, evidence, citations, confidence |
| Quality (customer / trade press) | `QualitySection`: customer rating (when found), theme sentiment, trade press, rationale, citations, confidence |
| Explainable / citation-backed | Citations list + allowlist filter + confidence criteria tooltips |
| Orchestration + grounding + uncertainty | Search agent + intelligence graph + §7–§8 |

**Profile (identity)** is shown first as statutory context (number, status, type, address, SIC) before the three synthesis pillars.

---

## 10. API surface (summary)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Liveness |
| `GET` | `/api/search/by-company-number/{number}` | Direct CH resolve |
| `POST` | `/api/search/agentic` | Agentic name / follow-up search |
| `POST` | `/api/intelligence/{number}/runs` | Start report run |
| `GET` | `/api/intelligence/runs/{id}/stream` | SSE progress + partial report |
| `GET` | `/api/intelligence/runs/{id}` | Snapshot |

Run state is held in-process and mirrored under `backend/.runs/` for local durability across reloads — suitable for demo, not multi-instance production.

---

## 11. Frontend architecture

| Surface | Responsibility |
|---------|----------------|
| `/` | Brand + lookup form; clarification message; right panel for suggestions or matched company |
| `/report/[companyNumber]` | Start run, consume SSE, render progressive intelligence dashboard |

Shared formatting: company-type labels, confidence tooltip helpers (`frontend/lib/confidence.ts`) aligned with backend rules.

---

## 12. Key design trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| CH-only business model | Avoids fabricated websites | Weaker product/market detail without web |
| Sequential pillars | Clear provenance, simpler failure isolation | Higher latency than parallel fan-out |
| Citation allowlist | Blocks invented URLs / fake CH refs | Does not prove textual entailment |
| Deterministic confidence | Auditable uncertainty for assessors | Heuristic substring / marker false positives |
| Chat Completions + tools | Simple LangGraph ReAct stack | Cannot use Terra/Luna elevated reasoning with tools |
| In-memory + file runs | Fast local demo | No HA / shared store |

---

## 13. Local configuration

See `backend/.env.example`:

- `COMPANIES_HOUSE_API_KEY` / `COMPANIES_HOUSE_BASE_URL`  
- `OPENAI_API_KEY`, `OPENAI_MODEL` (search), `OPENAI_INTELLIGENCE_MODEL` (report)  
- `TAVILY_API_KEY` / `TAVILY_BASE_URL`  

Frontend: `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).

Setup steps: root `README.md`.

---

## 14. Future extensions (out of current demo)

- Deployed environment + written runbook for external assessors  
- Surface `gaps`, overall confidence, and rivalry/quality numeric scores in the report UI  
- Claim↔citation linking or a lightweight entailment pass  
- Responses API for higher reasoning effort with tools  
- Business-model enrichment via verified official website (after identity confirmation)  
- Persistent run store and authentication  

---

## 15. Repository map

```
citehouse/
├── ARCHITECTURE.md          # This document
├── README.md                # Local setup
├── frontend/                # Next.js UI
│   ├── app/                 # Routes
│   ├── components/          # Lookup + intelligence sections
│   └── lib/                 # API client, confidence tooltip helpers
└── backend/
    ├── main.py
    ├── routers/             # HTTP API
    ├── agents/
    │   ├── company_search/  # Entity resolution agent
    │   └── intelligence/    # Graph, pillar agents, citations, confidence
    ├── services/            # CH, peers, web, runs
    ├── schema/              # Report contracts
    └── utils/               # HTTP clients
```

---

*Document version: aligned with the Citehouse codebase as of the intelligence pipeline with citation allowlisting and deterministic confidence.*
