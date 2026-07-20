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

Guidelines
----------
• Composite Score
• Edge Score
• Reliability Score
• Efficiency Score
• Portfolio Allocation
• Leaderboard Ranking
• Robustness Analysis
• Correlation Analysis

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
# Composite Score
# ============================================================

COMPOSITE_WEIGHTS = {
    "Edge Score": 0.20,
    "Reliability Score": 0.20,
    "Risk Score": 0.15,
    "Opportunity Score": 0.15,
    "Efficiency Score": 0.15,
    "Return Score": 0.15,
}

# ============================================================
# Edge Score
# ============================================================

EDGE_WEIGHTS = {
    EXPECTANCY: 0.35,
    PROFIT_FACTOR: 0.30,
    REWARD_RISK: 0.20,
    PROFIT_VELOCITY: 0.15,
}

# ============================================================
# Reliability Score
# ============================================================

RELIABILITY_WEIGHTS = {
    TRADES_PER_YEAR: 0.30,
    WINNING_EXIT: 0.25,
    LOSING_EXIT: 0.20,
    SIGNAL_QUALITY: 0.25,
}

# ============================================================
# Efficiency Score
# ============================================================

EFFICIENCY_WEIGHTS = {
    HOLDING_EFFICIENCY: 0.40,
    PROFIT_VELOCITY: 0.30,
    EXPECTANCY: 0.30,
}

# ============================================================
# Portfolio Allocation
# ============================================================

PORTFOLIO_WEIGHTS = {
    COMPOSITE_SCORE: 0.60,
    RELIABILITY_SCORE: 0.20,
    EDGE_SCORE: 0.20,
}

# ============================================================
# Leaderboard Ranking
# ============================================================

LEADERBOARD_WEIGHTS = {
    COMPOSITE_SCORE: 0.50,
    EDGE_SCORE: 0.20,
    RELIABILITY_SCORE: 0.15,
    EFFICIENCY_SCORE: 0.15,
}

# ============================================================
# Robustness Analysis
# ============================================================

ROBUSTNESS_WEIGHTS = {
    "Composite Consistency": 0.35,
    "Expectancy Stability": 0.25,
    "Profit Factor Stability": 0.20,
    "Reward Risk Stability": 0.20,
}

# ============================================================
# Correlation Analysis
# ============================================================

CORRELATION_WEIGHTS = {
    "Pearson": 0.50,
    "Spearman": 0.30,
    "Kendall": 0.20,
}
