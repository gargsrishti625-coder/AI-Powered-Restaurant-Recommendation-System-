from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phase2.normalizer import PreferenceValidationError, normalize_user_preference
from src.phase2.models import RawPreferenceInput


def main() -> None:
    # Example raw input; in a real app this would come from UI / API.
    raw = RawPreferenceInput(
        location="bangalore",
        budget="medium",
        cuisine="north indian, chinese",
        min_rating=4.0,
        additional_preferences="family-friendly place with quick service and good value",
    )
    try:
        pref = normalize_user_preference(raw)
    except PreferenceValidationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        raise SystemExit(1)

    result = {
        "ok": True,
        "city": pref.city,
        "budget_range": {
            "min_cost": pref.budget_range.min_cost,
            "max_cost": pref.budget_range.max_cost,
        },
        "cuisine_preferences": pref.cuisine_preferences,
        "min_rating": pref.min_rating,
        "keywords": pref.keywords,
        "sort_bias": pref.sort_bias,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

