from __future__ import annotations

from typing import Any, Dict, List, Set

from src.phase3.models import Candidate


class OutputValidationError(ValueError):
    pass


def validate_llm_output(
    raw: Dict[str, Any],
    candidates: List[Candidate],
    top_k: int,
) -> List[Dict[str, Any]]:
    """Validate LLM JSON output and return the cleaned recommendations list."""
    if not isinstance(raw, dict):
        raise OutputValidationError("LLM output is not a JSON object.")

    if "recommendations" not in raw:
        raise OutputValidationError("Missing 'recommendations' key in LLM output.")

    recs = raw["recommendations"]
    if not isinstance(recs, list) or len(recs) == 0:
        raise OutputValidationError("'recommendations' must be a non-empty list.")

    valid_ids: Set[str] = {c.restaurant_id for c in candidates}
    candidate_map: Dict[str, Candidate] = {c.restaurant_id: c for c in candidates}

    cleaned: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()

    for item in recs:
        if not isinstance(item, dict):
            continue

        rid = str(item.get("restaurant_id", ""))
        if not rid or rid not in valid_ids:
            # Reject hallucinated restaurant IDs
            continue
        if rid in seen_ids:
            continue
        seen_ids.add(rid)

        rank = item.get("rank")
        if not isinstance(rank, int) or rank < 1:
            rank = len(cleaned) + 1

        confidence = item.get("confidence", "medium")
        if confidence not in {"low", "medium", "high"}:
            confidence = "medium"

        fit_reason = str(item.get("fit_reason", "")).strip()
        tradeoffs = item.get("tradeoffs")
        if tradeoffs is not None:
            tradeoffs = str(tradeoffs).strip() or None

        c = candidate_map[rid]
        cleaned.append(
            {
                "restaurant_id": rid,
                "rank": rank,
                "name": c.name,
                "city": c.city,
                "cuisines": c.cuisines,
                "rating": c.rating,
                "avg_cost_for_two": c.avg_cost_for_two,
                "votes": c.votes,
                "fit_reason": fit_reason,
                "tradeoffs": tradeoffs,
                "confidence": confidence,
            }
        )

        if len(cleaned) >= top_k:
            break

    if not cleaned:
        raise OutputValidationError(
            "No valid grounded recommendations found in LLM output."
        )

    # Re-assign ranks in order
    for i, rec in enumerate(cleaned):
        rec["rank"] = i + 1

    return cleaned
