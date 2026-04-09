from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `src.*` imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env before any src imports
def _load_env() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

_load_env()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from src.api.routes import router  # noqa: E402

UI_DIR = PROJECT_ROOT / "src" / "ui"

app = FastAPI(
    title="AI Restaurant Recommender",
    description="Phase 5: Recommendation Service API — backed by Gemini LLM + Zomato dataset",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve UI static files at /static/*
app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")

@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    return FileResponse(str(UI_DIR / "index.html"))
