from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.phase2.models import UserPreference
from src.phase3.models import Candidate
from src.phase4.config import Phase4Config
from src.phase4.llm_client import LLMClient, LLMError
from src.phase4.output_validator import OutputValidationError, validate_llm_output
from src.phase4.prompt_builder import build_prompt


@dataclass
class Phase4Result:
    recommendations: List[Dict[str, Any]]
    fallback_used: bool
    error: Optional[str]


def rank_with_llm(
    preference: UserPreference,
    candidates: List[Candidate],
    cfg: Phase4Config | None = None,
) -> Phase4Result:
    """
    Calls Gemini LLM to rank candidates and produce explanations.
    Falls back to baseline ranking if LLM fails or output is invalid.
    """
    cfg = cfg or Phase4Config()

    if not candidates:
        return Phase4Result(recommendations=[], fallback_used=False, error=None)

    # --- Try LLM path ---
    try:
        client = LLMClient(cfg)
        # Send only the top-N candidates to the LLM to keep prompt small and fast
        llm_candidates = candidates[: cfg.llm_candidate_limit]
        prompt = build_prompt(preference, llm_candidates, top_k=cfg.top_k_final)
        raw_output = client.generate_json(prompt)
        recommendations = validate_llm_output(raw_output, llm_candidates, top_k=cfg.top_k_final)
        return Phase4Result(
            recommendations=recommendations, fallback_used=False, error=None
        )
    except (LLMError, OutputValidationError, Exception) as exc:
        error_msg = str(exc)

    # --- Fallback: deterministic baseline ranking ---
    fallback = _baseline_fallback(candidates, cfg.top_k_final)
    return Phase4Result(
        recommendations=fallback, fallback_used=True, error=error_msg
    )


def _baseline_fallback(candidates: List[Candidate], top_k: int) -> List[Dict[str, Any]]:
    sorted_candidates = sorted(candidates, key=lambda c: c.baseline_score, reverse=True)
    results = []
    for i, c in enumerate(sorted_candidates[:top_k]):
        results.append(
            {
                "restaurant_id": c.restaurant_id,
                "rank": i + 1,
                "name": c.name,
                "city": c.city,
                "cuisines": c.cuisines,
                "rating": c.rating,
                "avg_cost_for_two": c.avg_cost_for_two,
                "votes": c.votes,
                "fit_reason": (
                    f"Ranked by score: rating {c.rating}/5, "
                    f"cuisine match {c.match_features.cuisine_match:.0%}, "
                    f"cost ₹{c.avg_cost_for_two:.0f} for two."
                ),
                "tradeoffs": None,
                "confidence": "medium",
            }
        )
    return results
