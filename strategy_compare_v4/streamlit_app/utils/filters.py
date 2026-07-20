"""
filters.py
==========

Common DataFrame filtering utilities.
"""

from __future__ import annotations

import pandas as pd


def filter_by_value(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    """
    Filter rows matching a value.
    """
    if column not in df.columns:
        return df

    return df[df[column] == value]


def filter_contains(
    df: pd.DataFrame,
    column: str,
    text: str,
) -> pd.DataFrame:
    """
    Case-insensitive text search.
    """
    if column not in df.columns:
        return df

    return df[df[column].astype(str).str.contains(text, case=False, na=False)]


def top_n(
    df: pd.DataFrame,
    column: str,
    n: int = 10,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Return Top/Bottom N rows.
    """
    if column not in df.columns:
        return df

    return (
        df.sort_values(
            column,
            ascending=ascending,
        )
        .head(n)
        .reset_index(drop=True)
    )


def filter_range(
    df: pd.DataFrame,
    column: str,
    minimum=None,
    maximum=None,
) -> pd.DataFrame:
    """
    Numeric range filter.
    """

    if column not in df.columns:
        return df

    result = df.copy()

    if minimum is not None:
        result = result[result[column] >= minimum]

    if maximum is not None:
        result = result[result[column] <= maximum]

    return result.reset_index(drop=True)
