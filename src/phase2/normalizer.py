from __future__ import annotations

import re
from typing import List, Tuple

from src.phase2.config import PreferenceConfig
from src.phase2.models import BudgetRange, RawPreferenceInput, UserPreference


class PreferenceValidationError(ValueError):
    pass


def _normalize_city(raw: str | None) -> str:
    if not raw or not raw.strip():
        raise PreferenceValidationError("location is required.")
    return raw.strip().title()


def _normalize_budget(raw: str | None, cfg: PreferenceConfig) -> Tuple[BudgetRange, str]:
    label = "medium" if not raw else raw.strip().lower()
    if label in {"low", "cheap", "budget"}:
        label = "low"
    elif label in {"mid", "medium", "moderate", "normal"}:
        label = "medium"
    elif label in {"high", "premium", "expensive"}:
        label = "high"

    if label not in cfg.budget.buckets:
        raise PreferenceValidationError(f"budget must be one of low/medium/high, got '{raw}'.")

    min_cost, max_cost = cfg.budget.buckets[label]
    return BudgetRange(min_cost=min_cost, max_cost=max_cost), label


def _normalize_cuisines(raw: str | None, cfg: PreferenceConfig) -> List[str]:
    if not raw:
        return []

    tokens = [c.strip().lower() for c in raw.split(",") if c.strip()]
    normalized: List[str] = []
    for token in tokens:
        base = cfg.cuisine_synonyms.synonyms.get(token, token)
        label = base.title()
        if label not in normalized:
            normalized.append(label)
    return normalized


def _normalize_min_rating(raw: float | None, cfg: PreferenceConfig) -> float:
    if raw is None:
        return cfg.default_min_rating
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise PreferenceValidationError("min_rating must be a number.") from exc
    if value < 0 or value > 5:
        raise PreferenceValidationError("min_rating must be between 0 and 5.")
    return value


def _extract_keywords_and_sort_bias(text: str | None, cfg: PreferenceConfig) -> tuple[list[str], list[str]]:
    if not text:
        return [], []

    content = text.lower()
    keywords: set[str] = set()
    sort_bias: set[str] = set()

    for bias, lexemes in cfg.keyword_lexicon.items():
        for lexeme in lexemes:
            if re.search(rf"\b{re.escape(lexeme)}\b", content):
                sort_bias.add(bias)
                keywords.add(lexeme)

    extra_tokens = [word for word in re.findall(r"[a-zA-Z]+", content) if len(word) > 3]
    for token in extra_tokens:
        keywords.add(token)

    return sorted(keywords), sorted(sort_bias)


def normalize_user_preference(
    raw: RawPreferenceInput, cfg: PreferenceConfig | None = None
) -> UserPreference:
    cfg = cfg or PreferenceConfig()

    city = _normalize_city(raw.location)
    budget_range, _ = _normalize_budget(raw.budget, cfg)
    cuisines = _normalize_cuisines(raw.cuisine, cfg)
    min_rating = _normalize_min_rating(raw.min_rating, cfg)
    keywords, sort_bias = _extract_keywords_and_sort_bias(raw.additional_preferences, cfg)

    return UserPreference(
        city=city,
        budget_range=budget_range,
        cuisine_preferences=cuisines,
        min_rating=min_rating,
        keywords=keywords,
        sort_bias=sort_bias,
    )

