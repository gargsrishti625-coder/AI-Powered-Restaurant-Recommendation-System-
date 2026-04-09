from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


REQUIRED_COLUMNS: tuple[str, ...] = (
    "restaurant_id",
    "name",
    "city",
    "locality",
    "cuisines",
    "avg_cost_for_two",
    "rating",
    "votes",
    "currency",
    "last_updated_at",
)


@dataclass
class ValidationResult:
    total_rows: int
    passed_rows: int
    pass_ratio: float
    missing_required_columns: list[str]
    null_counts_required: dict[str, int]
    invalid_rating_count: int
    invalid_cost_count: int

    def to_dict(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "passed_rows": self.passed_rows,
            "pass_ratio": self.pass_ratio,
            "missing_required_columns": self.missing_required_columns,
            "null_counts_required": self.null_counts_required,
            "invalid_rating_count": self.invalid_rating_count,
            "invalid_cost_count": self.invalid_cost_count,
        }


def validate_restaurants_schema(
    df: pd.DataFrame, required_columns: Iterable[str] = REQUIRED_COLUMNS
) -> ValidationResult:
    required_columns = tuple(required_columns)
    missing_required_columns = [col for col in required_columns if col not in df.columns]

    null_counts_required: dict[str, int] = {}
    for col in required_columns:
        if col in df.columns:
            null_counts_required[col] = int(df[col].isna().sum())
        else:
            null_counts_required[col] = len(df)

    invalid_rating_count = 0
    if "rating" in df.columns:
        rating = pd.to_numeric(df["rating"], errors="coerce")
        invalid_rating_count = int(((rating < 0) | (rating > 5) | rating.isna()).sum())

    invalid_cost_count = 0
    if "avg_cost_for_two" in df.columns:
        cost = pd.to_numeric(df["avg_cost_for_two"], errors="coerce")
        invalid_cost_count = int(((cost < 0) | cost.isna()).sum())

    total_rows = len(df)
    valid_row_mask = pd.Series([True] * total_rows)

    for col in required_columns:
        if col in df.columns:
            valid_row_mask &= df[col].notna()
        else:
            valid_row_mask &= False

    if "rating" in df.columns:
        rating = pd.to_numeric(df["rating"], errors="coerce")
        valid_row_mask &= rating.between(0, 5, inclusive="both")
    else:
        valid_row_mask &= False

    if "avg_cost_for_two" in df.columns:
        cost = pd.to_numeric(df["avg_cost_for_two"], errors="coerce")
        valid_row_mask &= cost >= 0
    else:
        valid_row_mask &= False

    passed_rows = int(valid_row_mask.sum())
    pass_ratio = (passed_rows / total_rows) if total_rows else 0.0

    return ValidationResult(
        total_rows=total_rows,
        passed_rows=passed_rows,
        pass_ratio=pass_ratio,
        missing_required_columns=missing_required_columns,
        null_counts_required=null_counts_required,
        invalid_rating_count=invalid_rating_count,
        invalid_cost_count=invalid_cost_count,
    )

