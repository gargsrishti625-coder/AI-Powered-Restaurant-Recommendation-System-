"""
Phase 5 integration test — exercises the full pipeline:
  Phase 2 (normalization) → Phase 3 (retrieval) → Phase 4 (LLM ranking) → API orchestrator

Runs 3 representative test cases and prints structured results.
No server needs to be running; calls the orchestrator directly.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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

from src.api.models import RecommendRequest  # noqa: E402
from src.api.orchestrator import run_recommendation  # noqa: E402

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
WARN = "\033[33mWARN\033[0m"


TEST_CASES = [
    {
        "name": "Case 1 – Bangalore, medium budget, Italian/Chinese, family-friendly",
        "input": RecommendRequest(
            location="Bangalore",
            budget="medium",
            cuisine="Italian, Chinese",
            min_rating=4.0,
            additional_preferences="family-friendly quick service",
        ),
    },
    {
        "name": "Case 2 – Delhi, low budget, North Indian, no extra preferences",
        "input": RecommendRequest(
            location="Delhi",
            budget="low",
            cuisine="North Indian",
            min_rating=3.5,
            additional_preferences=None,
        ),
    },
    {
        "name": "Case 3 – Mumbai, high budget, any cuisine, quality dining",
        "input": RecommendRequest(
            location="Mumbai",
            budget="high",
            cuisine=None,
            min_rating=4.2,
            additional_preferences="quality fine dining",
        ),
    },
]


def run_test(case: dict) -> bool:
    name = case["name"]
    req: RecommendRequest = case["input"]
    print(f"\n{'=' * 70}")
    print(f"  {name}")
    print(f"{'=' * 70}")
    print(f"  Input: location={req.location!r}, budget={req.budget!r}, "
          f"cuisine={req.cuisine!r}, min_rating={req.min_rating}, "
          f"additional={req.additional_preferences!r}")

    try:
        response = run_recommendation(req)
    except Exception as exc:
        print(f"[{FAIL}] Unexpected exception: {exc}")
        return False

    # Basic assertions
    ok = True
    if response.status not in {"success", "no_results", "error"}:
        print(f"[{FAIL}] Unexpected status: {response.status}")
        ok = False

    if response.status == "success" and len(response.recommendations) == 0:
        print(f"[{WARN}] status=success but 0 recommendations returned")
        ok = False

    if response.fallback_used:
        print(f"[{WARN}] LLM fallback was used — error: {response.error_detail}")

    print(f"  Status         : {response.status}")
    print(f"  City           : {response.city}")
    print(f"  Candidates found: {response.total_candidates_found}")
    print(f"  Recommendations : {len(response.recommendations)}")
    print(f"  Fallback used  : {response.fallback_used}")
    print(f"  Latency        : {response.latency_ms:.1f} ms")

    for rec in response.recommendations:
        print(f"\n  #{rec.rank}  {rec.restaurant_name}")
        print(f"       Cuisine : {rec.cuisine}")
        print(f"       Rating  : {rec.rating}  |  Cost: ₹{rec.estimated_cost:.0f}  |  Votes: {rec.votes}")
        print(f"       Confidence: {rec.confidence}")
        print(f"       Explanation: {rec.ai_explanation}")
        if rec.tradeoffs:
            print(f"       Tradeoffs: {rec.tradeoffs}")
        print(f"       Match signals: {json.dumps(rec.match_signals)}")

    if ok:
        print(f"\n[{PASS}] {name}")
    else:
        print(f"\n[{FAIL}] {name}")
    return ok


def main() -> None:
    print("\nPhase 5 Integration Tests — AI Restaurant Recommender")
    print(f"Model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}\n")

    results = [run_test(case) for case in TEST_CASES]
    passed = sum(results)
    total = len(results)

    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} tests passed.")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
