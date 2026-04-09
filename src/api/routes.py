from __future__ import annotations

import functools
from typing import List

import pandas as pd
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.api.models import RecommendRequest, RecommendResponse
from src.api.orchestrator import run_recommendation
from src.phase3.config import Phase3Config

router = APIRouter()


# Merge near-duplicate cuisine names to a single canonical label.
_CUISINE_CANONICAL: dict[str, str] = {
    "Afghan": "Afghani",
}

@functools.lru_cache(maxsize=1)
def _load_meta() -> tuple[List[str], List[str]]:
    """Load and cache locations and cuisines from the curated dataset."""
    cfg = Phase3Config()
    df = pd.read_csv(str(cfg.curated_csv_path))

    # Locations: all dataset localities sorted (no "Bangalore" catch-all)
    locations = sorted(df["city"].dropna().unique().tolist())

    # Cuisines: split, canonicalise duplicates, deduplicate, sort
    all_cuisines: set[str] = set()
    for row in df["cuisines"].dropna():
        for c in str(row).split(","):
            c = c.strip()
            if c:
                all_cuisines.add(_CUISINE_CANONICAL.get(c, c))
    cuisines = sorted(all_cuisines)

    return locations, cuisines


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    return run_recommendation(request)


@router.get("/locations", response_model=List[str])
def get_locations() -> List[str]:
    locations, _ = _load_meta()
    return locations


@router.get("/cuisines", response_model=List[str])
def get_cuisines() -> List[str]:
    _, cuisines = _load_meta()
    return cuisines


@router.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
