"""
============================================================
Institutional Strategy Comparison Engine V3

Global Configuration

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

from pathlib import Path

# ============================================================
# Project
# ============================================================

PROJECT_NAME = "Institutional Strategy Comparison Engine"

VERSION = "3.0.0"

AUTHOR = "Pavan Sai"

# ============================================================
# Directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

INPUT_DIR = DATA_DIR / "input"

INTERIM_DIR = DATA_DIR / "interim"

PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR = BASE_DIR / "outputs"

REPORT_DIR = OUTPUT_DIR / "reports"

EXCEL_DIR = OUTPUT_DIR / "excel"

CHART_DIR = OUTPUT_DIR / "charts"

LOG_DIR = OUTPUT_DIR / "logs"

# ============================================================
# Logging
# ============================================================

LOG_LEVEL = "INFO"

LOG_FILE = LOG_DIR / "strategy_compare.log"

# ============================================================
# Random State
# ============================================================

RANDOM_STATE = 42

# ============================================================
# Normalization
# ============================================================

DEFAULT_NORMALIZATION = "Percentile"

NORMALIZATION_METHODS = [

    "Percentile",

    "Min-Max",

    "Z-Score",

    "Robust Z-Score",

    "Quantile"

]

# ============================================================
# Recommendation Thresholds
# ============================================================

RECOMMENDATION_THRESHOLDS = {

    "STRONG BUY": 90,

    "BUY": 80,

    "ACCUMULATE": 70,

    "WATCH": 60,

    "HOLD": 50,

    "REDUCE": 40,

    "SELL": 30,

    "AVOID": 0

}

# ============================================================
# Composite Score Weights
# ============================================================

COMPOSITE_SCORE_WEIGHTS = {

    "Institutional Score": 0.40,

    "Edge Score": 0.15,

    "Risk Score": 0.10,

    "Efficiency Score": 0.10,

    "Stability Score": 0.10,

    "Reliability Score": 0.05,

    "Opportunity Score": 0.05,

    "Execution Score": 0.05

}

# ============================================================
# Institutional Score Weights
# ============================================================

INSTITUTIONAL_SCORE_WEIGHTS = {

    "Edge Score": 0.20,

    "Risk Score": 0.15,

    "Efficiency Score": 0.15,

    "Stability Score": 0.15,

    "Reliability Score": 0.15,

    "Opportunity Score": 0.10,

    "Execution Score": 0.10

}

# ============================================================
# Optimization
# ============================================================

MONTE_CARLO_SIMULATIONS = 1000

MONTE_CARLO_NOISE = 0.05

# ============================================================
# Visualization
# ============================================================

FIGURE_DPI = 300

HEATMAP_SIZE = (14, 12)

SCATTER_SIZE = (8, 6)

HISTOGRAM_SIZE = (8, 5)

BOXPLOT_SIZE = (8, 5)

# ============================================================
# Reporting
# ============================================================

TOP_N = 25

TOP_RANKING = 10

# ============================================================
# Streamlit
# ============================================================

PAGE_TITLE = PROJECT_NAME

PAGE_ICON = "📈"

LAYOUT = "wide"

# ============================================================
# Testing
# ============================================================

TEST_RANDOM_STATE = 123

TEST_SAMPLE_SIZE = 100

# ============================================================
# Performance
# ============================================================

ENABLE_CACHE = True

MAX_THREADS = 4

# ============================================================
# File Formats
# ============================================================

SUPPORTED_INPUT = [

    ".csv",

    ".xlsx"

]

SUPPORTED_EXPORT = [

    ".xlsx",

    ".csv"

]

# ============================================================
# Create Required Directories
# ============================================================

for directory in [

    DATA_DIR,

    INPUT_DIR,

    INTERIM_DIR,

    PROCESSED_DIR,

    OUTPUT_DIR,

    REPORT_DIR,

    EXCEL_DIR,

    CHART_DIR,

    LOG_DIR,

]:

    directory.mkdir(

        parents=True,

        exist_ok=True

    )