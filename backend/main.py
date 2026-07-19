from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import agentic_search, health, search_company

load_dotenv()

app = FastAPI(title="Citehouse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(search_company.router, prefix="/api")
app.include_router(agentic_search.router, prefix="/api")
