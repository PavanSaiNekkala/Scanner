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
# Constants
# ============================================================

EPSILON = 1e-12

NORMALIZED_MIN = 0.0

NORMALIZED_MAX = 100.0

DEFAULT_ROUNDING = 2

DEFAULT_WINSOR_LOWER = 0.05

DEFAULT_WINSOR_UPPER = 0.95


# ============================================================
# Numeric Conversion
# ============================================================


def numeric(
    series: pd.Series | Any,
) -> pd.Series:
    """
    Convert values to numeric.

    Invalid values become NaN.
    """

    return pd.to_numeric(
        series,
        errors="coerce",
    )


# ============================================================
# Safe Division
# ============================================================


def safe_divide(
    a,
    b,
):
    """
    Safe element-wise division.

    Supports

    • scalar
    • ndarray
    • Series
    • DataFrame

    Returns zero whenever the
    denominator is zero or NaN.
    """

    if isinstance(
        a,
        (
            pd.Series,
            pd.DataFrame,
        ),
    ):
        denominator = (
            b.replace(
                0,
                np.nan,
            )
            if isinstance(
                b,
                (
                    pd.Series,
                    pd.DataFrame,
                ),
            )
            else b
        )

        result = a.divide(
            denominator,
        )

        return result.fillna(
            0,
        )

    a = np.asarray(
        a,
        dtype=float,
    )

    b = np.asarray(
        b,
        dtype=float,
    )

    return np.divide(
        a,
        b,
        out=np.zeros_like(
            a,
            dtype=float,
        ),
        where=np.abs(
            b,
        )
        > EPSILON,
    )


# ============================================================
# Min-Max Normalization
# ============================================================


def normalize(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize values between
    0 and 100.
    """

    series = numeric(
        series,
    )

    minimum = series.min()

    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(
            NORMALIZED_MIN,
            index=series.index,
        )

    if (
        abs(
            maximum - minimum,
        )
        < EPSILON
    ):
        return pd.Series(
            NORMALIZED_MAX,
            index=series.index,
        )

    return ((series - minimum) / (maximum - minimum)) * NORMALIZED_MAX


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

    return NORMALIZED_MAX - normalize(
        series,
    )


# ============================================================
# Percentile Rank
# ============================================================


def percentile_rank(
    series: pd.Series,
) -> pd.Series:
    """
    Percentile ranking
    between 0 and 100.
    """

    return (
        numeric(
            series,
        )
        .rank(
            pct=True,
        )
        .mul(
            NORMALIZED_MAX,
        )
    )


# ============================================================
# Z Score
# ============================================================


def z_score(
    series: pd.Series,
) -> pd.Series:
    """
    Standard score.
    """

    series = numeric(
        series,
    )

    std = series.std()

    if pd.isna(std) or abs(std) < EPSILON:
        return pd.Series(
            0.0,
            index=series.index,
        )

    return (series - series.mean()) / std


# ============================================================
# Coefficient of Variation
# ============================================================


def coefficient_of_variation(
    series: pd.Series,
) -> float:
    """
    Coefficient of variation.
    """

    series = numeric(
        series,
    )

    mean = series.mean()

    if pd.isna(mean) or abs(mean) < EPSILON:
        return np.nan

    return float(
        series.std() / mean,
    )


# ============================================================
# Winsorization
# ============================================================


def winsorize(
    series: pd.Series,
    lower: float = DEFAULT_WINSOR_LOWER,
    upper: float = DEFAULT_WINSOR_UPPER,
) -> pd.Series:
    """
    Winsorize a Series.
    """

    if not (0 <= lower < upper <= 1):
        raise ValueError("Invalid winsorization limits.")

    lower_bound = series.quantile(
        lower,
    )

    upper_bound = series.quantile(
        upper,
    )

    return series.clip(
        lower=lower_bound,
        upper=upper_bound,
    )


# ============================================================
# Clamp
# ============================================================


def clamp(
    series: pd.Series,
    minimum: float = NORMALIZED_MIN,
    maximum: float = NORMALIZED_MAX,
) -> pd.Series:
    """
    Restrict values to a
    specified range.
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

    Raises
    ------
    ValueError
        If lengths differ.
    """

    values = np.asarray(
        values,
        dtype=float,
    )

    weights = np.asarray(
        weights,
        dtype=float,
    )

    if len(values) != len(weights):
        raise ValueError("Values and weights must have the same length.")

    total = weights.sum()

    if abs(total) < EPSILON:
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
    Compound Annual
    Growth Rate.
    """

    if beginning <= 0 or ending <= 0 or years <= 0:
        return np.nan

    return (ending / beginning) ** (1 / years) - 1


# ============================================================
# Safe Percentage
# ============================================================


def safe_percentage(
    part,
    total,
):
    """
    Safely compute percentage.
    """

    return (
        safe_divide(
            part,
            total,
        )
        * 100
    )


# ============================================================
# Median Absolute Deviation
# ============================================================


def median_absolute_deviation(
    series: pd.Series,
) -> float:
    """
    Median Absolute
    Deviation (MAD).
    """

    series = numeric(
        series,
    )

    median = series.median()

    return float((series - median).abs().median())


# ============================================================
# Interquartile Range
# ============================================================


def interquartile_range(
    series: pd.Series,
) -> float:
    """
    Interquartile Range.
    """

    series = numeric(
        series,
    )

    return float(
        series.quantile(
            0.75,
        )
        - series.quantile(
            0.25,
        )
    )


# ============================================================
# Outlier Mask
# ============================================================


def outlier_mask(
    series: pd.Series,
) -> pd.Series:
    """
    Return an IQR-based
    outlier mask.
    """

    series = numeric(
        series,
    )

    q1 = series.quantile(
        0.25,
    )

    q3 = series.quantile(
        0.75,
    )

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr

    upper = q3 + 1.5 * iqr

    return (series < lower) | (series > upper)


# ============================================================
# Round Utilities
# ============================================================


def round_dataframe(
    data: pd.DataFrame | pd.Series,
    decimals: int = DEFAULT_ROUNDING,
):
    """
    Round numeric values in a
    DataFrame or Series.
    """

    if isinstance(
        data,
        pd.Series,
    ):
        return data.round(
            decimals,
        )

    data = data.copy()

    numeric_columns = data.select_dtypes(
        include="number",
    ).columns

    data[numeric_columns] = data[numeric_columns].round(
        decimals,
    )

    return data


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "numeric",
    "safe_divide",
    "normalize",
    "reverse_normalize",
    "percentile_rank",
    "z_score",
    "coefficient_of_variation",
    "winsorize",
    "clamp",
    "weighted_average",
    "cagr",
    "safe_percentage",
    "median_absolute_deviation",
    "interquartile_range",
    "outlier_mask",
    "round_dataframe",
]
