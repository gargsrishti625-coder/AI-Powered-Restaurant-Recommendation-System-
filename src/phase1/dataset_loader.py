from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_hf_dataset(dataset_name: str, split: str = "train") -> pd.DataFrame:
    try:
        from datasets import load_dataset
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'datasets' package is required for Hugging Face loading. "
            "Install dependencies from requirements.txt or use local CSV ingestion."
        ) from exc

    dataset = load_dataset(dataset_name, split=split)
    return dataset.to_pandas()


def load_local_raw_snapshot(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def save_raw_snapshot(df: pd.DataFrame, output_dir: Path, filename: str = "raw.csv") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    df.to_csv(output_path, index=False)
    return output_path

