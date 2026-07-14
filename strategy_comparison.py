"""
====================================================================
Institutional Strategy Comparison Engine
Part 1 : Configuration, Loader & Validation
====================================================================

Input  : Multiple Strategy CSV Files
Output : Strategy_Comparison_Report.csv

Author : Pavan Sai
Version: 2.0
"""

import os
import glob
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

    "INPUT_FOLDER": ".",

    "FILE_PATTERN": "Output*.csv",

    "OUTPUT_FILE": "Strategy_Comparison_Report.csv",

    "ROUND": 2,

    "MIN_TRADES": 100,

    "MIN_EXPECTANCY": 0.50,

    "MIN_PROFIT_FACTOR": 1.20

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
# FIND CSV FILES
# ============================================================

def find_strategy_files():

    logger.info("Searching strategy files...")

    files = glob.glob(

        os.path.join(

            CONFIG["INPUT_FOLDER"],

            CONFIG["FILE_PATTERN"]

        )

    )

    files = [

        f for f in files

        if Path(f).name != CONFIG["OUTPUT_FILE"]

    ]

    if len(files) == 0:

        raise FileNotFoundError(

            "No strategy CSV files found."

        )

    logger.info(f"Strategies Found : {len(files)}")

    return sorted(files)

# ============================================================
# LOAD ONE STRATEGY
# ============================================================

def load_strategy(file):

    logger.info(f"Loading : {Path(file).name}")

    df = pd.read_csv(file)

    strategy = Path(file).stem

    df["Strategy"] = strategy

    return df

# ============================================================
# VALIDATE
# ============================================================

def validate_columns(df, filename):

    missing = [

        col

        for col in REQUIRED_COLUMNS

        if col not in df.columns

    ]

    if missing:

        raise ValueError(

            f"{filename}\nMissing Columns:\n{missing}"

        )

# ============================================================
# CLEAN DATA
# ============================================================

