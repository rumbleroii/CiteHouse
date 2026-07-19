# Citehouse

Next.js + shadcn/ui frontend, FastAPI backend.

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

## Structure

```
citehouse/
├── frontend/   # Next.js + shadcn
└── backend/    # FastAPI
```
