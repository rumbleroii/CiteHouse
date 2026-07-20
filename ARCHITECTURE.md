# Citehouse — Architecture

Citehouse turns a UK company name or Companies House number into an explainable, citation-backed intelligence report for underwriting-style review.

**Report pillars**

1. Business-model summary  
2. Competitive intensity (sector / geography)  
3. Company quality (customer / trade press)

---

## High-level system

```mermaid
flowchart LR
  UI[Next.js frontend] -->|HTTP + SSE| API[FastAPI]
  API --> Search[Company search agent]
  API --> Graph[Intelligence graph]
  Search --> CH[Companies House API]
  Graph --> CH
  Graph --> Tavily[Tavily Search]
  Search --> OpenAI[OpenAI]
  Graph --> OpenAI
```

| Layer | Role | Location |
|--------|------|----------|
| Frontend | Lookup UX + progressive report | `frontend/` |
| API | Thin HTTP for search + runs | `backend/routers/` |
| Agents | ReAct tools + structured outputs | `backend/agents/` |
| Services | External I/O | `backend/services/` |
| Schemas | Pydantic report contracts | `backend/schema/` |

**Why this split:** entity resolution and report synthesis are separate product problems. The API stays thin; grounding lives next to the graph.

---

## User flows

### 1. Find the company

```mermaid
flowchart TD
  A[User enters name or number] --> B{Valid CH number?}
  B -->|Yes| C[Resolve via Companies House profile]
  B -->|No| D[Company-search ReAct agent]
  D --> E{Decision}
  E -->|found| F[Single company]
  E -->|needs_clarification| G[Ask + show candidates]
  E -->|not_found| H[Soft failure message]
  G --> I[User clarifies or clicks a candidate]
  I --> D
  C --> J[Go to report]
  F --> J
```

Tools (Companies House only): `search_companies`, `filter_companies`, `get_company`. Max 5 search attempts so the agent can retry before giving up.

### 2. Build the report

```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend
  participant API as FastAPI
  participant G as LangGraph

  U->>FE: Confirm company
  FE->>API: POST /intelligence/{number}/runs
  API->>G: Start async run
  FE->>API: GET .../stream (SSE)
  loop Each pillar
    G-->>API: stage + partial report
    API-->>FE: SSE event
    FE-->>U: Update dashboard
  end
```

Dashboard order: **Profile → Business model → Competition → Quality**.

---

## Agent orchestration

### Company-search agent

```mermaid
flowchart LR
  In[Name / follow-up] --> Agent[ReAct agent]
  Agent --> Tools[CH tools only]
  Tools --> Agent
  Agent --> Out[AgentDecision]
```

| | |
|--|--|
| Framework | LangGraph `create_react_agent` |
| Output | `found` / `needs_clarification` / `not_found` |
| Sources | Companies House only — never invent an entity from the web |

### Intelligence graph

```mermaid
flowchart LR
  S([START]) --> P[load_profile]
  P --> BM[business_model]
  BM --> C[competition]
  C --> Q[quality]
  Q --> E([END])
```

| Node | Tools | Output |
|------|--------|--------|
| `load_profile` | CH profile (deterministic) | `CompanyIdentity` |
| `business_model` | `get_company_profile` | `BusinessModelSection` |
| `competition` | profile, peers, web search | `CompetitionSection` |
| `quality` | web search (+ profile context) | `QualitySection` |

**Design choices**

- Sequential so later pillars can use earlier structured context.
- After each agent, deterministic code overwrites peers, rivalry, confidence, and citations.
- SSE streams pillars as they finish.

---

## Data sources

```mermaid
flowchart TB
  subgraph Registry
    CH[Companies House]
  end
  subgraph Web
    TV[Tavily]
  end
  subgraph Models
    LLM[OpenAI]
  end

  CH --> Profile[Identity + SIC]
  CH --> Peers[Peer set]
  CH --> BM[Business model]
  TV --> Comp[Competition evidence]
  TV --> Qual[Quality evidence]
  LLM --> All[Tool loops + structured fill]
```

| Source | Used for |
|--------|----------|
| Companies House | Profile, search, peers |
| Tavily | Competition / quality snippets + URLs |
| OpenAI | Agents + structured sections |

