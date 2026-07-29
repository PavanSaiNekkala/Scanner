"""
core/formatting.py
==================

Formatting utilities for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Any

import pandas as pd

# =============================================================================
# Numbers
# =============================================================================


def number(
    value: Any,
    decimals: int = 2,
    default: str = "-",
) -> str:
    """
    Format a numeric value.
    """

    try:

        return f"{float(value):,.{decimals}f}"

    except (

        TypeError,

        ValueError,

    ):

        return default


def integer(
    value: Any,
    default: str = "-",
) -> str:
    """
    Format an integer.
    """

    try:

        return f"{int(value):,}"

    except (

        TypeError,

        ValueError,

    ):

        return default


# =============================================================================
# Percentage
# =============================================================================


def percent(
    value: Any,
    decimals: int = 2,
    default: str = "-",
) -> str:
    """
    Format a percentage.
    """

    try:

        return f"{float(value):.{decimals}f}%"

    except (

        TypeError,

        ValueError,

    ):

        return default


# =============================================================================
# Currency
# =============================================================================


def currency(
    value: Any,
    symbol: str = "$",
    decimals: int = 2,
    default: str = "-",
) -> str:
    """
    Format a currency value.
    """

    try:

        return (

            f"{symbol}"

            f"{float(value):,.{decimals}f}"

        )

    except (

        TypeError,

        ValueError,

    ):

        return default


# =============================================================================
# Dates
# =============================================================================


def date_string(
    value: datetime | date | str | None,
    fmt: str = "%d %b %Y",
) -> str:
    """
    Format a date.
    """

    if value is None:

        return "-"

    if isinstance(

        value,

        str,

    ):

        try:

            value = pd.to_datetime(

                value,

            )

        except Exception:

            return value

    return value.strftime(

        fmt,

    )


def datetime_string(
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
# Text
# =============================================================================


def title(
    text: str,
) -> str:
    """
    Title-case text.
    """

    return text.replace(

        "_",

        " ",

    ).title()


def uppercase(
    text: str,
) -> str:
    """
    Uppercase text.
    """

    return text.upper()


def lowercase(
    text: str,
) -> str:
    """
    Lowercase text.
    """

    return text.lower()


# =============================================================================
# DataFrame
# =============================================================================


def rename_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create display-friendly column names.
    """

    renamed = df.copy()

    renamed.columns = [

        title(

            column,

        )

        for column

        in renamed.columns

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

    if pd.isna(

        value,

    ):

        return "-"

    return str(

        value,

    )


# =============================================================================
# Boolean
# =============================================================================


def yes_no(
    value: bool,
) -> str:
    """
    Format booleans.
    """

    return (

        "Yes"

        if value

        else "No"

    )


# =============================================================================
# File Size
# =============================================================================


def file_size(
    size: int,
) -> str:
    """
    Human-readable file size.
    """

    units = [

        "B",

        "KB",

        "MB",

        "GB",

        "TB",

    ]

    value = float(

        size,

    )

    for unit in units:

        if value < 1024:

            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} PB"