def clean_dataframe(df):

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

    df = df.drop_duplicates()

    df = df.dropna(

        subset=[

            "Stock",

            "Trades",

            "Expectancy%"

        ]

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

    return df

# ============================================================
# LOAD ALL STRATEGIES
# ============================================================

def load_all_strategies():

    files = find_strategy_files()

    frames = []

    for file in files:

        df = load_strategy(file)

        validate_columns(df, file)

        df = clean_dataframe(df)

        frames.append(df)

    combined = pd.concat(

        frames,

        ignore_index=True

    )

    logger.info("=" * 60)

    logger.info(

        f"Total Strategies : {combined['Strategy'].nunique()}"

    )

    logger.info(

        f"Total Stocks : {len(combined)}"

    )

    logger.info("=" * 60)

    return combined

# ============================================================
# PERCENTILE NORMALIZATION
# ============================================================

def normalize(series, reverse=False):

    score = series.rank(

        method="average",

        pct=True

    ) * 100

    if reverse:

        score = 100 - score

    return score.round(CONFIG["ROUND"])

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
# PART 2 : CORE METRICS ENGINE
# ============================================================

logger.info("Loading Core Metrics Engine...")

# ============================================================
# CALCULATE METRICS
# ============================================================

def calculate_metrics(df):

    logger.info("Calculating Strategy Metrics...")

    # --------------------------------------------------------
    # Basic Performance
    # --------------------------------------------------------

    df["Loss %"] = (
        100 - df["Win%"]
    ).round(CONFIG["ROUND"])

    df["Reward Risk"] = safe_divide(

        df["Avg win%"],

        df["Avg loss%"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # Profit Factor (Best Possible Approximation)
    # --------------------------------------------------------

    gross_profit = (

        df["Avg win%"]

        *

        (

            df["Target #"]

            +

            df["Trail #"]

        )

    )

    gross_loss = (

        df["Avg loss%"]

        *

        df["Stop #"]

    )

    df["Profit Factor"] = safe_divide(

        gross_profit,

        gross_loss

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # Reliability
    # --------------------------------------------------------

    df["Trades / Year"] = safe_divide(

        df["Trades"],

        df["Years"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # Efficiency
    # --------------------------------------------------------

    df["Holding Efficiency"] = safe_divide(

        df["Expectancy%"],

        df["Avg days"]

    ).round(CONFIG["ROUND"])

    df["Profit Velocity"] = (

        df["Exp/DAY%"]

        *

        df["Trades"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # Exit Statistics
    # --------------------------------------------------------

    df["Winning Exit %"] = (

        df["Target %"]

        +

        df["Trail %"]

        +

        df["Time-win"]

    ).round(CONFIG["ROUND"])

    df["Losing Exit %"] = (

        df["Stop %"]

        +

        df["Time-loss"]

    ).round(CONFIG["ROUND"])

    # --------------------------------------------------------
    # Exit Quality
    # --------------------------------------------------------

    difference = (

        df["Winning Exit %"]

        -

        df["Losing Exit %"]

    )

    df["Exit Quality"] = np.select(

        [

            difference >= 20,

            difference >= 10,

            difference >= 0

        ],

        [

            "Excellent",

            "Good",

            "Average"

        ],

        default="Poor"

    )

    logger.info("Metrics Completed.")

    return df

# ============================================================
# STRATEGY SUMMARY
# ============================================================

def build_strategy_summary(df):

    logger.info("Building Strategy Summary...")

    summary = (

        df.groupby("Strategy")

        .agg(

            Stocks=(

                "Stock",

                "count"

            ),

            Median_Expectancy=(

                "Expectancy%",

                "median"

            ),

            Median_PF=(

                "Profit Factor",

                "median"

            ),

            Median_RR=(

                "Reward Risk",

                "median"

            ),

            Avg_Trades=(

                "Trades",

                "mean"

            ),

            Avg_Years=(

                "Years",

                "mean"

            ),

            Avg_Exp_Day=(

                "Exp/DAY%",

                "mean"

            ),

            Avg_Holding_Eff=(

                "Holding Efficiency",

                "mean"

            ),

            Avg_Stop=(

                "Stop %",

                "mean"

            ),

            Avg_Losing_Exit=(

                "Losing Exit %",

                "mean"

            ),

            Avg_Target=(

                "Target %",

                "mean"

            ),

            Avg_Winning_Exit=(

                "Winning Exit %",

                "mean"

            )

        )

        .reset_index()

    )

    summary = summary.round(CONFIG["ROUND"])

    logger.info("Strategy Summary Completed.")

    return summary

# ============================================================
# QUICK SUMMARY
# ============================================================

def print_summary(summary):

    print()

    print("=" * 70)

    print("STRATEGY SUMMARY")

    print("=" * 70)

    print(

        summary[

            [

                "Strategy",

                "Stocks",

                "Median_Expectancy",

                "Median_PF",

                "Median_RR"

            ]

        ]

    )

    print("=" * 70)

# ============================================================
# PART 3 : STRATEGY SCORING ENGINE
# ============================================================

logger.info("Loading Strategy Scoring Engine...")

# ============================================================
# EDGE SCORE
# ============================================================

def calculate_edge_score(summary):

    logger.info("Calculating Edge Score...")

    score = (

        normalize(summary["Median_Expectancy"]) * 0.45 +

        normalize(summary["Median_PF"]) * 0.35 +

        normalize(summary["Median_RR"]) * 0.20

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# RELIABILITY SCORE
# ============================================================

def calculate_reliability_score(summary):

    logger.info("Calculating Reliability Score...")

    score = (

        normalize(summary["Avg_Trades"]) * 0.60 +

        normalize(summary["Avg_Years"]) * 0.40

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# EFFICIENCY SCORE
# ============================================================

def calculate_efficiency_score(summary):

    logger.info("Calculating Efficiency Score...")

    score = (

        normalize(summary["Avg_Exp_Day"]) * 0.60 +

        normalize(summary["Avg_Holding_Eff"]) * 0.40

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk_score(summary):

    logger.info("Calculating Risk Score...")

    score = (

        normalize(

            summary["Avg_Stop"],

            reverse=True

        ) * 0.60 +

        normalize(

            summary["Avg_Losing_Exit"],

            reverse=True

        ) * 0.40

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# EXECUTION SCORE
# ============================================================

def calculate_execution_score(summary):

    logger.info("Calculating Execution Score...")

    score = (

        normalize(summary["Avg_Target"]) * 0.50 +

        normalize(summary["Avg_Winning_Exit"]) * 0.50

    )

    return score.round(CONFIG["ROUND"])

# ============================================================
# BUILD SCORES
# ============================================================

def score_strategies(summary):

    logger.info("Generating Institutional Scores...")

    summary["Edge Score"] = calculate_edge_score(summary)

    summary["Reliability Score"] = calculate_reliability_score(summary)

    summary["Efficiency Score"] = calculate_efficiency_score(summary)

    summary["Risk Score"] = calculate_risk_score(summary)

    summary["Execution Score"] = calculate_execution_score(summary)

    # -------------------------------------------------------
    # PRIMARY STRATEGY SCORE
    # -------------------------------------------------------

    summary["Strategy Score"] = (

        summary["Edge Score"] * 0.40 +

        summary["Reliability Score"] * 0.25 +

        summary["Efficiency Score"] * 0.15 +

        summary["Risk Score"] * 0.10 +

        summary["Execution Score"] * 0.10

    ).round(CONFIG["ROUND"])

    logger.info("Scoring Completed.")

    return summary


# ============================================================
# PREVIEW
# ============================================================

def preview_scores(summary):

    print()

    print("="*80)

    print("INSTITUTIONAL STRATEGY SCORES")

    print("="*80)

    print(

        summary[

            [

                "Strategy",

                "Strategy Score",

                "Edge Score",

                "Reliability Score",

                "Efficiency Score",

                "Risk Score",

                "Execution Score"

            ]

        ]

    )

    print("="*80)


# ============================================================
# PART 4 : FINAL STRATEGY RANKING
# ============================================================

logger.info("Loading Final Ranking Engine...")

# ============================================================
# ROBUSTNESS SCORE
# ============================================================

def robustness_analysis(df, summary):

    logger.info("Calculating Robustness...")

    robust = (

        df.groupby("Strategy")

        .agg(

            Exp_STD=("Expectancy%", "std"),

            PF_STD=("Profit Factor", "std"),

            RR_STD=("Reward Risk", "std")

        )

        .reset_index()

    )

    robust = robust.merge(

        summary[

            [

                "Strategy",

                "Median_Expectancy",

                "Median_PF",

                "Median_RR"

            ]

        ],

        on="Strategy",

        how="left"

    )

    robust["Exp_CV"] = np.where(

        robust["Median_Expectancy"] != 0,

        robust["Exp_STD"] /

        robust["Median_Expectancy"],

        np.nan

    )

    robust["PF_CV"] = np.where(

        robust["Median_PF"] != 0,

        robust["PF_STD"] /

        robust["Median_PF"],

        np.nan

    )

    robust["RR_CV"] = np.where(

        robust["Median_RR"] != 0,

        robust["RR_STD"] /

        robust["Median_RR"],

        np.nan

    )

    robust["Robustness Score"] = (

        normalize(

            robust["Exp_CV"],

            reverse=True

        ) * 0.40 +

        normalize(

            robust["PF_CV"],

            reverse=True

        ) * 0.35 +

        normalize(

            robust["RR_CV"],

            reverse=True

        ) * 0.25

    ).round(CONFIG["ROUND"])

    summary = summary.merge(

        robust[

            [

                "Strategy",

                "Robustness Score"

            ]

        ],

        on="Strategy",

        how="left"

    )

    return summary

# ============================================================
# BREADTH SCORE
# ============================================================

def quality_statistics(df, summary):

    logger.info("Calculating Breadth Score...")

    quality = df.copy()

    quality["PF_OK"] = (
        quality["Profit Factor"] >= 1.50
    )

    quality["RR_OK"] = (
        quality["Reward Risk"] >= 2.00
    )

    quality["EXP_OK"] = (
        quality["Expectancy%"] >= 1.00
    )

    breadth = (

        quality.groupby("Strategy")

        .agg(

            Stocks=("Stock","count"),

            PF_OK=("PF_OK","sum"),

            RR_OK=("RR_OK","sum"),

            EXP_OK=("EXP_OK","sum")

        )

        .reset_index()

    )

    breadth["PF >1.5 %"] = (

        breadth["PF_OK"]

        /

        breadth["Stocks"]

        *100

    ).round(CONFIG["ROUND"])

    breadth["RR >2 %"] = (

        breadth["RR_OK"]

        /

        breadth["Stocks"]

        *100

    ).round(CONFIG["ROUND"])

    breadth["EXP >1 %"] = (

        breadth["EXP_OK"]

        /

        breadth["Stocks"]

        *100

    ).round(CONFIG["ROUND"])

    breadth["Breadth Score"] = (

        breadth["PF >1.5 %"] * 0.40 +

        breadth["RR >2 %"] * 0.30 +

        breadth["EXP >1 %"] * 0.30

    ).round(CONFIG["ROUND"])

    summary = summary.merge(

        breadth[

            [

                "Strategy",

                "Breadth Score"

            ]

        ],

        on="Strategy",

        how="left"

    )

    return summary

# ============================================================
# FINAL SCORE
# ============================================================

def final_score(summary):

    logger.info("Calculating Final Score...")

    summary["Final Score"] = (

        summary["Edge Score"] * 0.35 +

        summary["Reliability Score"] * 0.20 +

        summary["Efficiency Score"] * 0.15 +

        summary["Risk Score"] * 0.10 +

        summary["Execution Score"] * 0.10 +

        summary["Robustness Score"] * 0.05 +
 
        summary["Breadth Score"] * 0.05

    ).round(CONFIG["ROUND"])

    return summary

# ============================================================
# GRADE
# ============================================================

def strategy_grade(score):

    if score >= 90:
        return "★★★★★ Elite"

    elif score >= 80:
        return "★★★★ Excellent"

    elif score >= 70:
        return "★★★ Good"

    elif score >= 60:
        return "★★ Average"

    elif score >= 50:
        return "★ Watch"

    return "Reject"

# ============================================================
# RECOMMENDATION
# ============================================================

def recommendation(row):

    score = row["Final Score"]

    if score >= 90:
        return "DEPLOY"

    elif score >= 80:
        return "STRONG BUY"

    elif score >= 70:
        return "BUY"

    elif score >= 60:
        return "PAPER TRADE"

    elif score >= 50:
        return "WATCH"

    return "REJECT"

# ============================================================
# FINAL RANK
# ============================================================

def rank_strategies(summary):

    summary["Grade"] = summary["Final Score"].apply(

        strategy_grade

    )

    summary["Recommendation"] = summary.apply(

        recommendation,

        axis=1

    )

    summary = summary.sort_values(

        by=[

            "Final Score",

            "Edge Score",

            "Robustness Score",

            "Reliability Score"

        ],

        ascending=False

    )

    summary["Final Rank"] = np.arange(

        1,

        len(summary)+1

    )

    return summary

# ============================================================
# EXPORT
# ============================================================

def export_report(summary):

    logger.info("Exporting Report...")

    report = summary[

        [

            "Final Rank",

            "Strategy",

            "Stocks",

            "Median_Expectancy",

            "Median_PF",

            "Median_RR",

            "Avg_Trades",

            "Edge Score",

            "Reliability Score",

            "Robustness Score",

            "Breadth Score",

            "Final Score",

            "Grade",

            "Recommendation"

        ]

    ]

    report.to_csv(

        CONFIG["OUTPUT_FILE"],

        index=False

    )

    logger.info(

        f"Saved : {CONFIG['OUTPUT_FILE']}"

    )

# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("="*60)

    logger.info("Institutional Strategy Comparison Engine")

    logger.info("="*60)

    df = load_all_strategies()

    df = calculate_metrics(df)

    summary = build_strategy_summary(df)

    summary = score_strategies(summary)

    summary = robustness_analysis(df, summary)

    summary = quality_statistics(df, summary)

    summary = final_score(summary)

    summary = rank_strategies(summary)

    export_report(summary)

    print()

    print("="*60)

    print("TOP STRATEGIES")

    print("="*60)

    print(

        summary[

            [

                "Final Rank",

                "Strategy",

                "Final Score",

                "Recommendation"

            ]

        ]

    )

    print("="*60)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()