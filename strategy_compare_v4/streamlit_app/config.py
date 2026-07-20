"""
config.py
=========

Global configuration for the
Institutional Strategy Platform.
"""

from pathlib import Path

# ==========================================================
# Application
# ==========================================================

APP_NAME = "Institutional Strategy Platform"

APP_VERSION = "4.0"

PAGE_ICON = "📊"

LAYOUT = "wide"

# ==========================================================
# Directories
# ==========================================================

BASE_DIR = Path(__file__).parent

OUTPUT_DIR = BASE_DIR.parent / "output"

ASSETS_DIR = BASE_DIR / "assets"

# ==========================================================
# Reports
# ==========================================================

STRATEGY_REPORT = "Strategy_Comparison.xlsx"

STOCK_REPORT = "Stock_Comparison.xlsx"

LEADERBOARD_REPORT = "Leaderboards.xlsx"

ROBUSTNESS_REPORT = "Robustness.xlsx"

CORRELATION_REPORT = "Correlation.xlsx"

PORTFOLIO_REPORT = "Institutional_Portfolio.xlsx"

FINAL_REPORT = "Institutional_Strategy_Report.xlsx"

# ==========================================================
# Worksheets
# ==========================================================

STRATEGY_RANKINGS = "Strategy Rankings"

STRATEGY_SUMMARY = "Strategy Summary"

TOP_OPPORTUNITIES = "Top Opportunities"

STOCK_RANKINGS = "Stock Rankings"

STOCK_SUMMARY = "Stock Summary"

OVERALL_LEADERBOARD = "Overall Leaderboard"

STRATEGY_LEADERBOARD = "Strategy Leaderboard"

STOCK_LEADERBOARD = "Stock Leaderboard"

EDGE_LEADERBOARD = "Edge Leaderboard"

PORTFOLIO = "Portfolio"

PORTFOLIO_SUMMARY = "Portfolio Summary"

ROBUSTNESS = "Robustness"

CONSISTENCY = "Consistency"

CORRELATION = "Correlation"

DIVERSIFICATION = "Diversification"

# ==========================================================
# Column Names
# ==========================================================

STRATEGY = "Strategy"

STOCK = "Stock"

RECOMMENDATION = "Recommendation"

COMPOSITE_SCORE = "Composite Score"

INSTITUTIONAL_SCORE = "Institutional Score"

EDGE_SCORE = "Edge Score"

RELIABILITY_SCORE = "Reliability Score"

EFFICIENCY_SCORE = "Efficiency Score"

RISK_SCORE = "Risk Score"

RETURN_SCORE = "Return Score"

OPPORTUNITY_SCORE = "Opportunity Score"

WEIGHT = "Weight %"

EXPECTED_RETURN = "Expected Return %"

EXPECTANCY = "Expectancy%"

PROFIT_FACTOR = "Profit Factor"

REWARD_RISK = "Reward Risk"

TRADES_YEAR = "Trades / Year"

# ==========================================================
# Recommendations
# ==========================================================

RECOMMENDATIONS = [
    "STRONG BUY",
    "BUY",
    "WATCH",
    "IMPROVE",
    "AVOID",
    "REJECT",
]

# ==========================================================
# Charts
# ==========================================================

DEFAULT_HEIGHT = 550

TOP_N = 20

MAX_ROWS = 500

# ==========================================================
# Colors
# ==========================================================

COLORS = {
    "STRONG BUY": "#16A34A",
    "BUY": "#2563EB",
    "WATCH": "#EAB308",
    "IMPROVE": "#F97316",
    "AVOID": "#DC2626",
    "REJECT": "#7C3AED",
}
