from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RawPreferenceInput:
    location: Optional[str] = None
    budget: Optional[str] = None
    cuisine: Optional[str] = None
    min_rating: Optional[float] = None
    additional_preferences: Optional[str] = None


@dataclass
class BudgetRange:
    min_cost: float
    max_cost: Optional[float]


@dataclass
class UserPreference:
    city: str
    budget_range: BudgetRange
    cuisine_preferences: List[str]
    min_rating: float
    keywords: List[str]
    sort_bias: List[str]

