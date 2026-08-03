"""
scanner_monitor.core.formatting
===============================

Formatting utilities for the Institutional Scanner Monitor.

This module provides consistent formatting helpers for numbers,
currencies, percentages, dates, text, DataFrames, booleans,
missing values, and file sizes.

All public APIs are preserved for backward compatibility.
"""

from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Any
from typing import Final

import pandas as pd

__all__ = [
    "number",
    "integer",
    "percent",
    "currency",
    "date_string",
    "datetime_string",
    "title",
    "uppercase",
    "lowercase",
    "rename_columns",
    "dash",
    "yes_no",
    "file_size",
]

# =============================================================================
# Constants
# =============================================================================

DEFAULT_DATE_FORMAT: Final[str] = "%d %b %Y"

DEFAULT_DATETIME_FORMAT: Final[str] = "%d %b %Y %H:%M:%S"

DEFAULT_MISSING_VALUE: Final[str] = "-"

_FILE_SIZE_UNITS: Final[tuple[str, ...]] = (
    "B",
    "KB",
    "MB",
    "GB",
    "TB",
    "PB",
)

# =============================================================================
# Numbers
# =============================================================================


def number(
    value: Any,
    decimals: int = 2,
    default: str = DEFAULT_MISSING_VALUE,
) -> str:
    """
    Format a numeric value with thousands separators.

    Parameters
    ----------
    value:
        Value to format.
    decimals:
        Number of decimal places.
    default:
        Returned if formatting fails.

    Returns
    -------
    str
    """

    try:
        return f"{float(value):,.{decimals}f}"

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return default


def integer(
    value: Any,
    default: str = DEFAULT_MISSING_VALUE,
) -> str:
    """
    Format an integer with thousands separators.
    """

    try:
        return f"{int(value):,}"

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return default


# =============================================================================
# Percentage
# =============================================================================


def percent(
    value: Any,
    decimals: int = 2,
    default: str = DEFAULT_MISSING_VALUE,
) -> str:
    """
    Format a percentage value.
    """

    try:
        return f"{float(value):.{decimals}f}%"

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return default


# =============================================================================
# Currency
# =============================================================================


def currency(
    value: Any,
    symbol: str = "$",
    decimals: int = 2,
    default: str = DEFAULT_MISSING_VALUE,
) -> str:
    """
    Format a currency value.
    """

    try:
        return f"{symbol}{float(value):,.{decimals}f}"

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return default


# =============================================================================
# Dates
# =============================================================================


def date_string(
    value: datetime | date | str | None,
    fmt: str = DEFAULT_DATE_FORMAT,
) -> str:
    """
    Format a date-like value.

    Accepts datetime, date, pandas.Timestamp,
    or a string parseable by pandas.
    """

    if value is None:
        return DEFAULT_MISSING_VALUE

    if isinstance(value, str):

        try:
            value = pd.to_datetime(value)

        except Exception:
            return value

    try:
        return value.strftime(fmt)

    except AttributeError:
        return DEFAULT_MISSING_VALUE


def datetime_string(
    value: datetime | None = None,
) -> str:
    """
    Format a datetime value.

    If no value is supplied, the current
    local datetime is used.
    """

    return (value or datetime.now()).strftime(
        DEFAULT_DATETIME_FORMAT,
    )


# =============================================================================
# Text
# =============================================================================


def title(
    text: str,
) -> str:
    """
    Convert snake_case or underscored text
    into title case.
    """

    return str(text).replace(
        "_",
        " ",
    ).title()


def uppercase(
    text: str,
) -> str:
    """
    Convert text to uppercase.
    """

    return str(text).upper()


def lowercase(
    text: str,
) -> str:
    """
    Convert text to lowercase.
    """

    return str(text).lower()


# =============================================================================
# DataFrame
# =============================================================================


def rename_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return a copy of the DataFrame with
    display-friendly column names.
    """

    renamed = df.copy()

    renamed.columns = [
        title(str(column))
        for column in renamed.columns
    ]

    return renamed


# =============================================================================
# Missing Values
# =============================================================================


def dash(
    value: Any,
) -> str:
    """
    Replace missing values with '-'.
    """

    if pd.isna(value):
        return DEFAULT_MISSING_VALUE

    return str(value)


# =============================================================================
# Boolean
# =============================================================================


def yes_no(
    value: bool,
) -> str:
    """
    Convert a boolean into 'Yes' or 'No'.
    """

    return "Yes" if bool(value) else "No"


# =============================================================================
# File Size
# =============================================================================


def file_size(
    size: int | float,
) -> str:
    """
    Convert a file size in bytes into a
    human-readable representation.

    Examples
    --------
    512      -> 512.0 B
    2048     -> 2.0 KB
    5242880  -> 5.0 MB
    """

    try:
        value = max(float(size), 0.0)

    except (
        TypeError,
        ValueError,
    ):
        return DEFAULT_MISSING_VALUE

    for unit in _FILE_SIZE_UNITS:

        if value < 1024 or unit == _FILE_SIZE_UNITS[-1]:
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} PB"