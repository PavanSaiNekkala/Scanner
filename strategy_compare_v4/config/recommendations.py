"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
config/recommendations.py

Purpose
-------
Centralized institutional recommendation engine.

Provides
--------
• Single recommendation function
• Batch dataframe assignment
• Recommendation ordering
• Portfolio eligibility

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
    AVOID_SCORE,
    BUY_SCORE,
    EXCELLENT_SCORE,
    GOOD_SCORE,
    IMPROVE_SCORE,
    MIN_COMPOSITE_SCORE,
    MIN_EDGE_SCORE,
    MIN_EFFICIENCY_SCORE,
    MIN_RELIABILITY_SCORE,
    STRONG_BUY_SCORE,
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
    Return institutional recommendation.
    """

    if (
        composite_score >= EXCELLENT_SCORE
        and edge_score >= STRONG_BUY_SCORE
        and reliability_score >= STRONG_BUY_SCORE
        and efficiency_score >= STRONG_BUY_SCORE
    ):
        return STRONG_BUY

    if (
        composite_score >= GOOD_SCORE
        and edge_score >= BUY_SCORE
        and reliability_score >= BUY_SCORE
        and efficiency_score >= BUY_SCORE
    ):
        return BUY

    if (
        composite_score >= MIN_COMPOSITE_SCORE
        and edge_score >= MIN_EDGE_SCORE
        and reliability_score >= MIN_RELIABILITY_SCORE
        and efficiency_score >= MIN_EFFICIENCY_SCORE
    ):
        return WATCH

    if composite_score >= IMPROVE_SCORE:
        return IMPROVE

    if composite_score >= AVOID_SCORE:
        return AVOID

    return REJECT


# ============================================================
# Batch Recommendation
# ============================================================


def assign_recommendations(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign recommendations to an entire DataFrame.
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

# ============================================================
# Portfolio Eligibility
# ============================================================

PORTFOLIO_ELIGIBILITY = {
    STRONG_BUY: True,
    BUY: True,
    WATCH: True,
    IMPROVE: False,
    AVOID: False,
    REJECT: False,
}

# ============================================================
# Recommendation Colors
# ============================================================

RECOMMENDATION_COLORS = {
    STRONG_BUY: "#008000",  # Green
    BUY: "#2E8B57",  # Sea Green
    WATCH: "#FFD700",  # Gold
    IMPROVE: "#FFA500",  # Orange
    AVOID: "#FF6347",  # Tomato
    REJECT: "#DC143C",  # Crimson
}

# ============================================================
# Recommendation Descriptions
# ============================================================

RECOMMENDATION_DESCRIPTIONS = {
    STRONG_BUY: (
        "Exceptional institutional-quality strategy with "
        "strong edge, reliability and efficiency."
    ),
    BUY: ("High-quality strategy suitable for institutional portfolio allocation."),
    WATCH: ("Acceptable strategy that should continue to be monitored."),
    IMPROVE: ("Shows potential but requires further optimization."),
    AVOID: ("Below preferred institutional standards."),
    REJECT: ("Does not satisfy minimum institutional criteria."),
}

# ============================================================
# Institutional Grades
# ============================================================

INSTITUTIONAL_GRADE = {
    STRONG_BUY: "A+",
    BUY: "A",
    WATCH: "B",
    IMPROVE: "C",
    AVOID: "D",
    REJECT: "F",
}

# ============================================================
# Recommendation Order
# ============================================================

RECOMMENDATION_ORDER = [
    STRONG_BUY,
    BUY,
    WATCH,
    IMPROVE,
    AVOID,
    REJECT,
]

# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "get_recommendation",
    "assign_recommendations",
    "RECOMMENDATION_PRIORITY",
    "PORTFOLIO_ELIGIBILITY",
    "RECOMMENDATION_COLORS",
    "RECOMMENDATION_DESCRIPTIONS",
    "INSTITUTIONAL_GRADE",
    "RECOMMENDATION_ORDER",
]
