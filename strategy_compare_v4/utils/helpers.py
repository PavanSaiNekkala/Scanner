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

Provides
--------
• DataFrame validation
• Safe DataFrame manipulation
• Directory management
• Column utilities
• Dataset summary

=============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd


# ============================================================
# Column Validation
# ============================================================

def require_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """
    Validate that a DataFrame contains all required columns.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(sorted(missing))
        )


# ============================================================
# DataFrame Copy
# ============================================================

def copy_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return a deep defensive copy.
    """

    return df.copy(deep=True)


# ============================================================
# Empty DataFrame
# ============================================================

def is_empty(
    df: pd.DataFrame | None,
) -> bool:
    """
    Check whether a DataFrame is None or empty.
    """

    return df is None or df.empty


# ============================================================
# Ensure Directory
# ============================================================

def ensure_directory(
    directory: str | Path,
) -> Path:
    """
    Create a directory if it does not exist.
    """

    path = Path(directory)

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
    Safely sort a DataFrame.

    Returns the original DataFrame if the
    requested column does not exist.
    """

    if column not in df.columns:
        return df

    return (
        df.sort_values(
            by=column,
            ascending=ascending,
        )
        .reset_index(drop=True)
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
    Move a column to a specified position.
    """

    if column not in df.columns:
        return df

    columns = list(df.columns)

    columns.remove(column)

    columns.insert(position, column)

    return df.loc[:, columns]


# ============================================================
# First Existing Column
# ============================================================

def first_existing_column(
    df: pd.DataFrame,
    candidates: Iterable[str],
) -> str | None:
    """
    Return the first matching column.
    """

    return next(
        (
            column
            for column in candidates
            if column in df.columns
        ),
        None,
    )


# ============================================================
# Safe Rename
# ============================================================

def safe_rename(
    df: pd.DataFrame,
    mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Rename only columns that exist.
    """

    valid_mapping = {
        old: new
        for old, new in mapping.items()
        if old in df.columns
    }

    return df.rename(columns=valid_mapping)


# ============================================================
# DataFrame Summary
# ============================================================

def dataframe_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return a basic DataFrame summary.
    """

    return {
        "Rows": int(len(df)),
        "Columns": int(df.shape[1]),
        "Missing Values": int(df.isna().sum().sum()),
        "Duplicate Rows": int(df.duplicated().sum()),
    }