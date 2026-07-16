"""
Strategy Comparison Dashboard Configuration
"""

from pathlib import Path

###########################################################################
# PROJECT PATHS
###########################################################################

BASE_DIR = Path(__file__).resolve().parent

OUTPUTS = BASE_DIR / "outputs"

REPORTS = BASE_DIR / "reports"

ASSETS = BASE_DIR / "assets"

OUTPUTS.mkdir(

    exist_ok=True

)

REPORTS.mkdir(

    exist_ok=True

)

ASSETS.mkdir(

    exist_ok=True

)

###########################################################################
# INPUT / OUTPUT
###########################################################################

INPUT_PATTERN = "Output*.xlsx"

REPORT_NAME = REPORTS / "Strategy_Comparison.xlsx"

###########################################################################
# EXCEL SHEETS
###########################################################################

SHEETS = {

    "ranking":

        "Strategy Ranking",

    "recommendations":

        "Recommendations",

    "overlap":

        "Top Stocks",

    "executive":

        "Executive Summary",

    "comparison":

        "Comparison",

    "analytics":

        "Analytics"

}

###########################################################################
# REQUIRED COLUMNS
###########################################################################

REQUIRED_COLUMNS = [

    "Strategy Rank",

    "Stock",

    "Overall Score",

    "Recommendation",

    "Performance Score",

    "Reliability Score",

    "Execution Score",

    "Opportunity Score"

]

###########################################################################
# PRIMARY METRICS
###########################################################################

PRIMARY_METRICS = (

    "Overall Score",

    "Performance Score",

    "Reliability Score",

    "Execution Score",

    "Opportunity Score"

)

###########################################################################
# SCORING WEIGHTS
###########################################################################

WEIGHTS = {

    "Overall Score":

        0.40,

    "Performance Score":

        0.20,

    "Reliability Score":

        0.15,

    "Execution Score":

        0.15,

    "Opportunity Score":

        0.10

}

###########################################################################
# GRADE RULES
###########################################################################

GRADE_RULES = {

    90:

        "A+",

    80:

        "A",

    70:

        "B",

    60:

        "C",

    50:

        "D",

    0:

        "F"

}

###########################################################################
# RECOMMENDATION RULES
###########################################################################

RECOMMENDATION_RULES = {

    90:

        "Strong Buy",

    80:

        "Buy",

    70:

        "Watch",

    60:

        "Improve",

    50:

        "Avoid",

    0:

        "Reject"

}

###########################################################################
# DASHBOARD SETTINGS
###########################################################################

TOP_N = 10

DEFAULT_RADAR_INDEX = 0

DECIMAL_PLACES = 2

###########################################################################
# CHART SETTINGS
###########################################################################

CHART_HEIGHT = 500

PIE_HEIGHT = 450

RADAR_HEIGHT = 600

SCATTER_HEIGHT = 550

HEATMAP_HEIGHT = 700

###########################################################################
# STREAMLIT SETTINGS
###########################################################################

PAGE_TITLE = "Strategy Comparison Dashboard"

PAGE_ICON = "📈"

LAYOUT = "wide"

DATAFRAME_WIDTH = "stretch"

###########################################################################
# EXPORT SETTINGS
###########################################################################

CSV_EXPORT_NAME = "Strategy_Ranking.csv"

JSON_EXPORT_NAME = "Strategy_Ranking.json"

###########################################################################
# APPLICATION INFORMATION
###########################################################################

APP_NAME = "Strategy Comparison Dashboard"

APP_VERSION = "3.0.0"

AUTHOR = "Pavan Sai Nekkala"

DESCRIPTION = (

    "Institutional-grade strategy comparison dashboard "

    "for evaluating quantitative trading strategies."

)