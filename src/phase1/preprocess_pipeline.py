from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Iterable

import pandas as pd


PREFERRED_COLUMN_MAPPING = {
    "Restaurant Name": "name",
    "restaurant_name": "name",
    "City": "city",
    "city": "city",
    "Locality": "locality",
    "locality": "locality",
    "Cuisines": "cuisines",
    "cuisines": "cuisines",
    "Average Cost for two": "avg_cost_for_two",
    "avg_cost_for_two": "avg_cost_for_two",
    "Aggregate rating": "rating",
    "rating": "rating",
    "Votes": "votes",
    "votes": "votes",
    "Currency": "currency",
    "currency": "currency",
    "Has Table booking": "is_table_booking",
    "is_table_booking": "is_table_booking",
    "Has Online delivery": "is_online_delivery",
    "is_online_delivery": "is_online_delivery",
    "Restaurant ID": "restaurant_id",
    "restaurant_id": "restaurant_id",
    "name": "name",
    "location": "locality",
    "listed_in(city)": "city",
    "rate": "rating",
    "approx_cost(for two people)": "avg_cost_for_two",
    "online_order": "is_online_delivery",
    "book_table": "is_table_booking",
}


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return re.sub(r"\s+", " ", text)


def _normalize_title_case(series: pd.Series) -> pd.Series:
    return series.map(lambda x: _clean_text(x).title() if _clean_text(x) else None)


def _normalize_cuisines(series: pd.Series) -> pd.Series:
    def _split(v: object) -> str | None:
        text = _clean_text(v)
        if not text:
            return None
        cuisines = [c.strip().title() for c in text.split(",") if c.strip()]
        if not cuisines:
            return None
        return ", ".join(sorted(set(cuisines)))

    return series.map(_split)


def _parse_rating(series: pd.Series) -> pd.Series:
    def parse(v: object) -> float | None:
        text = _clean_text(v)
        if text is None:
            return None
        if "/" in text:
            text = text.split("/", 1)[0].strip()
        if text.lower() in {"new", "-", "nan"}:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    return series.map(parse)


def _parse_cost(series: pd.Series) -> pd.Series:
    def parse(v: object) -> float | None:
        text = _clean_text(v)
        if text is None:
            return None
        cleaned = re.sub(r"[^\d.]", "", text)
        if cleaned == "":
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    return series.map(parse)


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _to_bool(series: pd.Series) -> pd.Series:
    truthy = {"yes", "true", "1", "y"}
    falsy = {"no", "false", "0", "n"}

    def convert(v: object) -> bool | None:
        text = _clean_text(v)
        if text is None:
            return None
        low = text.lower()
        if low in truthy:
            return True
        if low in falsy:
            return False
        return None

    return series.map(convert)


def _pick_existing_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    return [c for c in columns if c in df.columns]


def preprocess_restaurants(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(columns={k: v for k, v in PREFERRED_COLUMN_MAPPING.items() if k in df.columns})
    curated = pd.DataFrame()

    if "restaurant_id" in renamed.columns:
        curated["restaurant_id"] = renamed["restaurant_id"].map(_clean_text)
    else:
        curated["restaurant_id"] = renamed.index.astype(str)

    curated["name"] = renamed["name"].map(_clean_text) if "name" in renamed.columns else None
    curated["city"] = _normalize_title_case(renamed["city"]) if "city" in renamed.columns else None
    curated["locality"] = _normalize_title_case(renamed["locality"]) if "locality" in renamed.columns else None
    curated["cuisines"] = _normalize_cuisines(renamed["cuisines"]) if "cuisines" in renamed.columns else None
    curated["avg_cost_for_two"] = (
        _parse_cost(renamed["avg_cost_for_two"]) if "avg_cost_for_two" in renamed.columns else None
    )
    curated["rating"] = _parse_rating(renamed["rating"]) if "rating" in renamed.columns else None
    curated["votes"] = _to_numeric(renamed["votes"]).fillna(0).astype("Int64") if "votes" in renamed.columns else 0
    curated["currency"] = renamed["currency"].map(_clean_text) if "currency" in renamed.columns else "INR"
    curated["is_table_booking"] = (
        _to_bool(renamed["is_table_booking"]) if "is_table_booking" in renamed.columns else None
    )
    curated["is_online_delivery"] = (
        _to_bool(renamed["is_online_delivery"]) if "is_online_delivery" in renamed.columns else None
    )
    curated["tags"] = None
    curated["last_updated_at"] = datetime.now(timezone.utc).isoformat()

    curated["quality_flag_missing_required"] = curated[
        ["name", "city", "cuisines", "avg_cost_for_two", "rating"]
    ].isna().any(axis=1)

    curated.loc[~curated["rating"].between(0, 5, inclusive="both"), "rating"] = pd.NA
    curated.loc[curated["avg_cost_for_two"] < 0, "avg_cost_for_two"] = pd.NA
    curated.loc[curated["votes"] < 0, "votes"] = 0

    required_for_serving = ["name", "city", "locality", "cuisines", "avg_cost_for_two", "rating"]
    curated = curated.dropna(subset=required_for_serving).reset_index(drop=True)

    dedupe_keys = _pick_existing_columns(curated, ["restaurant_id", "name", "city", "locality"])
    curated = curated.drop_duplicates(subset=dedupe_keys, keep="first").reset_index(drop=True)

    fallback_ids = pd.Series(curated.index.astype(str), index=curated.index)
    curated["restaurant_id"] = curated["restaurant_id"].fillna(fallback_ids)
    curated["votes"] = curated["votes"].fillna(0).astype("Int64")

    return curated


def generate_quality_report(df: pd.DataFrame) -> dict:
    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "null_ratio_by_column": {col: float(df[col].isna().mean()) for col in df.columns},
        "unique_count_by_key_columns": {
            "restaurant_id": int(df["restaurant_id"].nunique()) if "restaurant_id" in df.columns else 0,
            "name": int(df["name"].nunique()) if "name" in df.columns else 0,
            "city": int(df["city"].nunique()) if "city" in df.columns else 0,
        },
        "range_checks": {
            "rating_min": float(df["rating"].min()) if "rating" in df.columns and len(df) else None,
            "rating_max": float(df["rating"].max()) if "rating" in df.columns and len(df) else None,
            "cost_min": float(df["avg_cost_for_two"].min())
            if "avg_cost_for_two" in df.columns and len(df)
            else None,
            "cost_max": float(df["avg_cost_for_two"].max())
            if "avg_cost_for_two" in df.columns and len(df)
            else None,
        },
    }
    return report

