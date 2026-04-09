from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phase2.models import RawPreferenceInput
from src.phase2.normalizer import normalize_user_preference
from src.phase3.retrieval import retrieve_candidates


def main() -> None:
    raw = RawPreferenceInput(
        location="Banashankari",
        budget="medium",
        cuisine="italian, chinese",
        min_rating=4.0,
        additional_preferences="family-friendly and quick service",
    )
    preference = normalize_user_preference(raw)
    result = retrieve_candidates(preference)

    payload = {
        "total_after_hard_filters": result.total_after_hard_filters,
        "returned_candidates": len(result.candidates),
        "top_candidates": [
            {
                "restaurant_id": c.restaurant_id,
                "name": c.name,
                "city": c.city,
                "cuisines": c.cuisines,
                "rating": c.rating,
                "avg_cost_for_two": c.avg_cost_for_two,
                "votes": c.votes,
                "match_features": {
                    "budget_fit": c.match_features.budget_fit,
                    "cuisine_match": c.match_features.cuisine_match,
                    "rating_pass": c.match_features.rating_pass,
                },
                "baseline_score": round(c.baseline_score, 4),
            }
            for c in result.candidates[:5]
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

