"""
Portfolio Statistics Engine
"""

import pandas as pd

from config import DECIMAL_PLACES, TOP_N

from utils import top_n, bottom_n, dataframe_info

###########################################################################
# STATISTICS REPORT
###########################################################################


class StatisticsReport:
    def __init__(self, ranked):
        self.df = ranked.copy()

    ###########################################################################
    # OVERALL SUMMARY
    ###########################################################################

    def overall_summary(self):
        if self.df.empty:
            return pd.DataFrame()

        score = self.df["Overall Score"]

        summary = {
            "Total Strategies": len(self.df),
            "Average Score": round(score.mean(), DECIMAL_PLACES),
            "Highest Score": round(score.max(), DECIMAL_PLACES),
            "Lowest Score": round(score.min(), DECIMAL_PLACES),
            "Median Score": round(score.median(), DECIMAL_PLACES),
            "Score Std Dev": round(score.std(), DECIMAL_PLACES),
        }

        return pd.DataFrame(summary.items(), columns=["Metric", "Value"])

    ###########################################################################
    # GRADE SUMMARY
    ###########################################################################

    def grade_summary(self):
        if "Grade" not in self.df.columns:
            return pd.DataFrame()

        grades = (
            self.df["Grade"]
            .value_counts()
            .rename_axis("Grade")
            .reset_index(name="Count")
        )

        grades["Percentage"] = (grades["Count"] / grades["Count"].sum() * 100).round(
            DECIMAL_PLACES
        )

        return grades

    ###########################################################################
    # RECOMMENDATION SUMMARY
    ###########################################################################

    def recommendation_summary(self):
        if "Recommendation" not in self.df.columns:
            return pd.DataFrame()

        recommendations = (
            self.df["Recommendation"]
            .value_counts()
            .rename_axis("Recommendation")
            .reset_index(name="Count")
        )

        recommendations["Percentage"] = (
            recommendations["Count"] / recommendations["Count"].sum() * 100
        ).round(DECIMAL_PLACES)

        return recommendations

    ###########################################################################
    # SCORE DISTRIBUTION
    ###########################################################################

    def score_distribution(self):
        if self.df.empty:
            return pd.DataFrame()

        return self.df[["Strategy", "Overall Score"]].sort_values(
            "Overall Score", ascending=False
        )

    ###########################################################################
    # METRIC AVERAGES
    ###########################################################################

    def metric_averages(self):
        metrics = [column for column in self.df.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Average": round(self.df[metric].mean(), DECIMAL_PLACES),
                    "Maximum": round(self.df[metric].max(), DECIMAL_PLACES),
                    "Minimum": round(self.df[metric].min(), DECIMAL_PLACES),
                    "Std Dev": round(self.df[metric].std(), DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # SCORE STATISTICS
    ###########################################################################

    def score_statistics(self):
        return self.df["Overall Score"].describe().round(DECIMAL_PLACES)

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top_strategies(self, n=TOP_N):
        return top_n(self.df, "Overall Score", n)

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom_strategies(self, n=TOP_N):
        return bottom_n(self.df, "Overall Score", n)

    ###########################################################################
    # EXECUTIVE KPI
    ###########################################################################

    def executive_kpi(self):
        return {
            "Strategies": len(self.df),
            "Average Score": round(self.df["Overall Score"].mean(), DECIMAL_PLACES),
            "Highest Score": round(self.df["Overall Score"].max(), DECIMAL_PLACES),
            "Strong Buy": int((self.df["Recommendation"] == "Strong Buy").sum()),
            "Buy": int((self.df["Recommendation"] == "Buy").sum()),
        }

    ###########################################################################
    # DATAFRAME INFO
    ###########################################################################

    def dataframe_summary(self):
        return dataframe_info(self.df)

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):
        return {
            "summary": self.overall_summary(),
            "grades": self.grade_summary(),
            "recommendations": self.recommendation_summary(),
            "metrics": self.metric_averages(),
            "distribution": self.score_distribution(),
            "statistics": self.score_statistics(),
            "top": self.top_strategies(),
            "bottom": self.bottom_strategies(),
            "kpi": self.executive_kpi(),
            "dataframe": self.dataframe_summary(),
        }
