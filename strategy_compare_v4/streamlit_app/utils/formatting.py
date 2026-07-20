"""
formatting.py
=============

Formatting utilities for the Institutional Strategy Platform.

These helper functions standardize the display of:

- Numbers
- Percentages
- Currency
- Large numbers
- Dates
- DataFrames
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

# ==========================================================
# Numeric Formatting
# ==========================================================


def format_number(value: Any, decimals: int = 2, default: str = "-") -> str:
    """
    Format any numeric value.

    Example:
        1234.5678 -> 1234.57
    """

    if pd.isna(value):
        return default

    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return default


# ==========================================================
# Percentage Formatting
# ==========================================================


def format_percent(value: Any, decimals: int = 2, default: str = "-") -> str:
    """
    Format percentage values.

    Example:
        12.456 -> 12.46%
    """

    if pd.isna(value):
        return default

    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return default


# ==========================================================
# Currency Formatting
# ==========================================================


def format_currency(
    value: Any, symbol: str = "₹", decimals: int = 2, default: str = "-"
) -> str:
    """
    Format currency values.

    Example:
        1500000 -> ₹1,500,000.00
    """

    if pd.isna(value):
        return default

    try:
        return f"{symbol}{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return default


# ==========================================================
# Large Number Formatting
# ==========================================================


def format_large_number(value: Any, default: str = "-") -> str:
    """
    Convert large numbers into K/M/B notation.

    Examples

    1,250 -> 1.25K
    2,400,000 -> 2.40M
    """

    if pd.isna(value):
        return default

    try:
        value = float(value)

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"

        return f"{value:.2f}"

    except (TypeError, ValueError):
        return default


# ==========================================================
# Date Formatting
# ==========================================================


def format_date(value: Any, fmt: str = "%d-%b-%Y", default: str = "-") -> str:
    """
    Format dates consistently.
    """

    if value is None:
        return default

    try:
        if isinstance(value, datetime):
            return value.strftime(fmt)

        dt = pd.Timestamp(value)

        return dt.strftime(fmt)

    except Exception:
        return default


# ==========================================================
# DataFrame Formatting
# ==========================================================


def round_dataframe(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    """
    Round all numeric columns.
    """

    result = df.copy()

    numeric = result.select_dtypes(include="number").columns

    result[numeric] = result[numeric].round(decimals)

    return result


# ==========================================================
# Missing Value Formatting
# ==========================================================


def replace_missing(df: pd.DataFrame, value: str = "-") -> pd.DataFrame:
    """
    Replace NaN values with a display value.
    """

    return df.fillna(value)
