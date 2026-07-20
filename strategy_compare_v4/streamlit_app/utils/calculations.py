"""
calculations.py
===============

Common calculation utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(
    numerator,
    denominator,
    default=0,
):
    """
    Safe division.
    """

    return np.where(
        denominator != 0,
        numerator / denominator,
        default,
    )


def percentage(
    value,
    total,
):
    """
    Calculate percentage.
    """

    if total == 0:
        return 0

    return (value / total) * 100


def weighted_average(
    values,
    weights,
):
    """
    Weighted average.
    """

    values = np.asarray(values)
    weights = np.asarray(weights)

    if weights.sum() == 0:
        return 0

    return np.average(
        values,
        weights=weights,
    )


def z_score(
    series: pd.Series,
) -> pd.Series:
    """
    Standardize values.
    """

    std = series.std()

    if std == 0:
        return pd.Series(
            0,
            index=series.index,
        )

    return (series - series.mean()) / std


def normalize(
    series: pd.Series,
) -> pd.Series:
    """
    Min-Max normalization.
    """

    minimum = series.min()
    maximum = series.max()

    if minimum == maximum:
        return pd.Series(
            1,
            index=series.index,
        )

    return (series - minimum) / (maximum - minimum)
