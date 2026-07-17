"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    config/thresholds.py

Purpose:
    Centralized thresholds used throughout the
    institutional strategy comparison platform.

=============================================================
"""

###############################################################################
# Strategy Eligibility
###############################################################################

MIN_EXPECTANCY = 0.00

MIN_PROFIT_FACTOR = 1.00

MIN_REWARD_RISK = 1.00

MIN_TRADES = 20

MIN_TRADES_PER_YEAR = 10

###############################################################################
# Portfolio Filters
###############################################################################

MIN_COMPOSITE_SCORE = 60

MIN_EDGE_SCORE = 50

MIN_RELIABILITY_SCORE = 50

MIN_EFFICIENCY_SCORE = 50

###############################################################################
# Portfolio Constraints
###############################################################################

MAX_POSITION_WEIGHT = 10.0

MIN_POSITION_WEIGHT = 1.0

TOP_STOCKS = 25

###############################################################################
# Robustness Thresholds
###############################################################################

MAX_EXPECTANCY_CV = 0.50

MAX_PROFIT_FACTOR_CV = 0.40

MAX_REWARD_RISK_CV = 0.50

MIN_ROBUSTNESS_SCORE = 60

###############################################################################
# Correlation Thresholds
###############################################################################

LOW_CORRELATION = 0.30

MEDIUM_CORRELATION = 0.60

HIGH_CORRELATION = 0.80

###############################################################################
# Signal Quality
###############################################################################

HIGH_SIGNAL_QUALITY = 80

MEDIUM_SIGNAL_QUALITY = 60

LOW_SIGNAL_QUALITY = 40

###############################################################################
# Holding Efficiency
###############################################################################

HIGH_HOLDING_EFFICIENCY = 80

MEDIUM_HOLDING_EFFICIENCY = 60

LOW_HOLDING_EFFICIENCY = 40

###############################################################################
# Profit Velocity
###############################################################################

HIGH_PROFIT_VELOCITY = 80

MEDIUM_PROFIT_VELOCITY = 60

LOW_PROFIT_VELOCITY = 40

###############################################################################
# Data Quality
###############################################################################

MAX_MISSING_PERCENT = 5

MIN_SAMPLE_SIZE = 30

###############################################################################
# Excel Reporting
###############################################################################

TOP_LEADERBOARD_ROWS = 20

TOP_PORTFOLIO_ROWS = 25