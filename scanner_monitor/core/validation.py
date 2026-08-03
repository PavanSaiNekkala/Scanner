"""
scanner_monitor.core.validation
===============================

Validation utilities for the Institutional Scanner Monitor.

This module provides reusable validation helpers for DataFrames,
columns, files, directories, numeric values, text values, duplicates,
missing values, and dataset summaries.

All public APIs are preserved for backward compatibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Final

import pandas as pd

__all__ = [
    # DataFrame
    "is_dataframe",
    "is_empty",
    "validate_dataframe",
    # Columns
    "has_column",
    "has_columns",
    "missing_columns",
    # Files
    "file_exists",
    "directory_exists",
    # Numeric
    "is_numeric",
    "between",
    # Text
    "not_blank",
    # Duplicates
    "duplicate_rows",
    "duplicate_values",
    # Missing Values
    "missing_values",
    "missing_by_column",
    # Shape
    "row_count",
    "column_count",
    # Summary
    "validation_summary",
]

_EMPTY_SERIES: Final[pd.Series] = pd.Series(dtype=int)

# =============================================================================
# DataFrame Validation
# =============================================================================


def is_dataframe(
    df: Any,
) -> bool:
    """
    Return True if the object is a pandas DataFrame.
    """

    return isinstance(df, pd.DataFrame)


def is_empty(
    df: pd.DataFrame | None,
) -> bool:
    """
    Return True if the DataFrame is None
    or contains no rows.
    """

    return (
        df is None
        or df.empty
    )


def validate_dataframe(
    df: pd.DataFrame | None,
) -> bool:
    """
    Validate that an object is a
    non-empty DataFrame.
    """

    return (
        is_dataframe(df)
        and not is_empty(df)
    )


# =============================================================================
# Column Validation
# =============================================================================


def has_column(
    df: pd.DataFrame,
    column: str,
) -> bool:
    """
    Return True if the DataFrame
    contains the specified column.
    """

    return (
        validate_dataframe(df)
        and column in df.columns
    )


def has_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...],
) -> bool:
    """
    Return True if all requested
    columns exist.
    """

    if not validate_dataframe(df):
        return False

    available = set(df.columns)

    return all(
        column in available
        for column in columns
    )


def missing_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...],
) -> list[str]:
    """
    Return the missing columns.
    """

    if not is_dataframe(df):
        return list(columns)

    available = set(df.columns)

    return [
        column
        for column in columns
        if column not in available
    ]


# =============================================================================
# File Validation
# =============================================================================


def file_exists(
    path: str | Path,
) -> bool:
    """
    Return True if the file exists.
    """

    return Path(path).is_file()


def directory_exists(
    path: str | Path,
) -> bool:
    """
    Return True if the directory exists.
    """

    return Path(path).is_dir()


# =============================================================================
# Numeric Validation
# =============================================================================


def is_numeric(
    value: Any,
) -> bool:
    """
    Return True if the value is numeric.

    Boolean values are excluded.
    """

    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def between(
    value: float,
    minimum: float,
    maximum: float,
) -> bool:
    """
    Return True if the value falls
    within the inclusive range.
    """

    return minimum <= value <= maximum


# =============================================================================
# Text Validation
# =============================================================================


def not_blank(
    value: str | None,
) -> bool:
    """
    Return True if the string is
    not None and not empty.
    """

    return (
        value is not None
        and bool(value.strip())
    )


# =============================================================================
# Duplicate Detection
# =============================================================================


def duplicate_rows(
    df: pd.DataFrame,
) -> int:
    """
    Return the number of duplicate rows.
    """

    if not validate_dataframe(df):
        return 0

    return int(
        df.duplicated().sum()
    )


def duplicate_values(
    df: pd.DataFrame,
    column: str,
) -> int:
    """
    Return the number of duplicate
    values within a column.
    """

    if not has_column(df, column):
        return 0

    return int(
        df[column]
        .duplicated()
        .sum()
    )


# =============================================================================
# Missing Values
# =============================================================================


def missing_values(
    df: pd.DataFrame,
) -> int:
    """
    Return the total number of
    missing values.
    """

    if not validate_dataframe(df):
        return 0

    return int(
        df.isna()
        .sum()
        .sum()
    )


def missing_by_column(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Return missing values
    grouped by column.
    """

    if not validate_dataframe(df):
        return _EMPTY_SERIES.copy()

    return df.isna().sum()


# =============================================================================
# Shape
# =============================================================================


def row_count(
    df: pd.DataFrame,
) -> int:
    """
    Return the number of rows.
    """

    if not validate_dataframe(df):
        return 0

    return int(df.shape[0])


def column_count(
    df: pd.DataFrame,
) -> int:
    """
    Return the number of columns.
    """

    if not validate_dataframe(df):
        return 0

    return int(df.shape[1])


# =============================================================================
# Summary
# =============================================================================


def validation_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return a validation summary
    for a DataFrame.
    """

    valid = validate_dataframe(df)

    return {
        "valid": valid,
        "rows": row_count(df),
        "columns": column_count(df),
        "duplicates": duplicate_rows(df),
        "missing_values": missing_values(df),
    }