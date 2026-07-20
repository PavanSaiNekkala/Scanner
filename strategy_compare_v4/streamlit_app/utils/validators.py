"""
validators.py
=============

Validation utilities.
"""

from __future__ import annotations

import pandas as pd


def validate_columns(
    df: pd.DataFrame,
    required: list[str],
) -> None:
    """
    Raise an error if required columns are missing.
    """

    missing = sorted(set(required) - set(df.columns))

    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")


def validate_sheet(
    workbook,
    sheet: str,
) -> None:
    """
    Validate worksheet exists.
    """

    if sheet not in workbook.sheet_names:
        raise ValueError(f"Worksheet '{sheet}' not found.")


def validate_dataframe(
    df: pd.DataFrame,
) -> None:
    """
    Ensure DataFrame is not empty.
    """

    if df is None or df.empty:
        raise ValueError("DataFrame is empty.")
