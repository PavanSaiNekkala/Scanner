"""
Configuration File
"""

from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "Strategy_Comparison.xlsx"

# =============================================================================
# METRICS
# =============================================================================

PRIMARY_METRICS = [
    "Overall Score",
    "Performance Score",
    "Reliability Score",
    "Execution Score",
    "Opportunity Score",
]

RECOMMENDATION_COLUMN = "Recommendation"

STOCK_COLUMN = "Stock"

# =============================================================================
# SCORING WEIGHTS
# =============================================================================

WEIGHTS = {
    "Overall Score": 0.40,
    "Performance Score": 0.20,
    "Reliability Score": 0.15,
    "Execution Score": 0.15,
    "Opportunity Score": 0.10,
}

GRADE_RULES = {90: "A+", 80: "A", 70: "B", 60: "C", 50: "D", 0: "F"}

RECOMMENDATION_RULES = {
    90: "Strong Buy",
    80: "Buy",
    70: "Watch",
    60: "Improve",
    50: "Avoid",
    0: "Reject",
}
