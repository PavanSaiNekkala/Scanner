"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
config/weights.py

Purpose
-------
Centralized scoring weights used throughout the
Institutional Strategy Comparison Platform.

=============================================================
"""

from __future__ import annotations

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    EDGE_SCORE,
    EFFICIENCY_SCORE,
    EXPECTANCY,
    HOLDING_EFFICIENCY,
    LOSING_EXIT,
    PROFIT_FACTOR,
    PROFIT_VELOCITY,
    RELIABILITY_SCORE,
    REWARD_RISK,
    SIGNAL_QUALITY,
    TRADES_PER_YEAR,
    WINNING_EXIT,
)


# ============================================================
# Validation
# ============================================================


def validate_weights(
    weights: dict[str, float],
    tolerance: float = 1e-9,
) -> dict[str, float]:
    """
    Validate that weight values sum to 1.0.
    """

    total = sum(
        weights.values()
    )

    if abs(total - 1.0) > tolerance:

        raise ValueError(
            f"Weights must sum to 1.0 (current={total:.4f})"
        )

    return weights


# ============================================================
# Institutional Composite Score
# ============================================================

COMPOSITE_WEIGHTS = validate_weights(
    {
        "Edge Score": 0.20,
        "Reliability Score": 0.20,
        "Risk Score": 0.20,
        "Efficiency Score": 0.10,
        "Opportunity Score": 0.10,
        "Consistency Score": 0.10,
        "Validation Score": 0.10,
    }
)


# ============================================================
# Edge Score
# ============================================================

EDGE_WEIGHTS = validate_weights(
    {
        EXPECTANCY: 0.35,
        PROFIT_FACTOR: 0.30,
        REWARD_RISK: 0.20,
        PROFIT_VELOCITY: 0.15,
    }
)


# ============================================================
# Reliability Score
# ============================================================

RELIABILITY_WEIGHTS = validate_weights(
    {
        TRADES_PER_YEAR: 0.25,
        WINNING_EXIT: 0.20,
        LOSING_EXIT: 0.15,
        SIGNAL_QUALITY: 0.20,
        "Consistency Score": 0.20,
    }
)


# ============================================================
# Efficiency Score
# ============================================================

EFFICIENCY_WEIGHTS = validate_weights(
    {
        HOLDING_EFFICIENCY: 0.40,
        PROFIT_VELOCITY: 0.30,
        EXPECTANCY: 0.30,
    }
)


# ============================================================
# Portfolio Allocation
# ============================================================

PORTFOLIO_WEIGHTS = validate_weights(
    {
        COMPOSITE_SCORE: 0.40,
        RELIABILITY_SCORE: 0.20,
        EDGE_SCORE: 0.15,
        "Risk Score": 0.15,
        "Consistency Score": 0.10,
    }
)


# ============================================================
# Leaderboard Ranking
# ============================================================

LEADERBOARD_WEIGHTS = validate_weights(
    {
        COMPOSITE_SCORE: 0.40,
        EDGE_SCORE: 0.20,
        RELIABILITY_SCORE: 0.15,
        "Risk Score": 0.15,
        EFFICIENCY_SCORE: 0.10,
    }
)


# ============================================================
# Robustness Analysis
# ============================================================

ROBUSTNESS_WEIGHTS = validate_weights(
    {
        "Composite Consistency": 0.30,
        "Expectancy Stability": 0.20,
        "Profit Factor Stability": 0.20,
        "Reward Risk Stability": 0.15,
        "Validation Stability": 0.15,
    }
)


# ============================================================
# Correlation Analysis
# ============================================================

CORRELATION_WEIGHTS = validate_weights(
    {
        "Pearson": 0.50,
        "Spearman": 0.30,
        "Kendall": 0.20,
    }
)


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "validate_weights",
    "COMPOSITE_WEIGHTS",
    "EDGE_WEIGHTS",
    "RELIABILITY_WEIGHTS",
    "EFFICIENCY_WEIGHTS",
    "PORTFOLIO_WEIGHTS",
    "LEADERBOARD_WEIGHTS",
    "ROBUSTNESS_WEIGHTS",
    "CORRELATION_WEIGHTS",
]