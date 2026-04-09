from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def write_restaurants_to_db(
    df: pd.DataFrame, db_url: str, table_name: str = "restaurants", if_exists: str = "replace"
) -> None:
    if db_url.startswith("sqlite:///"):
        sqlite_path = db_url.replace("sqlite:///", "", 1)
        with sqlite3.connect(sqlite_path) as connection:
            df.to_sql(table_name, con=connection, if_exists=if_exists, index=False)
        return

    try:
        from sqlalchemy import create_engine
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "SQLAlchemy is required for non-sqlite database URLs. Install dependencies from requirements.txt."
        ) from exc

    engine = create_engine(db_url)
    with engine.begin() as connection:
        df.to_sql(table_name, con=connection, if_exists=if_exists, index=False)


def save_processed_snapshot(
    df: pd.DataFrame, output_dir: Path, filename: str = "restaurants_curated.csv"
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    df.to_csv(output_path, index=False)
    return output_path

