"""
core/validation.py
==================

Validation utilities for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

# =============================================================================
# DataFrame Validation
# =============================================================================


def is_dataframe(
    df: Any,
) -> bool:
    """
    Return True if object is a DataFrame.
    """

    return isinstance(
        df,
        pd.DataFrame,
    )


def is_empty(
    df: pd.DataFrame,
) -> bool:
    """
    Check whether a DataFrame is empty.
    """

    return (

        df is None

        or df.empty

    )


def validate_dataframe(
    df: pd.DataFrame,
) -> bool:
    """
    Validate a DataFrame.
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
    Check if a column exists.
    """

    return (

        validate_dataframe(df)

        and column in df.columns

    )


def has_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> bool:
    """
    Check whether all columns exist.
    """

    if not validate_dataframe(df):

        return False

    return all(

        column in df.columns

        for column in columns

    )


def missing_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> list[str]:
    """
    Return missing columns.
    """

    if not is_dataframe(df):

        return columns

    return [

        column

        for column in columns

        if column not in df.columns

    ]


# =============================================================================
# File Validation
# =============================================================================


def file_exists(
    path: str | Path,
) -> bool:
    """
    Check file existence.
    """

    return Path(

        path,

    ).exists()


def directory_exists(
    path: str | Path,
) -> bool:
    """
    Check directory existence.
    """

    return Path(

        path,

    ).is_dir()


# =============================================================================
# Numeric Validation
# =============================================================================


def is_numeric(
    value: Any,
) -> bool:
    """
    Check numeric values.
    """

    return isinstance(

        value,

        (

            int,

            float,

        ),

    )


def between(
    value: float,
    minimum: float,
    maximum: float,
) -> bool:
    """
    Check range.
    """

    return minimum <= value <= maximum


# =============================================================================
# Text Validation
# =============================================================================


def not_blank(
    value: str | None,
) -> bool:
    """
    Check non-empty string.
    """

    return (

        value is not None

        and value.strip() != ""

    )


# =============================================================================
# Duplicate Detection
# =============================================================================


def duplicate_rows(
    df: pd.DataFrame,
) -> int:
    """
    Count duplicate rows.
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
    Count duplicate values.
    """

    if not has_column(

        df,

        column,

    ):

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
    Count missing values.
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
    Missing values by column.
    """

    if not validate_dataframe(df):

        return pd.Series(

            dtype=int,

        )

    return df.isna().sum()


# =============================================================================
# Shape
# =============================================================================


def row_count(
    df: pd.DataFrame,
) -> int:
    """
    Number of rows.
    """

    if not validate_dataframe(df):

        return 0

    return len(df)


def column_count(
    df: pd.DataFrame,
) -> int:
    """
    Number of columns.
    """

    if not validate_dataframe(df):

        return 0

    return len(df.columns)


# =============================================================================
# Summary
# =============================================================================


def validation_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Validation report.
    """

    return {

        "valid": validate_dataframe(df),

        "rows": row_count(df),

        "columns": column_count(df),

        "duplicates": duplicate_rows(df),

        "missing_values": missing_values(df),

    }