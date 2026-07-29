"""
core/helpers.py
===============

General helper utilities for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

# =============================================================================
# Column Helpers
# =============================================================================

def first_existing(
    df: pd.DataFrame,
    *columns: str,
) -> str | None:
    """
    Return first matching column
    (case-insensitive).
    """

    lookup = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for column in columns:

        key = str(column).strip().lower()

        if key in lookup:
            return lookup[key]

    return None


def existing_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> list[str]:
    """
    Return all columns that exist.
    """

    return [

        column

        for column in columns

        if column in df.columns

    ]


# =============================================================================
# Numeric Helpers
# =============================================================================


def numeric_series(
    df: pd.DataFrame,
    column: str | None,
) -> pd.Series:
    """
    Safely convert a column to numeric.
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

        .fillna(

            0.0,

        )

    )


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert to float.
    """

    try:

        return float(value)

    except (

        TypeError,

        ValueError,

    ):

        return default


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert to integer.
    """

    try:

        return int(value)

    except (

        TypeError,

        ValueError,

    ):

        return default


# =============================================================================
# DataFrame Helpers
# =============================================================================


def copy_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return a safe copy.
    """

    return df.copy()


def clean_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize column names.
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
    Sort by column if it exists.
    """

    if column not in df.columns:

        return df

    return df.sort_values(

        column,

        ascending=ascending,

    )


# =============================================================================
# Formatting
# =============================================================================


def format_percent(
    value: float,
    decimals: int = 2,
) -> str:
    """
    Format percentage.
    """

    return f"{safe_float(value):.{decimals}f}%"


def format_number(
    value: float,
    decimals: int = 2,
) -> str:
    """
    Format numeric value.
    """

    return f"{safe_float(value):,.{decimals}f}"


def format_integer(
    value: int,
) -> str:
    """
    Format integer.
    """

    return f"{safe_int(value):,}"


def format_datetime(
    value: datetime | None = None,
) -> str:
    """
    Format datetime.
    """

    value = value or datetime.now()

    return value.strftime(

        "%d %b %Y %H:%M:%S",

    )


# =============================================================================
# Missing Values
# =============================================================================


def fill_missing(
    df: pd.DataFrame,
    value: Any = 0,
) -> pd.DataFrame:
    """
    Fill missing values.
    """

    return df.fillna(

        value,

    )


# =============================================================================
# Statistics
# =============================================================================


def safe_mean(
    series: pd.Series,
) -> float:
    """
    Mean ignoring empty series.
    """

    if series.empty:

        return 0.0

    return float(

        series.mean()

    )


def safe_median(
    series: pd.Series,
) -> float:
    """
    Median ignoring empty series.
    """

    if series.empty:

        return 0.0

    return float(

        series.median()

    )


def safe_std(
    series: pd.Series,
) -> float:
    """
    Standard deviation.
    """

    if series.empty:

        return 0.0

    return float(

        series.std()

    )


def safe_max(
    series: pd.Series,
) -> float:
    """
    Maximum value.
    """

    if series.empty:

        return 0.0

    return float(

        series.max()

    )


def safe_min(
    series: pd.Series,
) -> float:
    """
    Minimum value.
    """

    if series.empty:

        return 0.0

    return float(

        series.min()

    )


# =============================================================================
# Date Helpers
# =============================================================================


def today() -> str:
    """
    Return today's date.
    """

    return datetime.now().strftime(

        "%Y-%m-%d",

    )


def timestamp() -> str:
    """
    Current timestamp.
    """

    return datetime.now().strftime(

        "%Y%m%d_%H%M%S",

    )


# =============================================================================
# Miscellaneous
# =============================================================================


def percentage(
    numerator: float,
    denominator: float,
) -> float:
    """
    Safe percentage calculation.
    """

    if denominator == 0:

        return 0.0

    return (

        numerator

        / denominator

    ) * 100


def unique_count(
    series: pd.Series,
) -> int:
    """
    Count unique values.
    """

    return int(

        series.nunique()

    )


def is_numeric_dtype(
    series: pd.Series,
) -> bool:
    """
    Check numeric dtype.
    """

    return pd.api.types.is_numeric_dtype(

        series,

    )


def replace_inf(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Replace infinite values.
    """

    return df.replace(

        [

            np.inf,

            -np.inf,

        ],

        np.nan,

    )