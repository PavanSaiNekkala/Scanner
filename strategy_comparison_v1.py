"""
====================================================================
Institutional Strategy Universe Evaluation Engine (ISUE) v3.0
====================================================================

Purpose
-------
Identify the strategy that produces the BEST STOCK UNIVERSE.

Author  : Pavan Sai
Version : 3.0
"""

# ================================================================
# IMPORTS
# ================================================================

from pathlib import Path
import glob
import logging
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ================================================================
# CONFIGURATION
# ================================================================

CONFIG = {
    "INPUT_FOLDER": ".",
    "FILE_PATTERN": "Output*.csv",
    "OUTPUT_FILE": "Strategy_Universe_Report.xlsx",
    "ROUND": 2,
    "TOP_N": [10, 20, 50],
    "MIN_DEPLOY_SCORE": 80,
    "MIN_BUY_SCORE": 70,
}

# ================================================================
# LOGGING
# ================================================================

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ISUE_V3")

# ================================================================
# INPUT SCHEMA
# ================================================================

REQUIRED_COLUMNS = [
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
    "Recommendation",
]

NUMERIC_COLUMNS = [
    "Institution Rank",
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
]

# ================================================================
# UTILITY FUNCTIONS
# ================================================================


def safe_divide(a, b):
    result = a.div(b)

    result = result.replace([np.inf, -np.inf], np.nan)

    return result


def percentage(series):
    return (series.mean() * 100).round(CONFIG["ROUND"])


# ================================================================
# FILE DISCOVERY
# ================================================================


def find_strategy_files():
    logger.info("Searching strategy files...")

    files = sorted(
        glob.glob(str(Path(CONFIG["INPUT_FOLDER"]) / CONFIG["FILE_PATTERN"]))
    )

    files = [file for file in files if Path(file).name != CONFIG["OUTPUT_FILE"]]

    if not files:
        raise FileNotFoundError("No strategy files found.")

    logger.info(f"Strategies Found : {len(files)}")

    return files


# ================================================================
# VALIDATION
# ================================================================


def validate_dataframe(df, filename):
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing:
        raise ValueError(f"\n{filename}\nMissing Columns:\n{missing}")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df["Stock"].duplicated().any():
        logger.warning(f"{filename} contains duplicate stocks.")

    if df["Composite Score"].isna().any():
        logger.warning(f"{filename} contains missing Composite Scores.")

    return df


# ================================================================
# LOAD STRATEGY
# ================================================================


def load_strategy(file):
    logger.info(f"Loading : {Path(file).name}")

    df = pd.read_csv(file)

    df = validate_dataframe(df, Path(file).name)

    df = df.drop_duplicates()

    df = df.sort_values("Institution Rank")

    df.reset_index(drop=True, inplace=True)

    df["Strategy"] = Path(file).stem

    return df


# ================================================================
# LOAD ALL STRATEGIES
# ================================================================


def load_universe():
    files = find_strategy_files()

    frames = []

    for file in files:
        frames.append(load_strategy(file))

    universe = pd.concat(frames, ignore_index=True)

    logger.info("=" * 70)

    logger.info(f"Strategies : {universe['Strategy'].nunique()}")

    logger.info(f"Stocks : {len(universe)}")

    logger.info("=" * 70)

    return universe


# ================================================================
# DATA SUMMARY
# ================================================================


def print_input_summary(df):
    print()

    print("=" * 80)

    print("INPUT DATA SUMMARY")

    print("=" * 80)

    print(f"Strategies Loaded : {df['Strategy'].nunique()}")

    print(f"Total Stocks : {len(df)}")

    print()

    print(df.groupby("Strategy").size().rename("Stocks").sort_values(ascending=False))

    print("=" * 80)


# ================================================================
# PART 2 : UNIVERSE ANALYTICS ENGINE
# ================================================================

logger.info("Loading Universe Analytics Engine...")

# ================================================================
# ANALYZE ONE STRATEGY
# ================================================================


