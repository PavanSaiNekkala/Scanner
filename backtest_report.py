"""
====================================================================
Strategy Evaluation Engine v5.0
====================================================================

PART 1 : DATA PREPARATION ENGINE

Author  : Pavan Sai
Version : 5.0
"""

# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path
import logging
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {

    "INPUT_FILE": "Input_backtest_WF_ATR_FT.csv",

    "OUTPUT_FILE": "Output_backtest_WF_ATR_FT_Report.xlsx",

    "ROUND": 2

}

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger("StrategyEvaluation")

# ============================================================
# REQUIRED COLUMNS
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
# LOAD DATA
# ============================================================

def load_data():

    logger.info("Loading Input File...")

    file = Path(CONFIG["INPUT_FILE"])

    if not file.exists():

        raise FileNotFoundError(

            f"{CONFIG['INPUT_FILE']} not found."

        )

    df = pd.read_csv(file)

    logger.info(

        f"Rows Loaded : {len(df):,}"

    )

    logger.info(

        f"Columns : {len(df.columns)}"

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

            f"Missing Columns:\n{missing}"

        )

    logger.info(

        "Column Validation Passed."

    )

# ============================================================
# CONVERT DATA TYPES
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

    duplicates = before - len(df)

    logger.info(

        f"Duplicates Removed : {duplicates}"

    )

    mandatory = [

        "Stock",

        "Trades",

        "Win%",

        "Expectancy%",

        "Avg win%",

        "Avg loss%",

        "Years"

    ]

    df = df.dropna(

        subset=mandatory

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

    logger.info(

        f"Rows Remaining : {len(df):,}"

    )

    return df

# ============================================================
# VALIDATE VALUES
# ============================================================

def validate_values(df):

    logger.info(

        "Running Data Validation..."

    )

    if (df["Trades"] <= 0).any():

        logger.warning(

            "Trades <= 0 detected."

        )

    if (df["Years"] <= 0).any():

        logger.warning(

            "Years <= 0 detected."

        )

    if (df["Avg days"] <= 0).any():

        logger.warning(

            "Avg Days <= 0 detected."

        )

    if (

        (df["Win%"] < 0)

        |

        (df["Win%"] > 100)

    ).any():

        logger.warning(

            "Win% outside 0-100."

        )

    if (

        (df["Target %"] +

         df["Trail %"] +

         df["Stop %"] +

         df["Time %"])

        > 100.5

    ).any():

        logger.warning(

            "Exit Percentages exceed 100%."

        )

    if (

        (df["Target #"] +

         df["Trail #"] +

         df["Stop #"] +

         df["Time #"])

        >

        df["Trades"]

    ).any():

        logger.warning(

            "Exit Counts exceed Trades."

        )

    logger.info(

        "Validation Completed."

    )

    return df

# ============================================================
# DATA SUMMARY
# ============================================================

def input_summary(df):

    print()

    print("=" * 80)

    print("INPUT DATA SUMMARY")

    print("=" * 80)

    print(f"Strategies           : {len(df):,}")

    print(f"Backtest From        : {df['BT from'].min().date()}")

    print(f"Backtest To          : {df['BT to'].max().date()}")

    print(f"Average Trades       : {df['Trades'].mean():.2f}")

    print(f"Average Win %        : {df['Win%'].mean():.2f}")

    print(f"Average Expectancy % : {df['Expectancy%'].mean():.2f}")

    print(f"Average Holding Days : {df['Avg days'].mean():.2f}")

    print("=" * 80)

# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data():

    logger.info("=" * 80)

    logger.info("PART 1 : DATA PREPARATION")

    logger.info("=" * 80)

    df = load_data()

    validate_columns(df)

    df = convert_datatypes(df)

    df = clean_data(df)

    df = validate_values(df)

    input_summary(df)

    logger.info("Data Preparation Completed.")

    return df

# ============================================================
# PART 2 : METRICS ENGINE
# ============================================================

logger.info("Loading Metrics Engine...")

# ============================================================
# SAFE DIVIDE
# ============================================================

def safe_divide(a, b):

    result = np.divide(
        a,
        b,
        out=np.full_like(np.asarray(a, dtype=float), np.nan, dtype=float),
        where=np.asarray(b) != 0
    )

    return pd.Series(result, index=a.index if hasattr(a, "index") else None)

# ============================================================
# CALCULATE METRICS
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
    # 2. REWARD RISK
    # --------------------------------------------------------

    rr = safe_divide(df["Avg win%"], df["Avg loss%"])

    df["Reward Risk"] = (
        rr.replace([np.inf, -np.inf], np.nan)
          .clip(upper=10)
    )

    # --------------------------------------------------------
    # 3. PROFIT FACTOR
    # --------------------------------------------------------

    gross_profit = (

        (df["Win%"] / 100)

        *

        df["Avg win%"]

    )

    gross_loss = (

        (df["Loss %"] / 100)

        *

        df["Avg loss%"]

    )

    pf = safe_divide(gross_profit, gross_loss)

    pf = (
        pf.replace([np.inf, -np.inf], np.nan)
          .clip(upper=20)
    )

    df["Profit Factor"] = pf

    # --------------------------------------------------------
    # 4. ANNUALIZED EXPECTANCY
    # --------------------------------------------------------

    df["Annualized Expectancy"] = safe_divide(

        df["Expectancy%"] * 365,

        df["Avg days"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 5. EXPECTED RETURN
    # --------------------------------------------------------

    df["Expected Return"] = (

        gross_profit -

        gross_loss

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 6. TRADES / YEAR
    # --------------------------------------------------------

    df["Trades / Year"] = safe_divide(

        df["Trades"],

        df["Years"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 7. TRADE CONFIDENCE
    # --------------------------------------------------------

    df["Trade Confidence"] = (

        df["Trades"]

        *

        df["Win%"]

        / 100

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 8. HOLDING EFFICIENCY
    # --------------------------------------------------------

    df["Holding Efficiency"] = safe_divide(

        df["Expectancy%"],

        df["Avg days"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 9. WINNING EXIT %
    # --------------------------------------------------------

    df["Winning Exit %"] = (

        df["Target %"]

        +

        df["Trail %"]

        +

        df["Time-win"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 10. LOSING EXIT %
    # --------------------------------------------------------

    df["Losing Exit %"] = (

        df["Stop %"]

        +

        df["Time-loss"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 11. EXIT EDGE
    # --------------------------------------------------------

    df["Exit Edge"] = (

        df["Winning Exit %"]

        -

        df["Losing Exit %"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 12. TARGET RATIO
    # --------------------------------------------------------

    df["Target Ratio"] = safe_divide(

        df["Target #"],

        df["Trades"]

    ).mul(100).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 13. TRAIL RATIO
    # --------------------------------------------------------

    df["Trail Ratio"] = safe_divide(

        df["Trail #"],

        df["Trades"]

    ).mul(100).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 14. STOP RATIO
    # --------------------------------------------------------

    df["Stop Ratio"] = safe_divide(

        df["Stop #"],

        df["Trades"]

    ).mul(100).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 15. TIME EXIT RATIO
    # --------------------------------------------------------

    df["Time Exit Ratio"] = safe_divide(

        df["Time #"],

        df["Trades"]

    ).mul(100).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # 16. OPPORTUNITY SCORE
    # --------------------------------------------------------

    df["Opportunity Score"] = safe_divide(
        df["Signals today"] * df["RS%"],
        np.log1p(df["Rank"])
    ).round(CONFIG["ROUND"])

    logger.info("Derived Metrics Completed.")

    return df

# ============================================================
# METRICS PREVIEW
# ============================================================

def metrics_preview(df):

    print()

    print("=" * 120)

    print("DERIVED METRICS")

    print("=" * 120)

    print(

        df[

            [

                "Stock",

                "Expectancy%",

                "Profit Factor",

                "Reward Risk",

                "Annualized Expectancy",

                "Expected Return",

                "Trades / Year",

                "Holding Efficiency",

                "Exit Edge",

                "Opportunity Score"

            ]

        ].head(20)

    )

    print("=" * 120)

# ============================================================
# PART 3 : SCORING & RANKING ENGINE
# ============================================================

logger.info("Loading Scoring Engine...")


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(series, higher_is_better=True):

    s = series.astype(float)

    lower = s.quantile(0.05)

    upper = s.quantile(0.95)

    s = s.clip(lower,upper)

    minimum = s.min()

    maximum = s.max()

    if pd.isna(minimum) or pd.isna(maximum):

        return pd.Series(
            50,
            index=s.index,
            dtype=float
        )

    if maximum == minimum:

        return pd.Series(
            50,
            index=s.index,
            dtype=float
        )

    score = (

        (s - minimum)

        /

        (maximum - minimum)

    ) * 100

    if not higher_is_better:

        score = 100 - score

    return score.fillna(50).round(CONFIG["ROUND"])

# ============================================================
# PERFORMANCE SCORE
# ============================================================

def performance_score(df):

    score = (

        normalize(df["Expectancy%"]) * 0.35 +

        normalize(df["Profit Factor"]) * 0.30 +

        normalize(df["Reward Risk"]) * 0.20 +

        normalize(df["Annualized Expectancy"]) * 0.15

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# RELIABILITY SCORE
# ============================================================

def reliability_score(df):

    score = (

        normalize(df["Trades"]) * 0.30 +

        normalize(df["Years"]) * 0.20 +

        normalize(df["Trade Confidence"]) * 0.30 +

        normalize(df["Win%"]) * 0.20

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# EXECUTION SCORE
# ============================================================

def execution_score(df):

    score = (

        normalize(df["Holding Efficiency"]) * 0.30 +

        normalize(df["Exit Edge"]) * 0.30 +

        normalize(df["Target Ratio"]) * 0.20 +

        normalize(df["Stop Ratio"], False) * 0.20

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# OPPORTUNITY SCORE
# ============================================================

def opportunity_score(df):

    score = (

        normalize(df["Signals today"]) * 0.30 +

        normalize(df["RS%"]) * 0.30 +

        normalize(df["Opportunity Score"]) * 0.40

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# OVERALL SCORE
# ============================================================

def overall_score(df):

    score = (

        df["Performance Score"] * 0.40 +

        df["Reliability Score"] * 0.25 +

        df["Execution Score"] * 0.20 +

        df["Opportunity Score"] * 0.15

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# RECOMMENDATION
# ============================================================

def recommendation(score):

    if score >= 90:

        return "DEPLOY"

    elif score >= 80:

        return "STRONG BUY"

    elif score >= 70:

        return "BUY"

    elif score >= 60:

        return "WATCH"

    return "REJECT"

# ============================================================
# BUILD SCORECARD
# ============================================================

def build_scorecard(df):

    logger.info("Building Strategy Scorecard...")

    df["Performance Score"] = performance_score(df)

    df["Reliability Score"] = reliability_score(df)

    df["Execution Score"] = execution_score(df)

    df["Opportunity Score"] = opportunity_score(df)

    df["Overall Score"] = overall_score(df)

    df = df.sort_values(

        by=[

            "Overall Score",

            "Performance Score",

            "Reliability Score",

            "Execution Score"

        ],

        ascending=False

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

    df["Strategy Rank"] = (

        df.index + 1

    )

    df["Recommendation"] = (

        df["Overall Score"]

        .apply(recommendation)

    )

    logger.info("Scoring Completed.")

    return df

# ============================================================
# SCORE PREVIEW
# ============================================================

def score_preview(df):

    print()

    print("=" * 110)

    print("STRATEGY SCORECARD")

    print("=" * 110)

    print(

        df[

            [

                "Strategy Rank",

                "Stock",

                "Performance Score",

                "Reliability Score",

                "Execution Score",

                "Opportunity Score",

                "Overall Score",

                "Recommendation"

            ]

        ].head(20)

    )

    print("=" * 110)

# ============================================================
# PART 4 : REPORT GENERATOR
# ============================================================

logger.info("Loading Report Generator...")

# ============================================================
# DASHBOARD
# ============================================================

def build_dashboard(df):

    dashboard = df[

        [

            "Strategy Rank",

            "Stock",

            "Overall Score",

            "Recommendation",

            "Performance Score",

            "Reliability Score",

            "Execution Score",

            "Opportunity Score"

        ]

    ].copy()

    return dashboard

# ============================================================
# METRICS SHEET
# ============================================================

def build_metrics_sheet(df):

    metrics = df[

        [

            "Stock",

            "Expectancy%",

            "Annualized Expectancy",

            "Profit Factor",

            "Reward Risk",

            "Expected Return",

            "Trades",

            "Trades / Year",

            "Trade Confidence",

            "Holding Efficiency",

            "Winning Exit %",

            "Losing Exit %",

            "Exit Edge",

            "Target Ratio",

            "Trail Ratio",

            "Stop Ratio",

            "Time Exit Ratio",

            "Opportunity Score"

        ]

    ].copy()

    return metrics

# ============================================================
# SCORES SHEET
# ============================================================

def build_scores_sheet(df):

    scores = df[

        [

            "Stock",

            "Performance Score",

            "Reliability Score",

            "Execution Score",

            "Opportunity Score",

            "Overall Score"

        ]

    ].copy()

    return scores

# ============================================================
# SUMMARY SHEET
# ============================================================

def build_summary(df):

    summary = pd.DataFrame({

        "Metric":[

            "Strategies",

            "Average Overall Score",

            "Highest Score",

            "Lowest Score",

            "Average Performance",

            "Average Reliability",

            "Average Execution",

            "Average Opportunity"

        ],

        "Value":[

            len(df),

            round(df["Overall Score"].mean(),2),

            round(df["Overall Score"].max(),2),

            round(df["Overall Score"].min(),2),

            round(df["Performance Score"].mean(),2),

            round(df["Reliability Score"].mean(),2),

            round(df["Execution Score"].mean(),2),

            round(df["Opportunity Score"].mean(),2)

        ]

    })

    return summary

# ============================================================
# EXPORT
# ============================================================

def export_report(df):

    logger.info("Generating Excel Report...")

    dashboard = build_dashboard(df)

    metrics = build_metrics_sheet(df)

    scores = build_scores_sheet(df)

    summary = build_summary(df)

    with pd.ExcelWriter(

        CONFIG["OUTPUT_FILE"],

        engine="openpyxl"

    ) as writer:

        dashboard.to_excel(

            writer,

            sheet_name="Dashboard",

            index=False

        )

        metrics.to_excel(

            writer,

            sheet_name="Metrics",

            index=False

        )

        scores.to_excel(

            writer,

            sheet_name="Scores",

            index=False

        )

        summary.to_excel(

            writer,

            sheet_name="Summary",

            index=False

        )

        df.to_excel(

            writer,

            sheet_name="Raw Data",

            index=False

        )

    logger.info(

        f"Workbook Saved : {CONFIG['OUTPUT_FILE']}"

    )

# ============================================================
# PREVIEW
# ============================================================

def report_preview(df):

    print()

    print("="*110)

    print("TOP STRATEGIES")

    print("="*110)

    print(

        df[

            [

                "Strategy Rank",

                "Stock",

                "Overall Score",

                "Recommendation"

            ]

        ].head(20)

    )

    print("="*110)

# ============================================================
# FINAL SUMMARY
# ============================================================

def final_summary(df):

    print()

    print("="*80)

    print("FINAL SUMMARY")

    print("="*80)

    print(f"Strategies Evaluated : {len(df)}")

    print(f"Average Score        : {df['Overall Score'].mean():.2f}")

    print(f"Highest Score        : {df['Overall Score'].max():.2f}")

    print(f"Lowest Score         : {df['Overall Score'].min():.2f}")

    print()

    print("Recommendation Distribution")

    print(

        df["Recommendation"]

        .value_counts()

    )

    print("="*80)

# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("="*80)

    logger.info("Strategy Evaluation Engine v5.0")

    logger.info("="*80)

    # -----------------------------------------
    # Part 1
    # -----------------------------------------

    df = prepare_data()

    # -----------------------------------------
    # Part 2
    # -----------------------------------------

    df = calculate_metrics(df)

    metrics_preview(df)

    # -----------------------------------------
    # Part 3
    # -----------------------------------------

    df = build_scorecard(df)

    score_preview(df)

    # -----------------------------------------
    # Part 4
    # -----------------------------------------

    export_report(df)

    report_preview(df)

    final_summary(df)

    logger.info("="*80)

    logger.info("PROCESS COMPLETED SUCCESSFULLY")

    logger.info("="*80)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()