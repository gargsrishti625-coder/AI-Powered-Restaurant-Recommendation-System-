from __future__ import annotations

import json

from src.phase1.config import Phase1Config
from src.phase1.dataset_loader import (
    load_hf_dataset,
    load_local_raw_snapshot,
    save_raw_snapshot,
)
from src.phase1.db_writer import save_processed_snapshot, write_restaurants_to_db
from src.phase1.preprocess_pipeline import generate_quality_report, preprocess_restaurants
from src.phase1.schema import validate_restaurants_schema


def run_phase1_pipeline(config: Phase1Config | None = None) -> dict:
    cfg = config or Phase1Config()
    cfg.raw_dir.mkdir(parents=True, exist_ok=True)
    cfg.processed_dir.mkdir(parents=True, exist_ok=True)
    cfg.quality_report_dir.mkdir(parents=True, exist_ok=True)
    cfg.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    raw_snapshot = cfg.raw_dir / "zomato_raw.csv"
    data_source = "unknown"

    def _load_from_hf() -> tuple:
        df = load_hf_dataset(cfg.dataset_name, cfg.dataset_split)
        snapshot = save_raw_snapshot(df, cfg.raw_dir, "zomato_raw.csv")
        return df, snapshot, "huggingface"

    def _load_from_local() -> tuple:
        if cfg.local_csv_path.exists():
            df = load_local_raw_snapshot(cfg.local_csv_path)
            snapshot = save_raw_snapshot(df, cfg.raw_dir, "zomato_raw.csv")
            return df, snapshot, "local_csv"
        if raw_snapshot.exists():
            df = load_local_raw_snapshot(raw_snapshot)
            return df, raw_snapshot, "local_snapshot"
        raise FileNotFoundError(
            f"No local CSV found at {cfg.local_csv_path} and no snapshot at {raw_snapshot}."
        )

    loaders = [_load_from_hf, _load_from_local]
    if cfg.source_priority.lower() == "local":
        loaders = [_load_from_local, _load_from_hf]

    last_error = None
    for loader in loaders:
        try:
            raw_df, raw_snapshot, data_source = loader()
            break
        except Exception as exc:
            last_error = exc
    else:
        raise RuntimeError(
            "Unable to load dataset from configured sources. "
            "Set PHASE1_SOURCE_PRIORITY=local to skip Hugging Face, "
            "or ensure network and dependencies are available."
        ) from last_error

    curated_df = preprocess_restaurants(raw_df)
    processed_snapshot = save_processed_snapshot(curated_df, cfg.processed_dir, "zomato_curated.csv")

    validation_result = validate_restaurants_schema(curated_df)
    quality_report = generate_quality_report(curated_df)
    quality_report["schema_validation"] = validation_result.to_dict()

    report_path = cfg.quality_report_dir / "phase1_quality_report.json"
    report_path.write_text(json.dumps(quality_report, indent=2), encoding="utf-8")

    write_restaurants_to_db(curated_df, cfg.db_url, cfg.table_name, if_exists="replace")

    summary = {
        "data_source": data_source,
        "raw_snapshot": str(raw_snapshot),
        "processed_snapshot": str(processed_snapshot),
        "quality_report": str(report_path),
        "db_url": cfg.db_url,
        "table_name": cfg.table_name,
        "total_rows": len(curated_df),
        "schema_pass_ratio": validation_result.pass_ratio,
    }
    return summary


def run_and_print_summary() -> None:
    summary = run_phase1_pipeline()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run_and_print_summary()

