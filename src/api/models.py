from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ── Request ────────────────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    location: str = Field(..., description="City or locality (e.g. 'Bangalore', 'Banashankari')")
    budget: str = Field("medium", description="low | medium | high (or aliases like cheap/premium)")
    cuisine: Optional[str] = Field(None, description="Comma-separated cuisines (e.g. 'Italian, Chinese')")
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Minimum restaurant rating (0-5)")
    additional_preferences: Optional[str] = Field(
        None, description="Free-text preferences (e.g. 'family-friendly, quick service')"
    )

    @field_validator("location")
    @classmethod
    def location_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("location must not be empty.")
        return v


# ── Response ───────────────────────────────────────────────────────────────────

class RecommendationItem(BaseModel):
    rank: int
    restaurant_id: str
    restaurant_name: str
    cuisine: str
    rating: float
    estimated_cost: float
    votes: int
    ai_explanation: str
    tradeoffs: Optional[str]
    confidence: str
    match_signals: Dict[str, Any]


class RecommendResponse(BaseModel):
    request_id: str
    status: str
    city: str
    total_candidates_found: int
    recommendations: List[RecommendationItem]
    fallback_used: bool
    error_detail: Optional[str]
    latency_ms: float
