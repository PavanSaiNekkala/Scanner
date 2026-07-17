"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    config/recommendations.py

Purpose:
    Centralized recommendation engine.

=============================================================
"""

from __future__ import annotations

from config.thresholds import (
    MIN_COMPOSITE_SCORE,
    MIN_EDGE_SCORE,
    MIN_RELIABILITY_SCORE,
    MIN_EFFICIENCY_SCORE
)


###############################################################################
# Recommendation Labels
###############################################################################

STRONG_BUY = "Strong Buy"

BUY = "Buy"

WATCH = "Watch"

IMPROVE = "Improve"

AVOID = "Avoid"

REJECT = "Reject"


###############################################################################
# Recommendation Function
###############################################################################

def get_recommendation(

    composite_score,

    edge_score,

    reliability_score,

    efficiency_score

):
    """
    Return institutional recommendation.

    Parameters
    ----------
    composite_score : float

    edge_score : float

    reliability_score : float

    efficiency_score : float

    Returns
    -------
    str
    """

    if (

        composite_score >= 90

        and edge_score >= 85

        and reliability_score >= 85

        and efficiency_score >= 85

    ):

        return STRONG_BUY

    if (

        composite_score >= 80

        and edge_score >= 75

        and reliability_score >= 75

        and efficiency_score >= 75

    ):

        return BUY

    if (

        composite_score >= MIN_COMPOSITE_SCORE

        and edge_score >= MIN_EDGE_SCORE

        and reliability_score >= MIN_RELIABILITY_SCORE

        and efficiency_score >= MIN_EFFICIENCY_SCORE

    ):

        return WATCH

    if composite_score >= 45:

        return IMPROVE

    if composite_score >= 30:

        return AVOID

    return REJECT


###############################################################################
# Batch Recommendation
###############################################################################

def assign_recommendations(df):
    """
    Add Recommendation column to dataframe.
    """

    df = df.copy()

    df["Recommendation"] = df.apply(

        lambda row: get_recommendation(

            row["Composite Score"],

            row["Edge Score"],

            row["Reliability Score"],

            row["Efficiency Score"]

        ),

        axis=1

    )

    return df


###############################################################################
# Recommendation Priority
###############################################################################

RECOMMENDATION_PRIORITY = {

    STRONG_BUY: 1,

    BUY: 2,

    WATCH: 3,

    IMPROVE: 4,

    AVOID: 5,

    REJECT: 6

}