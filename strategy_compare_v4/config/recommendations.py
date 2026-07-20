"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
config/recommendations.py

Purpose
-------
Centralized institutional recommendation engine.

Provides:
    • Single recommendation function
    • Batch dataframe assignment
    • Recommendation ordering

=============================================================
"""

from __future__ import annotations

import pandas as pd
from strategy_compare_v4.config.constants import (
    AVOID,
    BUY,
    COMPOSITE_SCORE,
    EDGE_SCORE,
    EFFICIENCY_SCORE,
    IMPROVE,
    RECOMMENDATION,
    REJECT,
    RELIABILITY_SCORE,
    STRONG_BUY,
    WATCH,
)
from strategy_compare_v4.config.thresholds import (
    EXCELLENT_SCORE,
    GOOD_SCORE,
    MIN_COMPOSITE_SCORE,
    MIN_EDGE_SCORE,
    MIN_EFFICIENCY_SCORE,
    MIN_RELIABILITY_SCORE,
)
from strategy_compare_v4.utils.helpers import require_columns

# ============================================================
# Recommendation Engine
# ============================================================


def get_recommendation(
    composite_score: float,
    edge_score: float,
    reliability_score: float,
    efficiency_score: float,
) -> str:
    """
    Return an institutional recommendation based on
    all institutional scores.
    """

    if (
        composite_score >= EXCELLENT_SCORE
        and edge_score >= 85
        and reliability_score >= 85
        and efficiency_score >= 85
    ):
        return STRONG_BUY

    if (
        composite_score >= GOOD_SCORE
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


# ============================================================
# Batch Recommendation
# ============================================================


def assign_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add institutional recommendations to a dataframe.
    """

    df = df.copy()

    require_columns(
        df,
        [
            COMPOSITE_SCORE,
            EDGE_SCORE,
            RELIABILITY_SCORE,
            EFFICIENCY_SCORE,
        ],
    )

    df[RECOMMENDATION] = df.apply(
        lambda row: get_recommendation(
            row[COMPOSITE_SCORE],
            row[EDGE_SCORE],
            row[RELIABILITY_SCORE],
            row[EFFICIENCY_SCORE],
        ),
        axis=1,
    )

    return df


# ============================================================
# Recommendation Priority
# ============================================================

RECOMMENDATION_PRIORITY = {
    STRONG_BUY: 1,
    BUY: 2,
    WATCH: 3,
    IMPROVE: 4,
    AVOID: 5,
    REJECT: 6,
}
