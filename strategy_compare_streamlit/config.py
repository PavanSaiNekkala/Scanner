from pathlib import Path

###########################################################################
# PATHS
###########################################################################

BASE_DIR = Path(__file__).resolve().parent

OUTPUTS = BASE_DIR / "outputs"

REPORTS = BASE_DIR / "reports"

OUTPUTS.mkdir(

    exist_ok=True

)

REPORTS.mkdir(

    exist_ok=True

)

REPORT_NAME = REPORTS / "Strategy_Comparison.xlsx"

###########################################################################
# METRICS
###########################################################################

PRIMARY_METRICS = [

    "Overall Score",

    "Performance Score",

    "Reliability Score",

    "Execution Score",

    "Opportunity Score"

]

###########################################################################
# WEIGHTS
###########################################################################

WEIGHTS = {

    "Overall Score": 0.40,

    "Performance Score": 0.20,

    "Reliability Score": 0.15,

    "Execution Score": 0.15,

    "Opportunity Score": 0.10

}

###########################################################################
# GRADE RULES
###########################################################################

GRADE_RULES = {

    90: "A+",

    80: "A",

    70: "B",

    60: "C",

    50: "D",

    0: "F"

}

###########################################################################
# RECOMMENDATION RULES
###########################################################################

RECOMMENDATION_RULES = {

    90: "Strong Buy",

    80: "Buy",

    70: "Watch",

    60: "Improve",

    50: "Avoid",

    0: "Reject"

}