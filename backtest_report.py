"""
===============================================================
Institutional Stock Analytics Engine
Part 1 : Configuration & Data Preparation
===============================================================

Input  : Backtest.csv
Output : Institutional_Stock_Report.csv

Author : Pavan Sai
Version: 2.0
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import warnings

warnings.filterwarnings("ignore")

# ===============================================================
# CONFIGURATION
# ===============================================================

CONFIG = {

    "INPUT_FILE": "Backtest.csv",

    "OUTPUT_FILE": "Institutional_Stock_Report.csv",

    "ROUND_DECIMALS": 2

}

# ===============================================================
# LOGGING
# ===============================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)

# ===============================================================
# REQUIRED COLUMNS
# ===============================================================

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

# ===============================================================
# NUMERIC COLUMNS
# ===============================================================

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

# ===============================================================
# LOAD CSV
# ===============================================================

def load_data():

    logger.info("Loading CSV...")

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

# ===============================================================
# VALIDATE COLUMNS
# ===============================================================

def validate_columns(df):

    missing = [

        col

        for col in REQUIRED_COLUMNS

        if col not in df.columns

    ]

    if missing:

        raise Exception(

            f"Missing Columns : {missing}"

        )

    logger.info(

        "Column Validation Passed"

    )

# ===============================================================
# CONVERT DATATYPES
# ===============================================================

def convert_datatypes(df):

    logger.info(

        "Converting Datatypes..."

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

# ===============================================================
# CLEAN DATA
# ===============================================================

def clean_data(df):

    logger.info(

        "Cleaning Data..."

    )

    rows_before = len(df)

    df = df.drop_duplicates()

    logger.info(

        f"Duplicates Removed : {rows_before-len(df)}"

    )

    df = df.dropna(

        subset=[

            "Stock",

            "Trades",

            "Win%",

            "Expectancy%"

        ]

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

    return df

# ===============================================================
# BASIC VALIDATION
# ===============================================================

def validate_ranges(df):

    logger.info(

        "Validating Data..."

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

        invalid = df[col] < 0

        if invalid.any():

            logger.warning(

                f"Negative values found in {col}"

            )

    if (df["Trades"] <= 0).any():

        logger.warning(

            "Some stocks have zero trades."

        )

    return df

# ===============================================================
# DATA QUALITY SUMMARY
# ===============================================================

def data_summary(df):

    print()

    print("="*70)

    print("DATA QUALITY SUMMARY")

    print("="*70)

    print(f"Stocks                 : {len(df)}")

    print(f"Backtest From          : {df['BT from'].min().date()}")

    print(f"Backtest To            : {df['BT to'].max().date()}")

    print(f"Average Trades         : {df['Trades'].mean():.2f}")

    print(f"Average Win %          : {df['Win%'].mean():.2f}")

    print(f"Average Expectancy %   : {df['Expectancy%'].mean():.2f}")

    print(f"Average Holding Days   : {df['Avg days'].mean():.2f}")

    print("="*70)

# ===============================================================
# PREPARE DATA
# ===============================================================

def prepare_data():

    df = load_data()

    validate_columns(df)

    df = convert_datatypes(df)

    df = clean_data(df)

    df = validate_ranges(df)

    data_summary(df)

    logger.info(

        "Data Preparation Completed"

    )

    return df


# ===============================================================
# PART 2 : DERIVED METRICS ENGINE
# ===============================================================

def calculate_metrics(df):

    logger.info("Calculating Derived Metrics...")

    # -----------------------------------------------------------
    # 1. LOSS RATE
    # -----------------------------------------------------------

    df["Loss %"] = (100 - df["Win%"]).round(2)

    # -----------------------------------------------------------
    # 2. REWARD : RISK
    # -----------------------------------------------------------

    df["Reward Risk"] = np.where(

        df["Avg loss%"] > 0,

        df["Avg win%"] / df["Avg loss%"],

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 3. PROFIT FACTOR
    # Approximation from summary statistics
    # -----------------------------------------------------------

    gross_profit = df["Avg win%"] * df["Win%"]

    gross_loss = df["Avg loss%"] * df["Loss %"]

    df["Profit Factor"] = np.where(

        gross_loss > 0,

        gross_profit / gross_loss,

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 4. TRADES PER YEAR
    # -----------------------------------------------------------

    df["Trades / Year"] = np.where(

        df["Years"] > 0,

        df["Trades"] / df["Years"],

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 5. ANNUAL EXPECTANCY
    # -----------------------------------------------------------

    df["Annual Expectancy"] = (

        df["Expectancy%"] *

        df["Trades / Year"]

    ).round(2)

    # -----------------------------------------------------------
    # 6. WINNING EXIT %
    # -----------------------------------------------------------

    df["Winning Exit %"] = (

        df["Target %"] +

        df["Trail %"] +

        df["Time-win"]

    ).round(2)

    # -----------------------------------------------------------
    # 7. LOSING EXIT %
    # -----------------------------------------------------------

    df["Losing Exit %"] = (

        df["Stop %"] +

        df["Time-loss"]

    ).round(2)

    # -----------------------------------------------------------
    # 8. TARGET EFFICIENCY
    # -----------------------------------------------------------

    df["Target Efficiency"] = np.where(

        df["Trades"] > 0,

        df["Target #"] /

        df["Trades"] * 100,

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 9. TRAIL EFFICIENCY
    # -----------------------------------------------------------

    df["Trail Efficiency"] = np.where(

        df["Trades"] > 0,

        df["Trail #"] /

        df["Trades"] * 100,

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 10. STOP EFFICIENCY
    # -----------------------------------------------------------

    df["Stop Efficiency"] = np.where(

        df["Trades"] > 0,

        df["Stop #"] /

        df["Trades"] * 100,

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 11. TIME EXIT EFFICIENCY
    # -----------------------------------------------------------

    df["Time Efficiency"] = np.where(

        df["Trades"] > 0,

        df["Time #"] /

        df["Trades"] * 100,

        np.nan

    ).round(2)

    # -----------------------------------------------------------
    # 12. HOLDING EFFICIENCY
    # Expectancy generated per holding day
    # -----------------------------------------------------------

    df["Holding Efficiency"] = np.where(

        df["Avg days"] > 0,

        df["Expectancy%"] /

        df["Avg days"],

        np.nan

    ).round(3)

    # -----------------------------------------------------------
    # 13. PROFIT VELOCITY
    # Annual expectancy generated
    # -----------------------------------------------------------

    df["Profit Velocity"] = (

        df["Exp/DAY%"] *

        df["Trades"]

    ).round(2)

    # -----------------------------------------------------------
    # 14. SIGNAL DENSITY
    # -----------------------------------------------------------

    df["Signal Density"] = np.where(

        df["Trades"] > 0,

        df["Signals today"] /

        df["Trades"],

        np.nan

    ).round(3)

    # -----------------------------------------------------------
    # 15. TRADE FREQUENCY
    # -----------------------------------------------------------

    df["Trade Frequency"] = np.where(

        df["Years"] > 0,

        df["Trades"] /

        (df["Years"] * 252),

        np.nan

    ).round(3)

    # -----------------------------------------------------------
    # 16. EXIT QUALITY
    # -----------------------------------------------------------

    df["Exit Quality"] = np.where(

        df["Winning Exit %"] >

        df["Losing Exit %"],

        "Positive",

        "Negative"

    )

    # -----------------------------------------------------------
    # 17. HOLDING STYLE
    # -----------------------------------------------------------

    conditions = [

        df["Avg days"] <= 1,

        (df["Avg days"] > 1) & (df["Avg days"] <= 7),

        (df["Avg days"] > 7) & (df["Avg days"] <= 30),

        (df["Avg days"] > 30)

    ]

    choices = [

        "Intraday",

        "Swing",

        "Position",

        "Long Term"

    ]

    df["Trading Style"] = np.select(

        conditions,

        choices,

        default="Unknown"

    )

    logger.info("Derived Metrics Completed.")

    return df

# ===============================================================
# PART 3 : INSTITUTIONAL SCORING ENGINE
# ===============================================================

logger.info("Loading Scoring Engine...")

# ===============================================================
# WEIGHTAGE
# ===============================================================

WEIGHTS = {

    "Expectancy":20,

    "ProfitFactor":20,

    "RewardRisk":15,

    "WinRate":15,

    "Trades":10,

    "ExpDay":10,

    "RS":5,

    "Holding":5

}

# ===============================================================
# NORMALIZE FUNCTION
# ===============================================================

def normalize(series, reverse=False):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series([50]*len(series), index=series.index)

    score = (series-minimum)/(maximum-minimum)*100

    if reverse:
        score = 100-score

    return score.round(2)

# ===============================================================
# CONFIDENCE SCORE
# ===============================================================

def confidence_score(df):

    logger.info("Calculating Confidence Score...")

    trades = normalize(df["Trades"])

    years = normalize(df["Years"])

    expectancy = normalize(df["Expectancy%"])

    confidence = (

        trades*0.50 +

        years*0.30 +

        expectancy*0.20

    )

    return confidence.round(2)

# ===============================================================
# RISK SCORE
# ===============================================================

def risk_score(df):

    logger.info("Calculating Risk Score...")

    stop = normalize(df["Stop %"], reverse=True)

    avg_loss = normalize(df["Avg loss%"], reverse=True)

    holding = normalize(df["Avg days"], reverse=True)

    risk = (

        stop*0.40 +

        avg_loss*0.40 +

        holding*0.20

    )

    return risk.round(2)

# ===============================================================
# OPPORTUNITY SCORE
# ===============================================================

def opportunity_score(df):

    logger.info("Calculating Opportunity Score...")

    expectancy = normalize(df["Expectancy%"])

    exp_day = normalize(df["Exp/DAY%"])

    rs = normalize(df["RS%"])

    pf = normalize(df["Profit Factor"])

    score = (

        expectancy*0.40 +

        exp_day*0.30 +

        rs*0.10 +

        pf*0.20

    )

    return score.round(2)

# ===============================================================
# CONSISTENCY SCORE
# ===============================================================

def consistency_score(df):

    logger.info("Calculating Consistency Score...")

    win = normalize(df["Win%"])

    rr = normalize(df["Reward Risk"])

    pf = normalize(df["Profit Factor"])

    score = (

        win*0.40 +

        rr*0.30 +

        pf*0.30

    )

    return score.round(2)

# ===============================================================
# HOLDING SCORE
# ===============================================================

def holding_score(df):

    return normalize(df["Avg days"], reverse=True)

# ===============================================================
# COMPOSITE SCORE
# ===============================================================

def composite_score(df):

    logger.info("Calculating Composite Score...")

    score = (

        normalize(df["Expectancy%"]) * WEIGHTS["Expectancy"]

        +

        normalize(df["Profit Factor"]) * WEIGHTS["ProfitFactor"]

        +

        normalize(df["Reward Risk"]) * WEIGHTS["RewardRisk"]

        +

        normalize(df["Win%"]) * WEIGHTS["WinRate"]

        +

        normalize(df["Trades"]) * WEIGHTS["Trades"]

        +

        normalize(df["Exp/DAY%"]) * WEIGHTS["ExpDay"]

        +

        normalize(df["RS%"]) * WEIGHTS["RS"]

        +

        holding_score(df) * WEIGHTS["Holding"]

    ) / 100

    return score.round(2)

# ===============================================================
# OVERALL RATING
# ===============================================================

def overall_rating(score):

    if score >= 90:
        return "★★★★★ Elite"

    elif score >= 80:
        return "★★★★ Excellent"

    elif score >= 70:
        return "★★★ Good"

    elif score >= 60:
        return "★★ Average"

    elif score >= 50:
        return "★ Weak"

    return "Poor"

# ===============================================================
# RECOMMENDATION
# ===============================================================

def recommendation(row):

    if row["Trades"] < 100:
        return "INSUFFICIENT DATA"

    if row["Profit Factor"] < 1:
        return "REJECT"

    if row["Expectancy%"] <= 0:
        return "REJECT"

    if row["Composite Score"] >= 90:
        return "⭐⭐⭐⭐⭐ INSTITUTIONAL BUY"

    elif row["Composite Score"] >= 80:
        return "STRONG BUY"

    elif row["Composite Score"] >= 70:
        return "BUY"

    elif row["Composite Score"] >= 60:
        return "WATCH"

    elif row["Composite Score"] >= 50:
        return "AVOID"

    return "REJECT"

# ===============================================================
# BUILD SCORECARD
# ===============================================================

def build_scorecard(df):

    logger.info("Building Institutional Scorecard...")

    df["Confidence Score"] = confidence_score(df)

    df["Risk Score"] = risk_score(df)

    df["Opportunity Score"] = opportunity_score(df)

    df["Consistency Score"] = consistency_score(df)

    df["Composite Score"] = composite_score(df)

    df["Overall Rating"] = df["Composite Score"].apply(overall_rating)

    df["Recommendation"] = df.apply(
        recommendation,
        axis=1
    )

    df = df.sort_values(

        by=[

            "Composite Score",

            "Opportunity Score",

            "Confidence Score",

            "Profit Factor",

            "Expectancy%"

        ],

        ascending=False

    )

    df["Institution Rank"] = range(

        1,

        len(df)+1

    )

    logger.info("Scoring Completed.")

    return df

# ===============================================================
# PART 4 : REPORT GENERATOR
# ===============================================================

logger.info("Loading Report Generator...")

# ===============================================================
# QUALITY FLAG
# ===============================================================

def quality_flag(row):

    flags = []

    if row["Trades"] < 100:
        flags.append("Low Sample")

    if row["Profit Factor"] < 1.50:
        flags.append("Low PF")

    if row["Reward Risk"] < 1.50:
        flags.append("Low RR")

    if row["Expectancy%"] < 1:
        flags.append("Low Edge")

    if row["Stop %"] > 50:
        flags.append("High Stop Rate")

    if len(flags) == 0:
        return "PASS"

    return ", ".join(flags)

# ===============================================================
# EXIT DOMINANCE
# ===============================================================

def exit_dominance(row):

    exits = {

        "Target": row["Target %"],

        "Trail": row["Trail %"],

        "Stop": row["Stop %"],

        "Time": row["Time %"]

    }

    return max(exits, key=exits.get)

# ===============================================================
# RISK CATEGORY
# ===============================================================

def risk_category(score):

    if score >= 80:
        return "Low Risk"

    elif score >= 60:
        return "Medium Risk"

    elif score >= 40:
        return "High Risk"

    return "Very High Risk"

# ===============================================================
# FINALIZE REPORT
# ===============================================================

def finalize_report(df):

    logger.info("Finalizing Report...")

    df["Quality Flag"] = df.apply(
        quality_flag,
        axis=1
    )

    df["Exit Dominance"] = df.apply(
        exit_dominance,
        axis=1
    )

    df["Risk Category"] = df["Risk Score"].apply(
        risk_category
    )

    # Final sort

    df = df.sort_values(

        by=[

            "Composite Score",

            "Confidence Score",

            "Opportunity Score",

            "Profit Factor",

            "Expectancy%",

            "Win%"

        ],

        ascending=False

    )

    df["Institution Rank"] = range(
        1,
        len(df)+1
    )

    return df

# ===============================================================
# SUMMARY
# ===============================================================

def print_summary(df):

    print()

    print("="*70)

    print("INSTITUTIONAL ANALYTICS SUMMARY")

    print("="*70)

    print(f"Stocks Analysed          : {len(df)}")

    print(f"Average Composite Score  : {df['Composite Score'].mean():.2f}")

    print(f"Average Confidence       : {df['Confidence Score'].mean():.2f}")

    print(f"Average Risk Score       : {df['Risk Score'].mean():.2f}")

    print(f"Average Opportunity      : {df['Opportunity Score'].mean():.2f}")

    print()

    print("Recommendation Distribution")

    print(df["Recommendation"].value_counts())

    print()

    print("Top 10 Stocks")

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

    print("="*70)

# ===============================================================
# EXPORT
# ===============================================================

def export_report(df):

    logger.info("Exporting Report...")

    df.to_csv(

        CONFIG["OUTPUT_FILE"],

        index=False

    )

    logger.info(

        f"Saved : {CONFIG['OUTPUT_FILE']}"

    )

# ===============================================================
# MAIN
# ===============================================================

def main():

    logger.info("="*60)

    logger.info("Institutional Stock Analytics Engine")

    logger.info("="*60)

    # Part 1

    df = prepare_data()

    # Part 2

    df = calculate_metrics(df)

    # Part 3

    df = build_scorecard(df)

    # Part 4

    df = finalize_report(df)

    print_summary(df)

    export_report(df)

    logger.info("="*60)

    logger.info("PROCESS COMPLETED SUCCESSFULLY")

    logger.info("="*60)

# ===============================================================
# START
# ===============================================================

if __name__ == "__main__":

    main()