Business model is **CH-only**. Competition and quality use web search with identity-oriented queries. Peers are re-fetched after the competition agent so the UI list is complete.

---

## Grounding

Evidence is constrained in layers — schema → tools → post-filters → UI.

```mermaid
flowchart TD
  A[Schema: typed pillars] --> B[Tools: CH + Tavily only]
  B --> C[Citation allowlist]
  C --> D[Deterministic overwrites]
  D --> E[UI: citations + confidence tooltips]
```

**Citation allowlist** (`citations.py`)

1. Web URLs must match that run’s Tavily results.  
2. CH refs must be known paths (e.g. `companies_house:profile.sic_codes`).  
3. Invalid citations are stripped; a gap note records removals.

This proves **source provenance**, not that every sentence is entailed by a citation.

**Deterministic overwrites**

| Field | Source of truth |
|-------|-----------------|
| Peer set / count / arena | Fresh `search_peers` |
| Rivalry score | Peer-count banding (1–5) |
| Pillar confidence | Rules in `confidence.py` |
| Confidence factors | Boolean ticks for UI tooltips |

---

## Uncertainty

```mermaid
flowchart TD
  subgraph Entity
    A1[Ambiguous name] --> A2[needs_clarification + candidates]
    A3[Tool / agent failure] --> A4[Soft JSON error, not opaque 502]
  end

  subgraph Report
    B1[Agent proposes confidence] --> B2[Code overwrites]
    B2 --> B3[Overall = weakest pillar]
    B2 --> B4[Gaps appended to payload]
  end
```

| Pillar | Higher confidence when… | Low when… |
|--------|-------------------------|-----------|
| Business model | SIC codes present → medium | No SIC |
| Competition | Peers + web name match + address corroboration → high; peers only → medium | No peers |
| Quality | Attributable Trustpilot review page **and** trade/news URL naming the company, plus profile corroboration → medium | Either site missing |

UI shows ✓ / unmet criteria in confidence tooltips. Still model-judged: free-text summaries, BM tags, and quality score (1–5).

---

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Liveness |
| `GET` | `/api/search/by-company-number/{number}` | Direct CH resolve |
| `POST` | `/api/search/agentic` | Agentic name search |
| `POST` | `/api/intelligence/{number}/runs` | Start report |
| `GET` | `/api/intelligence/runs/{id}/stream` | SSE progress |
| `GET` | `/api/intelligence/runs/{id}` | Snapshot |

Runs live in-memory and under `backend/.runs/` — fine for demo, not multi-instance production.

---

## Frontend

```mermaid
flowchart LR
  Home["/ — lookup + clarify"] -->|company confirmed| Report["/report/[number]"]
  Report -->|SSE| Dash[Progressive dashboard]
```

Shared confidence helpers in `frontend/lib/confidence.ts` stay aligned with backend rules.

---

## LLM usage

| Workload | Model | Env |
|----------|-------|-----|
| Company search | `gpt-5.6-luna` | `OPENAI_MODEL` |
| Intelligence pillars | `gpt-5.6-terra` | `OPENAI_INTELLIGENCE_MODEL` |

Both use `reasoning_effort=none` because LangGraph ReAct runs on Chat Completions + function tools. Luna for cheap tool loops; Terra for stronger synthesis.

---

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| CH-only business model | No fabricated websites | Less product/market detail |
| Sequential pillars | Clear provenance | Higher latency than parallel |
| Citation allowlist | Blocks invented sources | No NL entailment |
| Deterministic confidence | Auditable uncertainty | Heuristic false positives |
| In-memory + file runs | Fast local demo | No HA / shared store |

---

## Repo map

```
citehouse/
├── ARCHITECTURE.md
├── README.md
├── frontend/          # Next.js UI
└── backend/
    ├── routers/       # HTTP API
    ├── agents/
    │   ├── company_search/
    │   └── intelligence/   # graph, citations, confidence
    ├── services/      # CH, peers, web, runs
    └── schema/        # Report contracts
```

**Config:** see `backend/.env.example` and root `README.md`.