def analyze_universe(strategy_df):
    composite = strategy_df["Composite Score"]

    signal = strategy_df["Signal Quality"]

    analytics = {
        # =====================================================
        # GENERAL
        # =====================================================
        "Strategy": strategy_df["Strategy"].iloc[0],
        "Total Stocks": len(strategy_df),
        # =====================================================
        # UNIVERSE QUALITY
        # =====================================================
        "Mean Composite": composite.mean(),
        "Median Composite": composite.median(),
        "Top10 Composite": composite.nlargest(CONFIG["TOP_N"][0]).mean(),
        "Top20 Composite": composite.nlargest(CONFIG["TOP_N"][1]).mean(),
        "Top50 Composite": composite.nlargest(CONFIG["TOP_N"][2]).mean(),
        "Average Signal": signal.mean(),
        # =====================================================
        # INVESTABILITY
        # =====================================================
        "Deploy %": percentage(strategy_df["Recommendation"] == "DEPLOY"),
        "Strong Buy %": percentage(strategy_df["Recommendation"] == "STRONG BUY"),
        "Buy %": percentage(strategy_df["Recommendation"] == "BUY"),
        "Watch %": percentage(strategy_df["Recommendation"] == "WATCH"),
        "Reject %": percentage(strategy_df["Recommendation"] == "REJECT"),
        # =====================================================
        # CONSISTENCY
        # =====================================================
        "Std Composite": composite.std(),
        "IQR": composite.quantile(0.75) - composite.quantile(0.25),
        "CV": composite.std() / composite.mean() if composite.mean() != 0 else np.nan,
        "MAD": (composite - composite.median()).abs().median(),
        # =====================================================
        # CONCENTRATION
        # =====================================================
        "Top10 Contribution": composite.nlargest(CONFIG["TOP_N"][0]).sum()
        / composite.sum(),
        "Top20 Contribution": composite.nlargest(CONFIG["TOP_N"][1]).sum()
        / composite.sum(),
        # =====================================================
        # COVERAGE
        # =====================================================
        "Investable Stocks": strategy_df[
            strategy_df["Recommendation"].isin(["DEPLOY", "STRONG BUY", "BUY"])
        ].shape[0],
        "Average Trades": strategy_df["Trades / Year"].mean(),
    }

    return analytics


# ================================================================
# BUILD UNIVERSE ANALYTICS
# ================================================================


def build_universe_analytics(universe):
    logger.info("Building Universe Analytics...")

    analytics = []

    for _, strategy_df in universe.groupby("Strategy"):
        analytics.append(analyze_universe(strategy_df))

    analytics = pd.DataFrame(analytics)

    analytics = analytics.round(CONFIG["ROUND"])

    logger.info("Universe Analytics Completed.")

    return analytics


# ================================================================
# ANALYTICS PREVIEW
# ================================================================


def preview_universe(analytics):
    print()

    print("=" * 100)

    print("UNIVERSE ANALYTICS")

    print("=" * 100)

    print(
        analytics[
            [
                "Strategy",
                "Mean Composite",
                "Median Composite",
                "Deploy %",
                "Investable Stocks",
                "Average Signal",
            ]
        ]
    )

    print("=" * 100)


# ================================================================
# PART 3 : QUALIFICATION ENGINE
# ================================================================

logger.info("Loading Qualification Engine...")

# ================================================================
# CONFIGURABLE QUALIFICATION RULES
# ================================================================

RULES = {
    "MIN_MEDIAN_COMPOSITE": 80,
    "MIN_DEPLOY_PERCENT": 15,
    "MIN_INVESTABLE_STOCKS": 25,
    "MAX_CV": 0.25,
    "MIN_TOP20_COMPOSITE": 85,
}

# ================================================================
# QUALIFY ONE STRATEGY
# ================================================================


def qualify_strategy(row):
    reasons = []

    qualified = True

    # ------------------------------------------------------------
    # Median Composite
    # ------------------------------------------------------------

    if row["Median Composite"] < RULES["MIN_MEDIAN_COMPOSITE"]:
        qualified = False

        reasons.append("Weak Universe Quality")

    # ------------------------------------------------------------
    # Deploy %
    # ------------------------------------------------------------

    if row["Deploy %"] < RULES["MIN_DEPLOY_PERCENT"]:
        qualified = False

        reasons.append("Low Deployability")

    # ------------------------------------------------------------
    # Investable Stocks
    # ------------------------------------------------------------

    if row["Investable Stocks"] < RULES["MIN_INVESTABLE_STOCKS"]:
        qualified = False

        reasons.append("Insufficient Opportunities")

    # ------------------------------------------------------------
    # Consistency
    # ------------------------------------------------------------

    if row["CV"] > RULES["MAX_CV"]:
        qualified = False

        reasons.append("High Dispersion")

    # ------------------------------------------------------------
    # Top20 Quality
    # ------------------------------------------------------------

    if row["Top20 Composite"] < RULES["MIN_TOP20_COMPOSITE"]:
        qualified = False

        reasons.append("Weak High Conviction Ideas")

    return pd.Series(
        {
            "Qualified": qualified,
            "Qualification": "PASS" if qualified else "FAIL",
            "Reason": "; ".join(reasons) if reasons else "Qualified",
        }
    )


# ================================================================
# APPLY QUALIFICATION
# ================================================================


