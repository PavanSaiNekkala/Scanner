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

=============================================================
"""

from __future__ import annotations

# ============================================================
# Platform Thresholds
# ============================================================

EPSILON = 1e-12

NORMALIZED_MIN = 0.0

NORMALIZED_MAX = 100.0

# ============================================================
# Strategy Eligibility
# ============================================================

MIN_EXPECTANCY = 0.00

MIN_PROFIT_FACTOR = 1.00

MIN_REWARD_RISK = 1.00

MIN_TRADES = 50

MIN_TRADES_PER_YEAR = 10

MIN_YEARS = 1

MIN_WIN_RATE = 40.0

# ============================================================
# Institutional Score Filters
# ============================================================

MIN_COMPOSITE_SCORE = 60

MIN_EDGE_SCORE = 50

MIN_RELIABILITY_SCORE = 50

MIN_EFFICIENCY_SCORE = 50

MIN_RISK_SCORE = 50

MIN_CONSISTENCY_SCORE = 50

MIN_VALIDATION_SCORE = 50

# ============================================================
# Portfolio Construction
# ============================================================

TOP_STOCKS = 25

MIN_HOLDINGS = 10

MAX_HOLDINGS = 50

MIN_POSITION_WEIGHT = 1.0

MAX_POSITION_WEIGHT = 10.0

MAX_SINGLE_STRATEGY_WEIGHT = 25.0

# ============================================================
# Robustness Analysis
# ============================================================

MAX_EXPECTANCY_CV = 0.50

MAX_PROFIT_FACTOR_CV = 0.40

MAX_REWARD_RISK_CV = 0.50

MIN_ROBUSTNESS_SCORE = 75

MAX_EXPECTANCY_STD = 20.0

MAX_SCORE_STD = 15.0

# ============================================================
# Correlation Analysis
# ============================================================

LOW_CORRELATION = 0.30

MEDIUM_CORRELATION = 0.60

HIGH_CORRELATION = 0.80

MAX_PORTFOLIO_CORRELATION = 0.70

IDEAL_PORTFOLIO_CORRELATION = 0.50
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

# ============================================================
# Institutional Score Interpretation
# ============================================================

EXCELLENT_SCORE = 90

GOOD_SCORE = 75

ACCEPTABLE_SCORE = 60

POOR_SCORE = 40

VERY_POOR_SCORE = 20

# ============================================================
# Data Quality
# ============================================================

MAX_MISSING_PERCENT = 5

MIN_SAMPLE_SIZE = 30

MIN_STOCKS_FOR_COMPARISON = 5

MIN_STRATEGIES_FOR_COMPARISON = 2

MAX_DUPLICATE_PERCENT = 1.0

# ============================================================
# Outlier Detection
# ============================================================

EXTREME_RETURN_THRESHOLD = 100.0

EXTREME_EXPECTANCY_THRESHOLD = 50.0

Z_SCORE_OUTLIER = 3.0

IQR_MULTIPLIER = 1.5

DEFAULT_WINSOR_LOWER = 0.05

DEFAULT_WINSOR_UPPER = 0.95

# ============================================================
# Excel Reporting
# ============================================================

TOP_LEADERBOARD_ROWS = 20

TOP_PORTFOLIO_ROWS = 25

TOP_STRATEGY_ROWS = 10

MAX_EXCEL_SHEETNAME_LENGTH = 31

# ============================================================
# Recommendation Score Bands
# ============================================================

STRONG_BUY_SCORE = 90

BUY_SCORE = 75

WATCH_SCORE = 60

IMPROVE_SCORE = 45

AVOID_SCORE = 30

REJECT_SCORE = 0

# ============================================================
# Public Exports
# ============================================================

__all__ = [name for name in globals() if name.isupper()]
