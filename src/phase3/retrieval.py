from __future__ import annotations

from typing import List

import pandas as pd

from src.phase2.models import UserPreference
from src.phase3.config import Phase3Config
from src.phase3.models import Candidate, MatchFeatures, RetrievalResult


def load_curated_restaurants(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["avg_cost_for_two"] = pd.to_numeric(df["avg_cost_for_two"], errors="coerce")
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0)
    return df


def _budget_fit_score(cost: float, min_cost: float, max_cost: float | None) -> float:
    if pd.isna(cost):
        return 0.0
    if max_cost is None:
        return 1.0 if cost >= min_cost else max(0.0, cost / max(min_cost, 1.0))
    if min_cost <= cost <= max_cost:
        return 1.0
    # Soft decay outside range.
    if cost < min_cost:
        return max(0.0, 1.0 - (min_cost - cost) / max(min_cost, 1.0))
    return max(0.0, 1.0 - (cost - max_cost) / max(max_cost, 1.0))


def _cuisine_match_score(restaurant_cuisines: str, preferred: List[str]) -> float:
    if not preferred:
        return 1.0
    if not isinstance(restaurant_cuisines, str) or not restaurant_cuisines.strip():
        return 0.0
    restaurant_set = {c.strip().lower() for c in restaurant_cuisines.split(",") if c.strip()}
    pref_set = {c.strip().lower() for c in preferred if c.strip()}
    if not pref_set:
        return 1.0
    overlap = len(restaurant_set.intersection(pref_set))
    return overlap / len(pref_set)


def retrieve_candidates(preference: UserPreference, cfg: Phase3Config | None = None) -> RetrievalResult:
    cfg = cfg or Phase3Config()
    df = load_curated_restaurants(str(cfg.curated_csv_path))

    # 1) Filter by city/location
    city_key = preference.city.lower()
    if city_key in cfg.city_groups:
        # Expand known city aliases (e.g. "bangalore") to their dataset localities.
        allowed = {loc.lower() for loc in cfg.city_groups[city_key]}
        city_filtered = df[df["city"].astype(str).str.lower().isin(allowed)].copy()
    else:
        city_filtered = df[df["city"].astype(str).str.lower() == city_key].copy()
        if city_filtered.empty:
            # Fallback to locality contains match for user-provided location.
            city_filtered = df[
                df["locality"].astype(str).str.lower().str.contains(city_key, na=False)
            ].copy()
        if city_filtered.empty:
            # Keep retrieval robust even when taxonomy doesn't match user city granularity.
            city_filtered = df.copy()

    # 2) Filter by budget range (soft window with tolerance to avoid over-pruning)
    min_cost = preference.budget_range.min_cost
    max_cost = preference.budget_range.max_cost
    if max_cost is None:
        budget_filtered = city_filtered[city_filtered["avg_cost_for_two"] >= min_cost].copy()
    else:
        tolerance = 0.20 * max_cost
        budget_filtered = city_filtered[
            (city_filtered["avg_cost_for_two"] >= max(0.0, min_cost - tolerance))
            & (city_filtered["avg_cost_for_two"] <= (max_cost + tolerance))
        ].copy()

    # 3) Filter by min rating
    hard_filtered = budget_filtered[budget_filtered["rating"] >= preference.min_rating].copy()
    total_after_hard_filters = len(hard_filtered)

    if hard_filtered.empty:
        return RetrievalResult(total_after_hard_filters=0, candidates=[])

    # 4) Soft match cuisines and preferences (keywords are available for future heuristics)
    hard_filtered["cuisine_match"] = hard_filtered["cuisines"].map(
        lambda c: _cuisine_match_score(c, preference.cuisine_preferences)
    )
    hard_filtered["budget_fit"] = hard_filtered["avg_cost_for_two"].map(
        lambda c: _budget_fit_score(c, min_cost, max_cost)
    )

    # 5) Score and rank top N
    rating_norm = (hard_filtered["rating"] / 5.0).clip(0, 1)
    votes_max = max(float(hard_filtered["votes"].max()), 1.0)
    popularity_norm = (hard_filtered["votes"] / votes_max).clip(0, 1)
    sparse_penalty = hard_filtered["cuisines"].isna().map(lambda x: 0.05 if x else 0.0)

    hard_filtered["baseline_score"] = (
        cfg.weight_rating * rating_norm
        + cfg.weight_cuisine * hard_filtered["cuisine_match"]
        + cfg.weight_budget * hard_filtered["budget_fit"]
        + cfg.weight_popularity * popularity_norm
        - sparse_penalty
    )

    ranked = hard_filtered.sort_values(by="baseline_score", ascending=False)
    ranked = ranked.drop_duplicates(subset=["name", "locality", "cuisines"], keep="first")
    ranked = ranked.head(cfg.top_n_candidates)

    candidates: List[Candidate] = []
    for _, row in ranked.iterrows():
        candidates.append(
            Candidate(
                restaurant_id=str(row["restaurant_id"]),
                name=str(row["name"]),
                city=str(row["city"]),
                cuisines=str(row["cuisines"]),
                rating=float(row["rating"]),
                avg_cost_for_two=float(row["avg_cost_for_two"]),
                votes=int(row["votes"]),
                match_features=MatchFeatures(
                    budget_fit=float(row["budget_fit"]),
                    cuisine_match=float(row["cuisine_match"]),
                    rating_pass=bool(row["rating"] >= preference.min_rating),
                ),
                baseline_score=float(row["baseline_score"]),
            )
        )

    return RetrievalResult(total_after_hard_filters=total_after_hard_filters, candidates=candidates)