def qualification_engine(analytics):
    logger.info("Applying Qualification Rules...")

    result = analytics.apply(qualify_strategy, axis=1)

    analytics = pd.concat([analytics, result], axis=1)

    logger.info(f"Qualified Strategies : {analytics['Qualified'].sum()}")

    return analytics


# ================================================================
# PREVIEW
# ================================================================


def preview_qualification(df):
    print()

    print("=" * 100)

    print("QUALIFICATION RESULTS")

    print("=" * 100)

    print(df[["Strategy", "Qualification", "Reason"]])

    print("=" * 100)


# ================================================================
# PART 4 : UNIVERSE RANKING ENGINE
# ================================================================

logger.info("Loading Universe Ranking Engine...")

# ================================================================
# RANK STRATEGIES
# ================================================================


def rank_universes(analytics):
    logger.info("Ranking Universes...")

    ranking = analytics.copy()

    ranking = ranking.sort_values(
        by=[
            "Median Composite",
            "Deploy %",
            "CV",
            "Top20 Composite",
            "Investable Stocks",
            "Average Signal",
        ],
        ascending=[False, False, True, False, False, False],
    )

    ranking.reset_index(drop=True, inplace=True)

    ranking["Universe Rank"] = ranking.index + 1

    return ranking


# ================================================================
# BEST STRATEGY
# ================================================================


def best_universe(ranking):
    best = ranking.iloc[0]

    logger.info(f"Best Strategy : {best['Strategy']}")

    logger.info(f"Median Composite : {best['Median Composite']:.2f}")

    logger.info(f"Deploy % : {best['Deploy %']:.2f}")

    return best


# ================================================================
# TOP STRATEGIES
# ================================================================


def preview_ranking(ranking):
    print()

    print("=" * 100)

    print("BEST STOCK UNIVERSES")

    print("=" * 100)

    print(
        ranking[
            [
                "Universe Rank",
                "Strategy",
                "Median Composite",
                "Deploy %",
                "CV",
                "Top20 Composite",
                "Investable Stocks",
            ]
        ]
    )

    print("=" * 100)


# ================================================================
# PART 5 : UNIVERSE DIAGNOSTICS ENGINE
# ================================================================

logger.info("Loading Universe Diagnostics Engine...")

# ================================================================
# QUALITY RATING
# ================================================================


def quality_rating(value):
    if value >= 90:
        return "Excellent"

    elif value >= 85:
        return "Very Good"

    elif value >= 80:
        return "Good"

    elif value >= 70:
        return "Average"

    return "Poor"


# ================================================================
# DEPLOYABILITY RATING
# ================================================================


def deploy_rating(value):
    if value >= 40:
        return "Excellent"

    elif value >= 30:
        return "Very Good"

    elif value >= 20:
        return "Good"

    elif value >= 10:
        return "Average"

    return "Poor"


# ================================================================
# CONSISTENCY RATING
# ================================================================


def consistency_rating(cv):
    if cv <= 0.08:
        return "Excellent"

    elif cv <= 0.12:
        return "Very Good"

    elif cv <= 0.18:
        return "Good"

    elif cv <= 0.25:
        return "Average"

    return "Poor"


# ================================================================
# COVERAGE RATING
# ================================================================


def coverage_rating(stocks):
    if stocks >= 150:
        return "Excellent"

    elif stocks >= 100:
        return "Very Good"

    elif stocks >= 60:
        return "Good"

    elif stocks >= 30:
        return "Average"

    return "Poor"


# ================================================================
# BUILD DIAGNOSTICS
# ================================================================


def build_diagnostics(df):
    logger.info("Generating Diagnostics...")

    df["Quality Rating"] = df["Median Composite"].apply(quality_rating)

    df["Deployability Rating"] = df["Deploy %"].apply(deploy_rating)

    df["Consistency Rating"] = df["CV"].apply(consistency_rating)

    df["Coverage Rating"] = df["Investable Stocks"].apply(coverage_rating)

    strengths = []

    weaknesses = []

    decisions = []

    risks = []

    for _, row in df.iterrows():
        s = []

        w = []

        # ----------------------------------------------------
        # Strengths
        # ----------------------------------------------------

        if row["Quality Rating"] == "Excellent":
            s.append("High Quality Universe")

        if row["Deployability Rating"] == "Excellent":
            s.append("Excellent Deployability")

        if row["Consistency Rating"] == "Excellent":
            s.append("Highly Consistent")

        if row["Coverage Rating"] == "Excellent":
            s.append("Broad Opportunity Set")

        # ----------------------------------------------------
        # Weaknesses
        # ----------------------------------------------------

        if row["Quality Rating"] == "Poor":
            w.append("Weak Universe Quality")

        if row["Deployability Rating"] == "Poor":
            w.append("Low Deployability")

        if row["Consistency Rating"] == "Poor":
            w.append("High Dispersion")

        if row["Coverage Rating"] == "Poor":
            w.append("Limited Opportunities")

        # ----------------------------------------------------
        # Decision
        # ----------------------------------------------------

        if (
            row["Quality Rating"] == "Excellent"
            and row["Deployability Rating"] in ["Excellent", "Very Good"]
            and row["Consistency Rating"] in ["Excellent", "Very Good"]
        ):
            decision = "DEPLOY"

            risk = "LOW"

        elif row["Quality Rating"] in ["Very Good", "Good"]:
            decision = "PAPER TRADE"

            risk = "MEDIUM"

        else:
            decision = "REJECT"

            risk = "HIGH"

        strengths.append("; ".join(s) if s else "None")

        weaknesses.append("; ".join(w) if w else "None")

        decisions.append(decision)

        risks.append(risk)

    df["Strengths"] = strengths

    df["Weaknesses"] = weaknesses

    df["Risk"] = risks

    df["Decision"] = decisions

    logger.info("Diagnostics Completed.")

    return df


