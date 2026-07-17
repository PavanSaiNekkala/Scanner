"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    config/weights.py

Purpose:
    Centralized scoring weights used across the
    institutional ranking engine.

=============================================================
"""

###############################################################################
# Composite Score
###############################################################################

COMPOSITE_WEIGHTS = {

    "Edge Score": 0.30,

    "Reliability Score": 0.25,

    "Efficiency Score": 0.20,

    "Profit Velocity": 0.10,

    "Signal Quality": 0.05,

    "Holding Efficiency": 0.05,

    "Expectancy": 0.05

}

###############################################################################
# Edge Score
###############################################################################

EDGE_WEIGHTS = {

    "Expectancy": 0.35,

    "Profit Factor": 0.30,

    "Reward Risk": 0.20,

    "Profit Velocity": 0.15

}

###############################################################################
# Reliability Score
###############################################################################

RELIABILITY_WEIGHTS = {

    "Trades / Year": 0.30,

    "Winning Exit %": 0.25,

    "Losing Exit %": 0.20,

    "Signal Quality": 0.25

}

###############################################################################
# Efficiency Score
###############################################################################

EFFICIENCY_WEIGHTS = {

    "Holding Efficiency": 0.40,

    "Profit Velocity": 0.30,

    "Expectancy": 0.30

}

###############################################################################
# Portfolio Allocation
###############################################################################

PORTFOLIO_WEIGHTS = {

    "Composite Score": 0.60,

    "Reliability Score": 0.20,

    "Edge Score": 0.20

}

###############################################################################
# Leaderboard Ranking
###############################################################################

LEADERBOARD_WEIGHTS = {

    "Composite Score": 0.50,

    "Edge Score": 0.20,

    "Reliability Score": 0.15,

    "Efficiency Score": 0.15

}

###############################################################################
# Robustness Analysis
###############################################################################

ROBUSTNESS_WEIGHTS = {

    "Composite Consistency": 0.35,

    "Expectancy Stability": 0.25,

    "Profit Factor Stability": 0.20,

    "Reward Risk Stability": 0.20

}

###############################################################################
# Correlation Analysis
###############################################################################

CORRELATION_WEIGHTS = {

    "Pearson": 0.50,

    "Spearman": 0.30,

    "Kendall": 0.20

}