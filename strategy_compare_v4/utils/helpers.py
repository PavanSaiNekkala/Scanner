"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
utils/helpers.py

Purpose
-------
Common helper utilities shared across the
Institutional Strategy Comparison Platform.

=============================================================
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd

# ============================================================
# DataFrame Validation
# ============================================================


def validate_dataframe(
    df: pd.DataFrame | None,
) -> None:
    """
    Validate a DataFrame.
    """

    if df is None:
        raise ValueError("DataFrame is None.")

    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise TypeError("Expected pandas DataFrame.")


def require_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """
    Validate required columns.
    """

    validate_dataframe(df)

    missing = sorted(column for column in required_columns if column not in df.columns)

    if missing:
        raise ValueError("Missing required columns:\n" + "\n".join(missing))


def missing_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> list[str]:
    """
    Return missing columns.
    """

    validate_dataframe(df)

    return sorted(column for column in required_columns if column not in df.columns)


# ============================================================
# DataFrame Utilities
# ============================================================


def copy_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Deep copy.
    """

    validate_dataframe(df)

    return df.copy(
        deep=True,
    )


def is_empty(
    df: pd.DataFrame | None,
) -> bool:
    """
    Check whether DataFrame is empty.
    """

    return df is None or df.empty


# ============================================================
# Directory Utilities
# ============================================================


def ensure_directory(
    directory: str | Path,
) -> Path:
    """
    Create directory if required.
    """

    path = Path(
        directory,
    )

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


# ============================================================
# Safe Sorting
# ============================================================


def sort_dataframe(
    df: pd.DataFrame,
    column: str,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Stable DataFrame sorting.
    """

    validate_dataframe(df)

    if column not in df.columns:
        return df

    return df.sort_values(
        by=column,
        ascending=ascending,
        kind="stable",
    ).reset_index(
        drop=True,
    )


# ============================================================
# Column Utilities
# ============================================================


def first_existing_column(
    df: pd.DataFrame,
    candidates: Iterable[str],
) -> str | None:
    """
    Return first existing column.
    """

    validate_dataframe(df)

    return next(
        (column for column in candidates if column in df.columns),
        None,
    )


# ============================================================
# Move Column
# ============================================================


def move_column(
    df: pd.DataFrame,
    column: str,
    position: int,
) -> pd.DataFrame:
    """
    Move a column to the specified position.
    """

    validate_dataframe(df)

    if column not in df.columns:
        return df

    columns = list(df.columns)

    columns.remove(column)

    position = max(
        0,
        min(position, len(columns)),
    )

    columns.insert(
        position,
        column,
    )

    return df.loc[:, columns]


# ============================================================
# Safe Rename
# ============================================================


def safe_rename(
    df: pd.DataFrame,
    mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Rename only existing columns.
    """

    validate_dataframe(df)

    valid_mapping = {old: new for old, new in mapping.items() if old in df.columns}

    return df.rename(
        columns=valid_mapping,
    )


# ============================================================
# Column Utilities
# ============================================================


def column_exists(
    df: pd.DataFrame,
    column: str,
) -> bool:
    """
    Return True if the column exists.
    """

    validate_dataframe(df)

    return column in df.columns


def safe_get_column(
    df: pd.DataFrame,
    column: str,
    default: Any = None,
):
    """
    Safely retrieve a column.

    Returns
    -------
    pandas.Series | Any
        Column if present, otherwise default.
    """

    validate_dataframe(df)

    if column in df.columns:
        return df[column]

    return default


# ============================================================
# Numeric Utilities
# ============================================================


def ensure_numeric_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
) -> pd.DataFrame:
    """
    Convert specified columns to numeric.
    Invalid values become NaN.
    """

    validate_dataframe(df)

    df = df.copy()

    existing = [column for column in columns if column in df.columns]

    for column in existing:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


# ============================================================
# Normalization Utilities
# ============================================================


def normalize(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize numeric values to 0-100 scale.

    Used for institutional scoring models.

    Formula
    -------
    ((value - min) / (max - min)) * 100

    Returns
    -------
    pandas.Series
    """

    if not isinstance(
        series,
        pd.Series,
    ):
        raise TypeError("Expected pandas Series.")

    series = pd.to_numeric(
        series,
        errors="coerce",
    )

    minimum = series.min()

    maximum = series.max()

    # Avoid division by zero
    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(
            0,
            index=series.index,
        )

    if maximum == minimum:
        return pd.Series(
            50,
            index=series.index,
        )

    return (series - minimum) / (maximum - minimum) * 100


# ============================================================
# Duplicate Summary
# ============================================================


def duplicate_summary(
    df: pd.DataFrame,
) -> dict[str, int]:
    """
    Return duplicate statistics.
    """

    validate_dataframe(df)

    duplicates = int(df.duplicated().sum())

    unique = int(len(df) - duplicates)

    return {
        "Duplicate Rows": duplicates,
        "Unique Rows": unique,
    }


# ============================================================
# DataFrame Summary
# ============================================================


def dataframe_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return DataFrame summary statistics.
    """

    validate_dataframe(df)

    return {
        "Rows": int(len(df)),
        "Columns": int(df.shape[1]),
        "Missing Values": int(df.isna().sum().sum()),
        "Duplicate Rows": int(df.duplicated().sum()),
        "Memory Usage (Bytes)": int(
            df.memory_usage(
                deep=True,
            ).sum()
        ),
    }


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "validate_dataframe",
    "require_columns",
    "missing_columns",
    "copy_dataframe",
    "is_empty",
    "ensure_directory",
    "sort_dataframe",
    "move_column",
    "first_existing_column",
    "safe_rename",
    "column_exists",
    "safe_get_column",
    "ensure_numeric_columns",
    "normalize",
    "duplicate_summary",
    "dataframe_summary",
]
