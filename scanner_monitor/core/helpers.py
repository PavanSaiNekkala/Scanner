"""
scanner_monitor.core.helpers
============================

General helper utilities for the Institutional Scanner Monitor.

This module provides commonly used helper functions for working with
DataFrames, numeric values, formatting, statistics, and dates.

All public APIs are preserved for backward compatibility.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Final

import numpy as np
import pandas as pd

__all__ = [
    # Column Helpers
    "first_existing",
    "existing_columns",
    # Numeric Helpers
    "numeric_series",
    "safe_float",
    "safe_int",
    # DataFrame Helpers
    "copy_dataframe",
    "clean_columns",
    "sort_dataframe",
    # Formatting
    "format_percent",
    "format_number",
    "format_integer",
    "format_datetime",
    # Missing Values
    "fill_missing",
    # Statistics
    "safe_mean",
    "safe_median",
    "safe_std",
    "safe_max",
    "safe_min",
    # Date Helpers
    "today",
    "timestamp",
    # Miscellaneous
    "percentage",
    "unique_count",
    "is_numeric_dtype",
    "replace_inf",
]

# =============================================================================
# Constants
# =============================================================================

DEFAULT_FLOAT: Final[float] = 0.0

DEFAULT_INT: Final[int] = 0

DEFAULT_DATETIME_FORMAT: Final[str] = "%d %b %Y %H:%M:%S"

DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d"

DEFAULT_TIMESTAMP_FORMAT: Final[str] = "%Y%m%d_%H%M%S"

# =============================================================================
# Column Helpers
# =============================================================================

def first_existing(
    df: pd.DataFrame,
    *columns: str,
) -> str | None:
    """
    Return the first matching DataFrame column.

    Matching is case-insensitive and ignores
    leading/trailing whitespace.

    Parameters
    ----------
    df
        Input DataFrame.
    *columns
        Candidate column names.

    Returns
    -------
    str | None
        Matching column name from the DataFrame,
        otherwise ``None``.
    """

    if df.empty and len(df.columns) == 0:
        return None

    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for column in columns:

        key = str(column).strip().lower()

        if key in lookup:
            return lookup[key]

    return None


def existing_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...],
) -> list[str]:
    """
    Return all columns that exist
    in the DataFrame.
    """

    available = set(df.columns)

    return [
        column
        for column in columns
        if column in available
    ]


# =============================================================================
# Numeric Helpers
# =============================================================================

def numeric_series(
    df: pd.DataFrame,
    column: str | None,
) -> pd.Series:
    """
    Return a numeric version of a DataFrame column.

    Missing values are replaced with ``0.0``.

    If the column does not exist, an empty
    float Series is returned.
    """

    if (
        column is None
        or column not in df.columns
    ):
        return pd.Series(
            dtype=float,
        )

    return (
        pd.to_numeric(
            df[column],
            errors="coerce",
        )
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(
            DEFAULT_FLOAT,
        )
    )


def safe_float(
    value: Any,
    default: float = DEFAULT_FLOAT,
) -> float:
    """
    Safely convert a value to float.
    """

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return default


def safe_int(
    value: Any,
    default: int = DEFAULT_INT,
) -> int:
    """
    Safely convert a value to integer.
    """

    try:
        return int(float(value))

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return default


# =============================================================================
# DataFrame Helpers
# =============================================================================

def copy_dataframe(
    df: pd.DataFrame,
    *,
    deep: bool = True,
) -> pd.DataFrame:
    """
    Return a copy of the DataFrame.

    Parameters
    ----------
    deep
        Whether to perform a deep copy.
    """

    return df.copy(
        deep=deep,
    )


def clean_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize DataFrame column names.

    - Convert to string
    - Strip whitespace
    """

    cleaned = df.copy()

    cleaned.columns = (
        cleaned.columns
        .astype(str)
        .str.strip()
    )

    return cleaned


