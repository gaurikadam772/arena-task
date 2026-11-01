"""Load, validate and clean the raw sales data."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .config import REQUIRED_COLUMNS

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when the input data is unusable (empty, wrong schema, ...)."""


def validate_schema(df: pd.DataFrame) -> None:
    """Check that the frame is non-empty and has every required column."""
    if df is None or df.empty:
        raise DataValidationError("The dataset contains no rows.")
    normalised = {str(c).strip().lower() for c in df.columns}
    missing = [c for c in REQUIRED_COLUMNS if c not in normalised]
    if missing:
        raise DataValidationError(f"Missing required column(s): {', '.join(missing)}")


def load_data(path: str | Path) -> pd.DataFrame:
    """Read the CSV file and validate its structure.

    Raises:
        FileNotFoundError: the file does not exist.
        DataValidationError: the file is empty, unreadable or has the wrong columns.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise DataValidationError(f"The file is empty: {path}") from exc
    except pd.errors.ParserError as exc:
        raise DataValidationError(f"The file is not valid CSV: {exc}") from exc
    validate_schema(df)
    logger.info("Loaded %d rows x %d columns from %s", *df.shape, path.name)
    return df


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the raw frame and return ``(clean_df, cleaning_log)``.

    Steps (each count is recorded in the log):
      1. normalise column names and text columns
      2. drop exact duplicate rows (there is no order id, so identical rows
         are treated as accidental repeats)
      3. coerce types; drop rows with unparseable / missing values
      4. drop rows with non-positive quantity or price
      5. derive ``revenue``, ``month`` and ``weekday``
    """
    validate_schema(df)
    log: dict = {"rows_raw": int(len(df))}

    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df[REQUIRED_COLUMNS]
    for col in ("product", "category"):
        df[col] = df[col].astype("string").str.strip()

    before = len(df)
    df = df.drop_duplicates()
    log["duplicates_removed"] = int(before - len(df))

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    log["missing_or_invalid_removed"] = int(before - len(df))

    before = len(df)
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    log["non_positive_removed"] = int(before - len(df))

    if df.empty:
        raise DataValidationError("No valid rows remain after cleaning.")

    df["quantity"] = df["quantity"].astype(int)
    df["product"] = df["product"].astype(str)
    df["category"] = df["category"].astype(str)
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["date"].dt.day_name()
    df = df.sort_values("date").reset_index(drop=True)

    log["rows_clean"] = int(len(df))
    log["rows_removed_total"] = log["rows_raw"] - log["rows_clean"]
    logger.info("Cleaning log: %s", log)
    return df, log
