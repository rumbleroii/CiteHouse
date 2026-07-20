# Citehouse

Next.js + shadcn/ui frontend, FastAPI backend.

**System design:** see [Citehouse-Architecture.pdf](./Citehouse-Architecture.pdf) for overall architecture, LLM usage, grounding, and uncertainty handling.

## Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at http://localhost:3000

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs at http://localhost:8000  
Docs at http://localhost:8000/docs

Copy `backend/.env.example` → `backend/.env` and fill API keys.

### Frontend → API

Set `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).  
For a remote frontend, also set backend `CORS_ORIGINS` to that origin.

### Optional agent traces

With a [LangSmith](https://smith.langchain.com) key in `backend/.env`:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=citehouse
```

## Structure

```
citehouse/
├── frontend/   # Next.js + shadcn
└── backend/    # FastAPI
```
