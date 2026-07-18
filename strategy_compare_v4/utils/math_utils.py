"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
utils/math_utils.py

Purpose
-------
Mathematical helper functions shared across the
Institutional Strategy Comparison Platform.

Provides
--------
• Numeric conversion
• Safe arithmetic
• Normalization
• Statistical utilities
• Weighted calculations
• Financial calculations

=============================================================
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


# ============================================================
# Numeric Conversion
# ============================================================

def numeric(
    series: pd.Series | Any,
) -> pd.Series:
    """
    Convert a Series to numeric values.
    Invalid entries become NaN.
    """

    return pd.to_numeric(
        series,
        errors="coerce",
    )


# ============================================================
# Safe Division
# ============================================================

def safe_divide(
    numerator: Any,
    denominator: Any,
    default: float = 0.0,
) -> np.ndarray:
    """
    Divide safely while avoiding divide-by-zero.
    """

    numerator = np.asarray(numerator, dtype=float)

    denominator = np.asarray(
        denominator,
        dtype=float,
    )

    return np.where(
        denominator != 0,
        numerator / denominator,
        default,
    )


# ============================================================
# Min-Max Normalization
# ============================================================

def normalize(
    series: pd.Series,
) -> pd.Series:
    """
    Scale values between 0 and 100.
    """

    series = numeric(series)

    minimum = series.min()

    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(
            0.0,
            index=series.index,
        )

    if maximum == minimum:
        return pd.Series(
            100.0,
            index=series.index,
        )

    return (
        (series - minimum)
        /
        (maximum - minimum)
        * 100
    )


# ============================================================
# Reverse Normalization
# ============================================================

def reverse_normalize(
    series: pd.Series,
) -> pd.Series:
    """
    Reverse normalization where
    lower values are better.
    """

    return 100 - normalize(series)


# ============================================================
# Percentile Rank
# ============================================================

def percentile_rank(
    series: pd.Series,
) -> pd.Series:
    """
    Percentile ranking (0-100).
    """

    return (
        numeric(series)
        .rank(pct=True)
        * 100
    )


# ============================================================
# Z-Score
# ============================================================

def z_score(
    series: pd.Series,
) -> pd.Series:
    """
    Compute standard score.
    """

    series = numeric(series)

    std = series.std()

    if std == 0 or pd.isna(std):
        return pd.Series(
            0.0,
            index=series.index,
        )

    return (
        series - series.mean()
    ) / std


# ============================================================
# Coefficient of Variation
# ============================================================

def coefficient_of_variation(
    series: pd.Series,
) -> float:
    """
    Compute coefficient of variation.
    """

    series = numeric(series)

    mean = series.mean()

    if mean == 0 or pd.isna(mean):
        return np.nan

    return float(
        series.std() / mean
    )


# ============================================================
# Winsorization
# ============================================================

def winsorize(
    series: pd.Series,
    lower: float = 0.05,
    upper: float = 0.95,
) -> pd.Series:
    """
    Cap extreme outliers.
    """

    lower_bound = series.quantile(lower)

    upper_bound = series.quantile(upper)

    return series.clip(
        lower=lower_bound,
        upper=upper_bound,
    )


# ============================================================
# Clamp
# ============================================================

def clamp(
    series: pd.Series,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> pd.Series:
    """
    Restrict values to a range.
    """

    return series.clip(
        lower=minimum,
        upper=maximum,
    )


# ============================================================
# Weighted Average
# ============================================================

def weighted_average(
    values: Any,
    weights: Any,
) -> float:
    """
    Compute weighted average.
    """

    values = np.asarray(values, dtype=float)

    weights = np.asarray(
        weights,
        dtype=float,
    )

    total = weights.sum()

    if total == 0:
        return 0.0

    return float(
        np.average(
            values,
            weights=weights,
        )
    )


# ============================================================
# CAGR
# ============================================================

def cagr(
    beginning: float,
    ending: float,
    years: float,
) -> float:
    """
    Compute Compound Annual Growth Rate.
    """

    if (
        beginning <= 0
        or ending <= 0
        or years <= 0
    ):
        return np.nan

    return (
        (ending / beginning)
        ** (1 / years)
        - 1
    )


# ============================================================
# Round DataFrame
# ============================================================

def round_dataframe(
    df: pd.DataFrame,
    decimals: int = 2,
) -> pd.DataFrame:
    """
    Round numeric columns.
    """

    df = df.copy()

    numeric_columns = df.select_dtypes(
        include="number",
    ).columns

    df[numeric_columns] = (
        df[numeric_columns]
        .round(decimals)
    )

    return df