# ================================================================
# PREVIEW
# ================================================================


def preview_diagnostics(df):
    print()

    print("=" * 120)

    print("UNIVERSE DIAGNOSTICS")

    print("=" * 120)

    print(
        df[
            [
                "Universe Rank",
                "Strategy",
                "Quality Rating",
                "Deployability Rating",
                "Consistency Rating",
                "Coverage Rating",
                "Decision",
            ]
        ]
    )

    print("=" * 120)


# ================================================================
# PART 6 : REPORT GENERATOR
# ================================================================

logger.info("Loading Report Generator...")

# ================================================================
# EXPORT EXCEL REPORT
# ================================================================


def export_report(universe, analytics):
    logger.info("Generating Excel Report...")

    dashboard = analytics[
        [
            "Universe Rank",
            "Strategy",
            "Median Composite",
            "Deploy %",
            "CV",
            "Investable Stocks",
            "Quality Rating",
            "Deployability Rating",
            "Consistency Rating",
            "Coverage Rating",
            "Decision",
        ]
    ].copy()

    diagnostics = analytics[
        ["Universe Rank", "Strategy", "Strengths", "Weaknesses", "Risk", "Decision"]
    ].copy()

    analytics_sheet = analytics.copy()

    raw_data = universe.copy()

    with pd.ExcelWriter(CONFIG["OUTPUT_FILE"], engine="openpyxl") as writer:
        dashboard.to_excel(writer, sheet_name="Dashboard", index=False)

        diagnostics.to_excel(writer, sheet_name="Diagnostics", index=False)

        analytics_sheet.to_excel(writer, sheet_name="Universe Analytics", index=False)

        raw_data.to_excel(writer, sheet_name="Raw Data", index=False)

    logger.info(f"Workbook Saved : {CONFIG['OUTPUT_FILE']}")


# ================================================================
# FINAL SUMMARY
# ================================================================


def print_final_summary(df):
    print()

    print("=" * 90)

    print("BEST STOCK UNIVERSE")

    print("=" * 90)

    best = df.iloc[0]

    print(f"Strategy           : {best['Strategy']}")

    print(f"Universe Rank      : {best['Universe Rank']}")

    print(f"Median Composite   : {best['Median Composite']:.2f}")

    print(f"Deploy %           : {best['Deploy %']:.2f}")

    print(f"Investable Stocks  : {best['Investable Stocks']}")

    print(f"Decision           : {best['Decision']}")

    print()

    print("Strengths")

    print(best["Strengths"])

    print()

    print("Weaknesses")

    print(best["Weaknesses"])

    print("=" * 90)


# ================================================================
# MAIN
# ================================================================


def main():
    logger.info("=" * 80)

    logger.info("Institutional Strategy Universe Evaluation Engine V3")

    logger.info("=" * 80)

    # ------------------------------------------------------------
    # Load
    # ------------------------------------------------------------

    universe = load_universe()

    print_input_summary(universe)

    # ------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------

    analytics = build_universe_analytics(universe)

    preview_universe(analytics)

    # ------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------

    analytics = rank_universes(analytics)

    preview_ranking(analytics)

    # ------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------

    analytics = build_diagnostics(analytics)

    preview_diagnostics(analytics)

    # ------------------------------------------------------------
    # Export
    # ------------------------------------------------------------

    export_report(universe, analytics)

    print_final_summary(analytics)

    logger.info("=" * 80)

    logger.info("PROCESS COMPLETED SUCCESSFULLY")

    logger.info("=" * 80)


# ================================================================
# START
# ================================================================

if __name__ == "__main__":
    main()
