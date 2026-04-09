from __future__ import annotations

import json
from typing import List

from src.phase2.models import UserPreference
from src.phase3.models import Candidate


SYSTEM_PROMPT = (
    "You are a restaurant recommendation assistant. "
    "Rank the given candidates for the user. Rules: "
    "1) Only use restaurants from the list—no hallucinations. "
    "2) fit_reason: 1-2 concise sentences using only the given data. "
    "3) tradeoffs: one short sentence or null. "
    "4) confidence: low|medium|high. "
    "5) Return ONLY valid JSON, no markdown."
)


def _format_user_profile(preference: UserPreference) -> dict:
    budget = preference.budget_range
    return {
        "city": preference.city,
        "budget_range": {
            "min_cost": budget.min_cost,
            "max_cost": budget.max_cost if budget.max_cost is not None else "unlimited",
        },
        "cuisine_preferences": preference.cuisine_preferences,
        "min_rating": preference.min_rating,
        "keywords": preference.keywords,
        "sort_bias": preference.sort_bias,
    }


def _format_candidates(candidates: List[Candidate]) -> List[dict]:
    return [
        {
            "restaurant_id": c.restaurant_id,
            "name": c.name,
            "city": c.city,
            "cuisines": c.cuisines,
            "rating": c.rating,
            "avg_cost_for_two": c.avg_cost_for_two,
            "votes": c.votes,
            "baseline_score": round(c.baseline_score, 4),
        }
        for c in candidates
    ]


OUTPUT_SCHEMA = {
    "recommendations": [
        {
            "restaurant_id": "<string>",
            "rank": "<integer starting at 1>",
            "fit_reason": "<2-3 sentences explaining why this restaurant fits the user>",
            "tradeoffs": "<one sentence about any limitations, or null if none>",
            "confidence": "<low | medium | high>",
        }
    ]
}


def build_prompt(preference: UserPreference, candidates: List[Candidate], top_k: int = 5) -> str:
    user_profile = _format_user_profile(preference)
    candidate_list = _format_candidates(candidates)
    k = min(top_k, len(candidates))

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"USER:{json.dumps(user_profile, separators=(',', ':'))}\n\n"
        f"CANDIDATES:{json.dumps(candidate_list, separators=(',', ':'))}\n\n"
        f"Return the top {k} recommendations as JSON:\n"
        f"{json.dumps(OUTPUT_SCHEMA, separators=(',', ':'))}"
    )
