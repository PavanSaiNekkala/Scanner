"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    portfolio/allocation.py

Purpose:
    Portfolio allocation algorithms.

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.thresholds import (
    MAX_POSITION_WEIGHT,
    MIN_POSITION_WEIGHT
)


###############################################################################
# Equal Weight Allocation
###############################################################################

def equal_weight(df):
    """
    Allocate equal weights.
    """

    df = df.copy()

    n = len(df)

    if n == 0:

        df["Weight"] = []

        return df

    df["Weight"] = round(

        100 / n,

        2

    )

    return df


###############################################################################
# Composite Score Allocation
###############################################################################

def score_weight(df):
    """
    Allocate using Composite Score.
    """

    df = df.copy()

    scores = df["Composite Score"].clip(lower=0)

    total = scores.sum()

    if total == 0:

        return equal_weight(df)

    df["Weight"] = (

        scores

        /

        total

        *

        100

    )

    return df


###############################################################################
# Edge Score Allocation
###############################################################################

def edge_weight(df):
    """
    Allocate using Edge Score.
    """

    df = df.copy()

    scores = df["Edge Score"].clip(lower=0)

    total = scores.sum()

    if total == 0:

        return equal_weight(df)

    df["Weight"] = (

        scores

        /

        total

        *

        100

    )

    return df


###############################################################################
# Reliability Allocation
###############################################################################

def reliability_weight(df):
    """
    Allocate using Reliability Score.
    """

    df = df.copy()

    scores = df["Reliability Score"].clip(lower=0)

    total = scores.sum()

    if total == 0:

        return equal_weight(df)

    df["Weight"] = (

        scores

        /

        total

        *

        100

    )

    return df


###############################################################################
# Composite + Reliability Allocation
###############################################################################

def blended_weight(
    df,
    composite_weight=0.60,
    reliability_weighting=0.40
):
    """
    Allocate using weighted blend.
    """

    df = df.copy()

    score = (

        composite_weight

        * df["Composite Score"]

        +

        reliability_weighting

        * df["Reliability Score"]

    )

    total = score.sum()

    if total == 0:

        return equal_weight(df)

    df["Weight"] = (

        score

        /

        total

        *

        100

    )

    return df


###############################################################################
# Apply Position Limits
###############################################################################

def apply_position_limits(df):
    """
    Apply min/max limits and normalize.
    """

    df = df.copy()

    df["Weight"] = df["Weight"].clip(

        lower=MIN_POSITION_WEIGHT,

        upper=MAX_POSITION_WEIGHT

    )

    total = df["Weight"].sum()

    if total > 0:

        df["Weight"] = (

            df["Weight"]

            /

            total

            *

            100

        )

    return df


###############################################################################
# Round Allocation
###############################################################################

def finalize_weights(df):
    """
    Round weights.
    """

    df = df.copy()

    df["Weight"] = df["Weight"].round(2)

    difference = round(

        100 - df["Weight"].sum(),

        2

    )

    if len(df):

        df.loc[

            df["Weight"].idxmax(),

            "Weight"

        ] += difference

    return df


###############################################################################
# Main Allocation Function
###############################################################################

def allocate_portfolio(
    df,
    method="composite"
):
    """
    Portfolio allocation dispatcher.
    """

    method = method.lower()

    if method == "equal":

        df = equal_weight(df)

    elif method == "edge":

        df = edge_weight(df)

    elif method == "reliability":

        df = reliability_weight(df)

    elif method == "blend":

        df = blended_weight(df)

    else:

        df = score_weight(df)

    df = apply_position_limits(df)

    df = finalize_weights(df)

    return df