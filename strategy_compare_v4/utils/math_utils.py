"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    utils/math_utils.py

Purpose:
    Mathematical helper functions used throughout
    the institutional strategy comparison platform.

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd


###############################################################################
# Numeric Conversion
###############################################################################

def numeric(series):
    """
    Convert series to numeric.
    """

    return pd.to_numeric(

        series,

        errors="coerce"

    )


###############################################################################
# Safe Division
###############################################################################

def safe_divide(

    numerator,

    denominator,

    default=0

):
    """
    Safe division avoiding divide-by-zero.
    """

    numerator = np.asarray(numerator)

    denominator = np.asarray(denominator)

    return np.where(

        denominator != 0,

        numerator / denominator,

        default

    )


###############################################################################
# Min-Max Normalization
###############################################################################

def normalize(

    series

):
    """
    Normalize values to 0-100.
    """

    series = numeric(series)

    minimum = series.min()

    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):

        return pd.Series(

            0,

            index=series.index

        )

    if maximum == minimum:

        return pd.Series(

            100,

            index=series.index

        )

    return (

        (series - minimum)

        /

        (maximum - minimum)

        *

        100

    )


###############################################################################
# Reverse Normalization
###############################################################################

def reverse_normalize(

    series

):
    """
    Normalize where lower is better.
    """

    return 100 - normalize(series)


###############################################################################
# Percentile Rank
###############################################################################

def percentile_rank(

    series

):
    """
    Percentile ranking (0-100).
    """

    return (

        numeric(series)

        .rank(

            pct=True

        )

        * 100

    )


###############################################################################
# Z-Score
###############################################################################

def z_score(

    series

):
    """
    Standard score.
    """

    series = numeric(series)

    std = series.std()

    if std == 0:

        return pd.Series(

            0,

            index=series.index

        )

    return (

        series - series.mean()

    ) / std


###############################################################################
# Coefficient of Variation
###############################################################################

def coefficient_of_variation(

    series

):
    """
    Coefficient of variation.
    """

    series = numeric(series)

    mean = series.mean()

    if mean == 0:

        return np.nan

    return (

        series.std()

        /

        mean

    )


###############################################################################
# Winsorize
###############################################################################

def winsorize(

    series,

    lower=0.05,

    upper=0.95

):
    """
    Cap outliers.
    """

    lower_bound = series.quantile(lower)

    upper_bound = series.quantile(upper)

    return series.clip(

        lower_bound,

        upper_bound

    )


###############################################################################
# Clamp
###############################################################################

def clamp(

    series,

    minimum=0,

    maximum=100

):
    """
    Clamp values to range.
    """

    return series.clip(

        lower=minimum,

        upper=maximum

    )


###############################################################################
# Weighted Average
###############################################################################

def weighted_average(

    values,

    weights

):
    """
    Compute weighted average.
    """

    values = np.asarray(values)

    weights = np.asarray(weights)

    total = weights.sum()

    if total == 0:

        return 0

    return np.average(

        values,

        weights=weights

    )


###############################################################################
# CAGR
###############################################################################

def cagr(

    beginning,

    ending,

    years

):
    """
    Compound Annual Growth Rate.
    """

    if (

        beginning <= 0

        or

        ending <= 0

        or

        years <= 0

    ):

        return np.nan

    return (

        (ending / beginning)

        ** (1 / years)

        - 1

    )


###############################################################################
# Round DataFrame
###############################################################################

def round_dataframe(

    df,

    decimals=2

):
    """
    Round numeric columns.
    """

    numeric_cols = df.select_dtypes(

        include="number"

    ).columns

    df = df.copy()

    df[numeric_cols] = (

        df[numeric_cols]

        .round(decimals)

    )

    return df