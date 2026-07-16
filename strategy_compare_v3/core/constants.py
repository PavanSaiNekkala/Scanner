"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/constants.py
Author : Pavan Sai
Description :
Centralized constants used across the entire application.
============================================================
"""

from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

INPUT_DIR = DATA_DIR / "input"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"
EXCEL_DIR = PROJECT_ROOT / "outputs" / "excel"
CHART_DIR = PROJECT_ROOT / "outputs" / "charts"
LOG_DIR = PROJECT_ROOT / "outputs" / "logs"

# ==========================================================
# FILE TYPES
# ==========================================================

SUPPORTED_FILE_TYPES = (
    ".csv",
    ".xlsx",
    ".xls",
)

# ==========================================================
# MISSING VALUE STRINGS
# ==========================================================

MISSING_STRINGS = [
    "",
    " ",
    "NA",
    "N/A",
    "NULL",
    "null",
    "None",
    "none",
    "-",
]

# ==========================================================
# OUTLIER SETTINGS
# ==========================================================

IQR_MULTIPLIER = 1.5

Z_SCORE_THRESHOLD = 3.0

# ==========================================================
# DATA QUALITY WEIGHTS
# ==========================================================

QUALITY_WEIGHTS = {

    "missing": 0.30,

    "duplicates": 0.20,

    "datatype": 0.15,

    "outliers": 0.20,

    "consistency": 0.15

}

# ==========================================================
# SCALING
# ==========================================================

MIN_SCORE = 0.0

MAX_SCORE = 100.0

# ==========================================================
# ROUNDING
# ==========================================================

DECIMAL_PLACES = 4

PERCENT_DECIMALS = 2

# ==========================================================
# REPORT SHEETS
# ==========================================================

SHEET_SUMMARY = "Dataset Summary"

SHEET_DESCRIPTIVE = "Descriptive Statistics"

SHEET_DISTRIBUTION = "Distribution"

SHEET_OUTLIERS = "Outliers"

SHEET_MISSING = "Missing Values"

SHEET_DUPLICATES = "Duplicates"

SHEET_QUALITY = "Quality Score"

# ==========================================================
# DATA TYPES
# ==========================================================

NUMERIC_DTYPES = [

    "int64",

    "float64",

    "int32",

    "float32",

]

# ==========================================================
# DEFAULT REPORT NAME
# ==========================================================

DEFAULT_REPORT_NAME = "Data_Profile_Report.xlsx"

# ==========================================================
# LOGGING
# ==========================================================

LOG_FORMAT = (

    "%(asctime)s | "

    "%(levelname)s | "

    "%(name)s | "

    "%(message)s"

)

LOG_LEVEL = "INFO"

# ==========================================================
# VERSION
# ==========================================================

ENGINE_NAME = "Institutional Strategy Comparison Engine"

ENGINE_VERSION = "3.0.0"

AUTHOR = "Pavan Sai"

# ==========================================================
# RANDOM SEED
# ==========================================================

RANDOM_STATE = 42