"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
config/thresholds.py

Purpose
-------
Centralized threshold values used throughout the
Institutional Strategy Comparison Platform.

Guidelines
----------
• Strategy Eligibility
• Portfolio Filters
• Portfolio Constraints
• Robustness
• Correlation
• Quality Classification
• Data Validation
• Reporting

=============================================================
"""

from __future__ import annotations

# ============================================================
# Strategy Eligibility
# ============================================================

MIN_EXPECTANCY = 0.00

MIN_PROFIT_FACTOR = 1.00

MIN_REWARD_RISK = 1.00

MIN_TRADES = 20

MIN_TRADES_PER_YEAR = 10

# ============================================================
# Institutional Score Filters
# ============================================================

MIN_COMPOSITE_SCORE = 60

MIN_EDGE_SCORE = 50

MIN_RELIABILITY_SCORE = 50

MIN_EFFICIENCY_SCORE = 50

# ============================================================
# Portfolio Construction
# ============================================================

TOP_STOCKS = 25

MAX_POSITION_WEIGHT = 10.0

MIN_POSITION_WEIGHT = 1.0

# ============================================================
# Robustness Analysis
# ============================================================

MAX_EXPECTANCY_CV = 0.50

MAX_PROFIT_FACTOR_CV = 0.40

MAX_REWARD_RISK_CV = 0.50

MIN_ROBUSTNESS_SCORE = 60

# ============================================================
# Correlation Analysis
# ============================================================

LOW_CORRELATION = 0.30

MEDIUM_CORRELATION = 0.60

HIGH_CORRELATION = 0.80

# Diversification guidance

MAX_PORTFOLIO_CORRELATION = 0.70

# ============================================================
# Quality Classification
# ============================================================

HIGH_SIGNAL_QUALITY = 80
MEDIUM_SIGNAL_QUALITY = 60
LOW_SIGNAL_QUALITY = 40

HIGH_HOLDING_EFFICIENCY = 80
MEDIUM_HOLDING_EFFICIENCY = 60
LOW_HOLDING_EFFICIENCY = 40

HIGH_PROFIT_VELOCITY = 80
MEDIUM_PROFIT_VELOCITY = 60
LOW_PROFIT_VELOCITY = 40

# Institutional score interpretation

EXCELLENT_SCORE = 90

GOOD_SCORE = 75

ACCEPTABLE_SCORE = 60

POOR_SCORE = 40

# ============================================================
# Data Quality
# ============================================================

MAX_MISSING_PERCENT = 5

MIN_SAMPLE_SIZE = 30

MIN_STOCKS_FOR_COMPARISON = 5

MIN_STRATEGIES_FOR_COMPARISON = 2

# ============================================================
# Data Validation / Outlier Detection
# ============================================================

# Maximum absolute return (%) considered reasonable.
# Values beyond this are flagged as extreme.
EXTREME_RETURN_THRESHOLD = 100.0

# Maximum absolute expectancy (%) before flagging.
EXTREME_EXPECTANCY_THRESHOLD = 50.0

# ============================================================
# Excel Reporting
# ============================================================

TOP_LEADERBOARD_ROWS = 20

TOP_PORTFOLIO_ROWS = 25

TOP_STRATEGY_ROWS = 10
