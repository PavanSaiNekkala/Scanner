"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
config/constants.py

Purpose
-------
Centralized constants shared across the entire
Institutional Strategy Comparison Platform.

=============================================================
"""

from __future__ import annotations

from pathlib import Path

# ============================================================
# Project Directories
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIRECTORY = PROJECT_ROOT

OUTPUT_DIRECTORY = PROJECT_ROOT / "output"

REPORT_DIRECTORY = OUTPUT_DIRECTORY / "reports"

EXPORT_DIRECTORY = OUTPUT_DIRECTORY / "exports"

LOG_DIRECTORY = OUTPUT_DIRECTORY / "logs"

# ============================================================
# Platform Defaults
# ============================================================

EPSILON = 1e-12

DEFAULT_ROUNDING = 2

DEFAULT_SHEET_NAME = "Sheet1"

MAX_SHEET_NAME = 31

DEFAULT_PATTERN = "*"

CSV_PATTERN = "**/*.csv"

STATISTICS_PATTERN = "**/*Statistics.xlsx"

# ============================================================
# Portfolio Defaults
# ============================================================

CAPITAL = 1_000_000

TOP_STOCKS = 25

MAX_POSITION_WEIGHT = 10.0

MIN_POSITION_WEIGHT = 0.0

# ============================================================
# Normalization
# ============================================================

NORMALIZED_MIN = 0.0

NORMALIZED_MAX = 100.0

DEFAULT_WINSOR_LOWER = 0.05

DEFAULT_WINSOR_UPPER = 0.95

# ============================================================
# Common Column Names
# ============================================================

STOCK = "Stock"

STRATEGY = "Strategy"

INSTITUTION_RANK = "Institution Rank"

RECOMMENDATION = "Recommendation"

WEIGHT = "Weight"

VALIDATION_STATUS = "Validation Status"

# ============================================================
# Required Columns
# ============================================================

REQUIRED_COMPARISON_COLUMNS = [
    STOCK,
    STRATEGY,
    INSTITUTION_RANK,
    "Composite Score",
    RECOMMENDATION,
]

# ============================================================
# Strategy Discovery
# ============================================================

STRATEGY_FOLDERS = [
    "backtest_F_ATR_FT",
    "backtest_F_ATR_Tr",
    "backtest_F_Str_FT",
    "backtest_F_Str_Tr",
    "backtest_WF_ATR_FT",
    "backtest_WF_ATR_Tr",
    "backtest_WF_Str_FT",
    "backtest_WF_Str_Tr",
]

# ============================================================
# Performance Metrics
# ============================================================

EXPECTANCY = "Expectancy"

EXPECTANCY_PERCENT = "Expectancy%"

PROFIT_FACTOR = "Profit Factor"

REWARD_RISK = "Reward Risk"

PROFIT_VELOCITY = "Profit Velocity"

TRADES = "Trades"

TRADES_PER_YEAR = "Trades / Year"

# ============================================================
# Exit Metrics
# ============================================================

WINNING_EXIT = "Winning Exit %"

LOSING_EXIT = "Losing Exit %"

TARGET_PERCENT = "Target %"

TRAIL_PERCENT = "Trail %"

STOP_PERCENT = "Stop %"

TIME_PERCENT = "Time %"

# ============================================================
# Efficiency Metrics
# ============================================================

HOLDING_EFFICIENCY = "Holding Efficiency"

SIGNAL_QUALITY = "Signal Quality"

# ============================================================
# Institutional Scores
# ============================================================

EDGE_SCORE = "Edge Score"

RELIABILITY_SCORE = "Reliability Score"

EFFICIENCY_SCORE = "Efficiency Score"

COMPOSITE_SCORE = "Composite Score"

# ============================================================
# Report Names
# ============================================================

SUMMARY = "Summary"

PORTFOLIO = "Portfolio"

LEADERBOARD = "Leaderboard"

ROBUSTNESS = "Robustness"

CORRELATION = "Correlation"

# ============================================================
# Excel Sheet Names
# ============================================================

SHEET_STRATEGY_COMPARISON = "Strategy Comparison"

SHEET_BEST_STRATEGY = "Best Strategy"

SHEET_STRATEGY_SUMMARY = "Strategy Summary"

SHEET_STOCK_COMPARISON = "Stock Comparison"

SHEET_STOCK_RANKINGS = "Stock Rankings"

SHEET_OVERALL_LEADERBOARD = "Overall Leaderboard"

SHEET_STRATEGY_LEADERBOARD = "Strategy Leaderboard"

SHEET_STOCK_LEADERBOARD = "Stock Leaderboard"

SHEET_EDGE_LEADERBOARD = "Edge Leaderboard"

SHEET_ROBUSTNESS = "Robustness"

SHEET_STABILITY = "Stability"

SHEET_CORRELATION = "Correlation"

SHEET_DIVERSIFICATION = "Diversification"

SHEET_PORTFOLIO = "Portfolio"

SHEET_PORTFOLIO_SUMMARY = "Portfolio Summary"

# ============================================================
# Recommendation Labels
# ============================================================

STRONG_BUY = "Strong Buy"

BUY = "Buy"

WATCH = "Watch"

IMPROVE = "Improve"

AVOID = "Avoid"

REJECT = "Reject"

RECOMMENDATION_ORDER = [
    STRONG_BUY,
    BUY,
    WATCH,
    IMPROVE,
    AVOID,
    REJECT,
]

# ============================================================
# Output File Names
# ============================================================

DERIVED_METRICS_REPORT = "Derived_Metrics.xlsx"

COMPARISON_REPORT = "Strategy_Comparison.xlsx"

FINAL_REPORT = "Institutional_Strategy_Report.xlsx"

FINAL_INSTITUTIONAL_REPORT = FINAL_REPORT

PORTFOLIO_REPORT = "Institutional_Portfolio.xlsx"

LEADERBOARD_REPORT = "Leaderboards.xlsx"

ROBUSTNESS_REPORT = "Robustness.xlsx"

CORRELATION_REPORT = "Correlation.xlsx"

STOCK_REPORT = "Stock_Comparison.xlsx"

STRATEGY_REPORT = "Strategy_Comparison.xlsx"

# ============================================================
# Public Exports
# ============================================================

__all__ = [name for name in globals() if name.isupper()]
