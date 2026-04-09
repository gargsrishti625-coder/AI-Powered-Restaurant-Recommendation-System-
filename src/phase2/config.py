from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class BudgetConfig:
    buckets: Dict[str, Tuple[float, float | None]] = field(
        default_factory=lambda: {
            "low": (0.0, 700.0),
            "medium": (700.0, 2000.0),
            "high": (2000.0, None),
        }
    )


@dataclass(frozen=True)
class CuisineSynonymConfig:
    synonyms: Dict[str, str] = field(
        default_factory=lambda: {
            "north indian": "indian",
            "south indian": "indian",
            "mughlai": "indian",
            "american": "american",
            "fast food": "fast food",
            "italian": "italian",
            "chinese": "chinese",
            "cafe": "cafe",
        }
    )


@dataclass(frozen=True)
class PreferenceConfig:
    budget: BudgetConfig = BudgetConfig()
    cuisine_synonyms: CuisineSynonymConfig = CuisineSynonymConfig()
    default_min_rating: float = 3.5
    keyword_lexicon: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "family": ["family", "kids", "child", "children"],
            "quick": ["quick", "fast", "speed", "rapid"],
            "value": ["cheap", "budget", "value", "affordable"],
            "quality": ["ambience", "experience", "fine dining", "quality"],
        }
    )