def sort_dataframe(
    df: pd.DataFrame,
    column: str,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Sort a DataFrame if the requested
    column exists.

    If the column is missing, the original
    DataFrame is returned unchanged.
    """

    if (
        df.empty
        or column not in df.columns
    ):
        return df

    return df.sort_values(
        by=column,
        ascending=ascending,
        kind="stable",
        ignore_index=False,
    )


# =============================================================================
# Formatting
# =============================================================================

def format_percent(
    value: float,
    decimals: int = 2,
) -> str:
    """
    Format a percentage value.
    """

    return (
        f"{safe_float(value):.{decimals}f}%"
    )


def format_number(
    value: float,
    decimals: int = 2,
) -> str:
    """
    Format a numeric value with
    thousands separators.
    """

    return (
        f"{safe_float(value):,.{decimals}f}"
    )


def format_integer(
    value: int,
) -> str:
    """
    Format an integer using
    thousands separators.
    """

    return (
        f"{safe_int(value):,}"
    )


def format_datetime(
    value: datetime | None = None,
) -> str:
    """
    Format a datetime value.

    If no value is supplied,
    the current local time is used.
    """

    return (
        value or datetime.now()
    ).strftime(
        DEFAULT_DATETIME_FORMAT,
    )


# =============================================================================
# Missing Values
# =============================================================================

def fill_missing(
    df: pd.DataFrame,
    value: Any = 0,
) -> pd.DataFrame:
    """
    Replace missing values in
    a DataFrame.
    """

    return df.fillna(value)


# =============================================================================
# Statistics
# =============================================================================

def safe_mean(
    series: pd.Series,
) -> float:
    """
    Return the arithmetic mean.

    Empty or fully missing Series return 0.0.
    """

    cleaned = series.dropna()

    if cleaned.empty:
        return DEFAULT_FLOAT

    return float(cleaned.mean())


def safe_median(
    series: pd.Series,
) -> float:
    """
    Return the median.

    Empty or fully missing Series return 0.0.
    """

    cleaned = series.dropna()

    if cleaned.empty:
        return DEFAULT_FLOAT

    return float(cleaned.median())


def safe_std(
    series: pd.Series,
) -> float:
    """
    Return the standard deviation.

    Empty or fully missing Series return 0.0.
    """

    cleaned = series.dropna()

    if cleaned.empty:
        return DEFAULT_FLOAT

    return float(cleaned.std())


def safe_max(
    series: pd.Series,
) -> float:
    """
    Return the maximum value.

    Empty or fully missing Series return 0.0.
    """

    cleaned = series.dropna()

    if cleaned.empty:
        return DEFAULT_FLOAT

    return float(cleaned.max())


def safe_min(
    series: pd.Series,
) -> float:
    """
    Return the minimum value.

    Empty or fully missing Series return 0.0.
    """

    cleaned = series.dropna()

    if cleaned.empty:
        return DEFAULT_FLOAT

    return float(cleaned.min())


# =============================================================================
# Date Helpers
# =============================================================================

def today() -> str:
    """
    Return today's date as YYYY-MM-DD.
    """

    return datetime.now().strftime(
        DEFAULT_DATE_FORMAT,
    )


def timestamp() -> str:
    """
    Return the current timestamp.

    Format
    ------
    YYYYMMDD_HHMMSS
    """

    return datetime.now().strftime(
        DEFAULT_TIMESTAMP_FORMAT,
    )


# =============================================================================
# Miscellaneous
# =============================================================================

def percentage(
    numerator: float,
    denominator: float,
) -> float:
    """
    Calculate a percentage safely.

    Returns 0.0 when the denominator is zero.
    """

    denominator = safe_float(denominator)

    if denominator == 0:
        return DEFAULT_FLOAT

    return (
        safe_float(numerator)
        / denominator
    ) * 100.0


def unique_count(
    series: pd.Series,
    *,
    dropna: bool = True,
) -> int:
    """
    Return the number of unique values.

    Parameters
    ----------
    dropna
        Whether missing values should be excluded.
    """

    return int(
        series.nunique(
            dropna=dropna,
        )
    )


def is_numeric_dtype(
    series: pd.Series,
) -> bool:
    """
    Return True if the Series has
    a numeric dtype.
    """

    return bool(
        pd.api.types.is_numeric_dtype(
            series,
        )
    )


def replace_inf(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Replace positive and negative infinity
    values with NaN.

    Returns
    -------
    pandas.DataFrame
        Cleaned DataFrame.
    """

    return df.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )