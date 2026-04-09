from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Phase1Config:
    dataset_name: str = os.getenv(
        "HF_DATASET_NAME", "ManikaSaini/zomato-restaurant-recommendation"
    )
    dataset_split: str = os.getenv("HF_DATASET_SPLIT", "train")
    source_priority: str = os.getenv("PHASE1_SOURCE_PRIORITY", "huggingface")
    workspace_root: Path = Path(
        os.getenv("WORKSPACE_ROOT", Path(__file__).resolve().parents[2])
    )
    raw_dir: Path = workspace_root / "data" / "raw"
    local_csv_path: Path = Path(
        os.getenv("PHASE1_LOCAL_CSV_PATH", workspace_root / "data" / "zomato.csv")
    )
    processed_dir: Path = workspace_root / "data" / "processed"
    quality_report_dir: Path = workspace_root / "data" / "quality_reports"
    sqlite_path: Path = workspace_root / "data" / "restaurants.db"
    table_name: str = os.getenv("PHASE1_TABLE_NAME", "restaurants")

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.sqlite_path}"

