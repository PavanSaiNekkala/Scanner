"""
=====================================================================
Institutional Stock Analytics Engine v3.0
=====================================================================

Input  : Backtest CSV
Output : Institutional_Stock_Report.csv

Author  : Pavan Sai
Version : 3.0
"""

import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {

    "INPUT_FILE": "Input_backtest_WF_ATR_Tr.csv",

    "OUTPUT_FILE": "Output_backtest_WF_ATR_Tr_Report.csv",

    "ROUND": 2

}

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)

# ============================================================
# REQUIRED INPUT COLUMNS
# ============================================================

REQUIRED_COLUMNS = [

    "Stock",

    "Signals today",

    "Rank",

    "Exp/DAY%",

    "RS%",

    "Trades",

    "Win%",

    "Target #",

    "Target %",

    "Trail #",

    "Trail %",

    "Stop #",

    "Stop %",

    "Time #",

    "Time %",

    "Time-win",

    "Time-loss",

    "Expectancy%",

    "Avg win%",

    "Avg loss%",

    "Avg days",

    "BT from",

    "BT to",

    "Years",

    "Remark"

]

# ============================================================
# NUMERIC COLUMNS
# ============================================================

NUMERIC_COLUMNS = [

    "Signals today",

    "Rank",

    "Exp/DAY%",

    "RS%",

    "Trades",

    "Win%",

    "Target #",

    "Target %",

    "Trail #",

    "Trail %",

    "Stop #",

    "Stop %",

    "Time #",

    "Time %",

    "Time-win",

    "Time-loss",

    "Expectancy%",

    "Avg win%",

    "Avg loss%",

    "Avg days",

    "Years"

]

# ============================================================
# LOAD CSV
# ============================================================

def load_data():

    logger.info("Loading Input CSV...")

    file = Path(CONFIG["INPUT_FILE"])

    if not file.exists():

        raise FileNotFoundError(

            f"{CONFIG['INPUT_FILE']} not found."

        )

    df = pd.read_csv(file)

    logger.info(

        f"Rows Loaded : {len(df)}"

    )

    return df

# ============================================================
# VALIDATE COLUMNS
# ============================================================

def validate_columns(df):

    missing = [

        col

        for col in REQUIRED_COLUMNS

        if col not in df.columns

    ]

    if missing:

        raise ValueError(

            f"Missing Columns : {missing}"

        )

    logger.info(

        "Column Validation Successful."

    )

# ============================================================
# CONVERT DATATYPES
# ============================================================

def convert_datatypes(df):

    logger.info(

        "Converting Data Types..."

    )

    for col in NUMERIC_COLUMNS:

        df[col] = pd.to_numeric(

            df[col],

            errors="coerce"

        )

    df["BT from"] = pd.to_datetime(

        df["BT from"],

        errors="coerce"

    )

    df["BT to"] = pd.to_datetime(

        df["BT to"],

        errors="coerce"

    )

    return df

# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):

    logger.info(

        "Cleaning Dataset..."

    )

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    logger.info(

        f"Duplicates Removed : {removed}"

    )

    df = df.dropna(

        subset=[

            "Stock",

            "Trades",

            "Expectancy%",

            "Win%"

        ]

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

    return df

# ============================================================
# VALIDATE VALUES
# ============================================================

def validate_values(df):

    logger.info(

        "Performing Data Validation..."

    )

    percentage_columns = [

        "Win%",

        "Target %",

        "Trail %",

        "Stop %",

        "Time %",

        "Expectancy%",

        "Avg win%",

        "Avg loss%"

    ]

    for col in percentage_columns:

        if (df[col] < 0).any():

            logger.warning(

                f"Negative values found in {col}"

            )

    if (df["Trades"] <= 0).any():

        logger.warning(

            "Stocks with zero trades detected."

        )

    return df

# ============================================================
# DATA SUMMARY
# ============================================================

def print_data_summary(df):

    print()

    print("=" * 65)

    print("INPUT DATA SUMMARY")

    print("=" * 65)

    print(f"Stocks              : {len(df)}")

    bt_from = df["BT from"].min()
    bt_to = df["BT to"].max()

    print(
        f"Backtest From       : {bt_from.date() if pd.notna(bt_from) else 'N/A'}"
    )

    print(
        f"Backtest To         : {bt_to.date() if pd.notna(bt_to) else 'N/A'}"
    )
    print(f"Average Trades      : {df['Trades'].mean():.2f}")

    print(f"Average Win %       : {df['Win%'].mean():.2f}")

    print(f"Average Expectancy  : {df['Expectancy%'].mean():.2f}")

    print(f"Average Holding     : {df['Avg days'].mean():.2f}")

    print("=" * 65)

# ============================================================
# ABSOLUTE SCORING ENGINE
# ============================================================

def score_metric(series, metric):

    x = series.astype(float)

    score = pd.Series(
        np.nan,
        index=x.index,
        dtype=float
    )

    # --------------------------------------------------------
    # PROFIT FACTOR
    # --------------------------------------------------------

    if metric == "PF":

        score = np.select(

            [

                x < 1.00,

                x < 1.20,

                x < 1.50,

                x < 2.00,

                x >= 2.00

            ],

            [

                0,

                40,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # EXPECTANCY
    # --------------------------------------------------------

    elif metric == "EXPECTANCY":

        score = np.select(

            [

                x < 0,

                x < 0.50,

                x < 1.00,

                x < 2.00,

                x >= 2.00

            ],

            [

                0,

                40,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # REWARD RISK
    # --------------------------------------------------------

    elif metric == "RR":

        score = np.select(

            [

                x < 1,

                x < 1.5,

                x < 2,

                x < 3,

                x >= 3

            ],

            [

                0,

                40,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # WIN RATE
    # --------------------------------------------------------

    elif metric == "WIN":

        score = np.select(

            [

                x < 35,

                x < 45,

                x < 55,

                x < 65,

                x >= 65

            ],

            [

                0,

                40,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # TRADES
    # --------------------------------------------------------

    elif metric == "TRADES":

        score = np.select(

            [

                x < 100,

                x < 300,

                x < 600,

                x < 1000,

                x >= 1000

            ],

            [

                20,

                50,

                75,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # YEARS
    # --------------------------------------------------------

    elif metric == "YEARS":

        score = np.select(

            [

                x < 2,

                x < 4,

                x < 6,

                x < 10,

                x >= 10

            ],

            [

                30,

                50,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # PROFIT VELOCITY
    # --------------------------------------------------------

    elif metric == "PROFIT_VELOCITY":

        score = np.select(

            [

                x < 10,

                x < 50,

                x < 100,

                x < 200,

                x >= 200

            ],

            [

                20,

                40,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # HOLDING EFFICIENCY
    # --------------------------------------------------------

    elif metric == "HOLDING_EFFICIENCY":

        score = np.select(

            [

                x < 0.10,

                x < 0.30,

                x < 0.50,

                x < 1.00,

                x >= 1.00

            ],

            [

                20,

                40,

                70,

                90,

                100

            ]

        )

    # --------------------------------------------------------
    # EXIT EDGE
    # --------------------------------------------------------

    elif metric == "EXIT_EDGE":

        score = np.select(

            [

                x < 0,

                x < 20,

                x < 40,

                x < 60,

                x >= 60

            ],

            [

                20,

                40,

                70,

                90,

                100

            ]

        )

    return pd.Series(
        score,
        index=series.index
    )

# ============================================================
# SAFE DIVISION
# ============================================================

def safe_divide(a, b):

    return pd.Series(

        np.where(

            b != 0,

            a / b,

            np.nan

        ),

        index=a.index

    )

# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data():

    df = load_data()

    validate_columns(df)

    df = convert_datatypes(df)

    df = clean_data(df)

    df = validate_values(df)

    print_data_summary(df)

    logger.info(

        "Data Preparation Completed."

    )

    return df

# ============================================================
# PART 2 : DERIVED METRICS ENGINE
# ============================================================

logger.info("Loading Derived Metrics Engine...")

# ============================================================
# CALCULATE DERIVED METRICS
# ============================================================

def calculate_metrics(df):

    logger.info("Calculating Derived Metrics...")

    # --------------------------------------------------------
    # 1. LOSS %
    # --------------------------------------------------------

    df["Loss %"] = (

        100 -

        df["Win%"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 2. REWARD : RISK
    # --------------------------------------------------------

    df["Reward Risk"] = safe_divide(

        df["Avg win%"],

        df["Avg loss%"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # PROFIT FACTOR (Institutional Approximation)
    # --------------------------------------------------------

    gross_profit = (
        (df["Win%"] / 100)
        * df["Avg win%"]
    )

    gross_loss = (
        ((100 - df["Win%"]) / 100)
        * df["Avg loss%"]
    )

    df["Profit Factor"] = safe_divide(
        gross_profit,
        gross_loss
    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 4. TRADES PER YEAR
    # --------------------------------------------------------

    df["Trades / Year"] = safe_divide(

        df["Trades"],

        df["Years"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 5. PROFIT VELOCITY
    # --------------------------------------------------------

    df["Profit Velocity"] = (

        df["Exp/DAY%"]

        *

        df["Trades"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 6. HOLDING EFFICIENCY
    # --------------------------------------------------------

    df["Holding Efficiency"] = safe_divide(

        df["Expectancy%"],

        df["Avg days"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 7. WINNING EXIT %
    # --------------------------------------------------------

    df["Winning Exit %"] = (

        df["Target %"]

        +

        df["Trail %"]

        +

        df["Time-win"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 8. LOSING EXIT %
    # --------------------------------------------------------

    df["Losing Exit %"] = (

        df["Stop %"]

        +

        df["Time-loss"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 9. EXIT EDGE
    # --------------------------------------------------------

    df["Exit Edge"] = (

        df["Winning Exit %"]

        -

        df["Losing Exit %"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 10. SIGNAL QUALITY
    # --------------------------------------------------------

    df["Signal Quality"] = (
        score_metric(df["Expectancy%"], "EXPECTANCY") * 0.50 +

        score_metric(df["Reward Risk"], "RR") * 0.30 +

        score_metric(df["Win%"], "WIN") * 0.20

    ).round(CONFIG["ROUND"])

    logger.info("Derived Metrics Completed.")

    return df

# ============================================================
# DATA PREVIEW
# ============================================================

def metrics_preview(df):

    print()

    print("=" * 75)

    print("DERIVED METRICS PREVIEW")

    print("=" * 75)

    print(

        df[

            [

                "Stock",

                "Expectancy%",

                "Profit Factor",

                "Reward Risk",

                "Trades / Year",

                "Profit Velocity"

            ]

        ].head(10)

    )

    print("=" * 75)

# ============================================================
# PART 3 : INSTITUTIONAL SCORING ENGINE
# ============================================================

logger.info("Loading Institutional Scoring Engine...")

# ============================================================
# EDGE SCORE
# ============================================================

def edge_score(df):

    logger.info("Calculating Edge Score...")

    score = (

        score_metric(

            df["Expectancy%"],

            "EXPECTANCY"

        ) * 0.40 +

        score_metric(

            df["Profit Factor"],

            "PF"

        ) * 0.35 +

        score_metric(

            df["Reward Risk"],

            "RR"
    
        ) * 0.25

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# RELIABILITY SCORE
# ============================================================

def reliability_score(df):

    logger.info("Calculating Reliability Score...")

    score = (

        score_metric(

            df["Trades"],

            "TRADES"

        ) * 0.70 +

        score_metric(

            df["Years"],

            "YEARS"

        ) * 0.30

    )
    
    return score.round(CONFIG["ROUND"])

# ============================================================
# EFFICIENCY SCORE
# ============================================================

def efficiency_score(df):

    logger.info("Calculating Efficiency Score...")

    score = (

        score_metric(

            df["Profit Velocity"],

            "PROFIT_VELOCITY"

        ) * 0.30 +

        score_metric(

            df["Holding Efficiency"],

            "HOLDING_EFFICIENCY"

        ) * 0.25 +

        score_metric(

            df["Exit Edge"],

            "EXIT_EDGE"

        ) * 0.20 +

        df["Signal Quality"] * 0.25

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# COMPOSITE SCORE
# ============================================================

def composite_score(df):

    logger.info("Calculating Composite Score...")

    score = (

        df["Edge Score"] * 0.45 +

        df["Reliability Score"] * 0.35 +

        df["Efficiency Score"] * 0.20

    )    

    return score.round(CONFIG["ROUND"])

# ============================================================
# RECOMMENDATION
# ============================================================

def recommendation(score):

    if score >= 90:
        return "★★★★★ DEPLOY"

    elif score >= 80:
        return "★★★★ STRONG BUY"

    elif score >= 70:
        return "★★★ BUY"

    elif score >= 60:
        return "★★ WATCH"

    return "★ REJECT"

# ============================================================
# BUILD SCORECARD
# ============================================================

def build_scorecard(df):

    logger.info("Building Institutional Scorecard...")

    df["Edge Score"] = edge_score(df)

    df["Reliability Score"] = reliability_score(df)

    df["Efficiency Score"] = efficiency_score(df)

    df["Composite Score"] = composite_score(df)

    df = df.sort_values(

        by=[

            "Composite Score",

            "Edge Score",

            "Reliability Score",

            "Efficiency Score",

            "Expectancy%",

            "Profit Factor"

        ],

        ascending=False

    )

    df["Institution Rank"] = np.arange(

        1,

        len(df)+1

    )

    df["Recommendation"] = (

        df["Composite Score"]

        .apply(recommendation)

    )

    logger.info("Institutional Ranking Completed.")

    return df

# ============================================================
# SCORE PREVIEW
# ============================================================

def score_preview(df):

    print()

    print("=" * 80)

    print("INSTITUTIONAL SCORECARD")

    print("=" * 80)

    print(

        df[

            [

                "Institution Rank",

                "Stock",

                "Edge Score",

                "Reliability Score",

                "Efficiency Score",

                "Composite Score",

                "Recommendation"

            ]

        ].head(10)

    )

    print("=" * 80)

# ============================================================
# PART 4 : REPORT GENERATOR
# ============================================================

logger.info("Loading Report Generator...")

# ============================================================
# EXPORT REPORT
# ============================================================

def export_report(df):

    logger.info("Preparing Institutional Report...")

    report = df[

        [

            "Institution Rank",

            "Stock",

            "Expectancy%",

            "Profit Factor",

            "Reward Risk",

            "Trades / Year",

            "Profit Velocity",

            "Signal Quality",

            "Holding Efficiency",

            "Winning Exit %",

            "Losing Exit %",

            "Edge Score",

            "Reliability Score",

            "Efficiency Score",

            "Composite Score",

            "Recommendation"

        ]

    ].copy()

    report = report.round(CONFIG["ROUND"])

    report.to_csv(

        CONFIG["OUTPUT_FILE"],

        index=False

    )

    logger.info(

        f"Report Saved : {CONFIG['OUTPUT_FILE']}"

    )

    return report

# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(df):

    print()

    print("="*80)

    print("INSTITUTIONAL STOCK ANALYTICS SUMMARY")

    print("="*80)

    print(f"Stocks Analysed      : {len(df)}")

    print(f"Average Edge Score   : {df['Edge Score'].mean():.2f}")

    print(f"Average Reliability  : {df['Reliability Score'].mean():.2f}")

    print(f"Average Efficiency   : {df['Efficiency Score'].mean():.2f}")

    print(f"Average Composite    : {df['Composite Score'].mean():.2f}")

    print()

    print("Recommendation Distribution")

    print(

        df["Recommendation"]

        .value_counts()

    )

    print()

    print("TOP 10 STOCKS")

    print(

        df[

            [

                "Institution Rank",

                "Stock",

                "Composite Score",

                "Recommendation"

            ]

        ].head(10)

    )

    print("="*80)

# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("="*80)

    logger.info(

        "Institutional Stock Analytics Engine v3.0"

    )

    logger.info("="*80)

    # -------------------------------------------------------
    # PART 1
    # -------------------------------------------------------

    df = prepare_data()

    # -------------------------------------------------------
    # PART 2
    # -------------------------------------------------------

    df = calculate_metrics(df)

    metrics_preview(df)

    # -------------------------------------------------------
    # PART 3
    # -------------------------------------------------------

    df = build_scorecard(df)

    score_preview(df)

    # -------------------------------------------------------
    # PART 4
    # -------------------------------------------------------

    export_report(df)

    print_summary(df)

    logger.info("="*80)

    logger.info(

        "PROCESS COMPLETED SUCCESSFULLY"

    )

    logger.info("="*80)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()