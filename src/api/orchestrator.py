from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Tuple

from src.api.models import RecommendRequest, RecommendResponse, RecommendationItem
from src.phase2.models import RawPreferenceInput
from src.phase2.normalizer import PreferenceValidationError, normalize_user_preference
from src.phase3.retrieval import retrieve_candidates
from src.phase4.orchestrator import rank_with_llm


def run_recommendation(request: RecommendRequest) -> RecommendResponse:
    request_id = str(uuid.uuid4())
    start_ms = time.monotonic() * 1000

    # ── Phase 2: Normalize user preferences ────────────────────────────────────
    try:
        raw = RawPreferenceInput(
            location=request.location,
            budget=request.budget,
            cuisine=request.cuisine,
            min_rating=request.min_rating,
            additional_preferences=request.additional_preferences,
        )
        preference = normalize_user_preference(raw)
    except PreferenceValidationError as exc:
        return RecommendResponse(
            request_id=request_id,
            status="error",
            city=request.location,
            total_candidates_found=0,
            recommendations=[],
            fallback_used=False,
            error_detail=str(exc),
            latency_ms=_elapsed_ms(start_ms),
        )

    # ── Phase 3: Retrieve candidates ────────────────────────────────────────────
    retrieval_result = retrieve_candidates(preference)

    if retrieval_result.total_after_hard_filters == 0:
        return RecommendResponse(
            request_id=request_id,
            status="no_results",
            city=preference.city,
            total_candidates_found=0,
            recommendations=[],
            fallback_used=False,
            error_detail="No restaurants match the given filters. Try relaxing budget or rating.",
            latency_ms=_elapsed_ms(start_ms),
        )

    # ── Phase 4: LLM ranking and explanations ──────────────────────────────────
    phase4_result = rank_with_llm(preference, retrieval_result.candidates)

    # ── Format response ─────────────────────────────────────────────────────────
    items = _format_recommendations(phase4_result.recommendations, retrieval_result.candidates)

    return RecommendResponse(
        request_id=request_id,
        status="success",
        city=preference.city,
        total_candidates_found=retrieval_result.total_after_hard_filters,
        recommendations=items,
        fallback_used=phase4_result.fallback_used,
        error_detail=phase4_result.error,
        latency_ms=_elapsed_ms(start_ms),
    )


def _elapsed_ms(start_ms: float) -> float:
    return round(time.monotonic() * 1000 - start_ms, 1)


def _format_recommendations(
    recs: List[Dict[str, Any]],
    candidates: List[Any],
) -> List[RecommendationItem]:
    candidate_map = {c.restaurant_id: c for c in candidates}
    items: List[RecommendationItem] = []

    for rec in recs:
        rid = rec["restaurant_id"]
        candidate = candidate_map.get(rid)
        match_signals: Dict[str, Any] = {}
        if candidate:
            match_signals = {
                "budget_fit": round(candidate.match_features.budget_fit, 3),
                "cuisine_match": round(candidate.match_features.cuisine_match, 3),
                "rating_pass": candidate.match_features.rating_pass,
                "baseline_score": round(candidate.baseline_score, 4),
            }

        items.append(
            RecommendationItem(
                rank=rec["rank"],
                restaurant_id=rid,
                restaurant_name=rec.get("name", ""),
                cuisine=rec.get("cuisines", ""),
                rating=rec.get("rating", 0.0),
                estimated_cost=rec.get("avg_cost_for_two", 0.0),
                votes=rec.get("votes", 0),
                ai_explanation=rec.get("fit_reason", ""),
                tradeoffs=rec.get("tradeoffs"),
                confidence=rec.get("confidence", "medium"),
                match_signals=match_signals,
            )
        )

    return items
