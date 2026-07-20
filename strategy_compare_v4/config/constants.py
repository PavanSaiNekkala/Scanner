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

Guidelines
----------
• Column Names
• Report Names
• Excel Sheet Names
• Recommendation Labels
• File Names
• Default Configuration

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

# ============================================================
# Portfolio Defaults
# ============================================================

CAPITAL = 1_000_000

TOP_STOCKS = 25

MAX_POSITION_WEIGHT = 10.0

# ============================================================
# Common Column Names
# ============================================================

STOCK = "Stock"

STRATEGY = "Strategy"

INSTITUTION_RANK = "Institution Rank"

RECOMMENDATION = "Recommendation"

WEIGHT = "Weight"

# ============================================================
# Validation Metrics
# ============================================================

VALIDATION_STATUS = "Validation Status"

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
# Required Columns
# ============================================================

REQUIRED_COMPARISON_COLUMNS = [
    "Stock",
    "Strategy",
    "Institution Rank",
    "Composite Score",
    "Recommendation",
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

FINAL_INSTITUTIONAL_REPORT = "Institutional_Strategy_Report.xlsx"

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
