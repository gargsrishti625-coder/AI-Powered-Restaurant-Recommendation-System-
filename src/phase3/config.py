from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


# All localities in the dataset belong to Bangalore.
# Map "bangalore" and "bengaluru" to all known locality names so that
# users typing the parent city get results from the full dataset.
_BANGALORE_LOCALITIES = [
    "Banashankari", "Bannerghatta Road", "Basavanagudi", "Bellandur",
    "Brigade Road", "Brookefield", "Btm", "Church Street", "Electronic City",
    "Frazer Town", "Hsr", "Indiranagar", "Jayanagar", "Jp Nagar",
    "Kalyan Nagar", "Kammanahalli", "Koramangala 4Th Block",
    "Koramangala 5Th Block", "Koramangala 6Th Block", "Koramangala 7Th Block",
    "Lavelle Road", "Malleshwaram", "Marathahalli", "Mg Road", "New Bel Road",
    "Old Airport Road", "Rajajinagar", "Residency Road", "Sarjapur Road",
    "Whitefield",
]


@dataclass(frozen=True)
class Phase3Config:
    workspace_root: Path = Path(
        os.getenv("WORKSPACE_ROOT", Path(__file__).resolve().parents[2])
    )
    curated_csv_path: Path = workspace_root / "data" / "processed" / "zomato_curated.csv"
    top_n_candidates: int = int(os.getenv("PHASE3_TOP_N_CANDIDATES", "20"))

    # Baseline scoring weights from architecture.
    weight_rating: float = 0.40
    weight_cuisine: float = 0.25
    weight_budget: float = 0.20
    weight_popularity: float = 0.15

    # City group aliases: maps a user-facing city name (lowercase) to a list
    # of dataset city values it covers.
    city_groups: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "bangalore": _BANGALORE_LOCALITIES,
            "bengaluru": _BANGALORE_LOCALITIES,
        }
    )

