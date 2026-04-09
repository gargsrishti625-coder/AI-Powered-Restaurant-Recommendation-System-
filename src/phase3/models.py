from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class MatchFeatures:
    budget_fit: float
    cuisine_match: float
    rating_pass: bool


@dataclass
class Candidate:
    restaurant_id: str
    name: str
    city: str
    cuisines: str
    rating: float
    avg_cost_for_two: float
    votes: int
    match_features: MatchFeatures
    baseline_score: float


@dataclass
class RetrievalResult:
    total_after_hard_filters: int
    candidates: List[Candidate]

