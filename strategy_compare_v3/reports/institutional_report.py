"""
============================================================
Institutional Strategy Comparison Engine V3
File : reports/institutional_report.py

Institutional Report Generator

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class InstitutionalReport:
    """
    Generates an executive institutional report.

    Produces KPI tables and executive
    summaries from the scored dataset.
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # --------------------------------------------------

    def executive_summary(self):
        return pd.DataFrame(
            {
                "Metric": [
                    "Report Generated",
                    "Total Strategies",
                    "Average Composite Score",
                    "Highest Composite Score",
                    "Lowest Composite Score",
                    "Average Institutional Score",
                ],
                "Value": [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(self.df),
                    round(self.df["Composite Score"].mean(), 2),
                    round(self.df["Composite Score"].max(), 2),
                    round(self.df["Composite Score"].min(), 2),
                    round(self.df["Institutional Score"].mean(), 2),
                ],
            }
        )

    # --------------------------------------------------

    def recommendation_distribution(self):
        if "Recommendation" not in self.df.columns:
            return pd.DataFrame()

        result = (
            self.df["Recommendation"]
            .value_counts()
            .rename_axis("Recommendation")
            .reset_index(name="Count")
        )

        result["Percentage"] = (result["Count"] / len(self.df) * 100).round(2)

        return result

    # --------------------------------------------------

    def score_statistics(self):
        score_columns = [
            column for column in self.df.columns if column.endswith("Score")
        ]

        if not score_columns:
            return pd.DataFrame()

        return self.df[score_columns].describe().T

    # --------------------------------------------------

    def top_strategies(self, n: int = 20):
        columns = [
            c
            for c in [
                "Stock",
                "Composite Score",
                "Institutional Score",
                "Recommendation",
            ]
            if c in self.df.columns
        ]

        return (
            self.df.sort_values("Composite Score", ascending=False)[columns]
            .head(n)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def bottom_strategies(self, n: int = 20):
        columns = [
            c
            for c in [
                "Stock",
                "Composite Score",
                "Institutional Score",
                "Recommendation",
            ]
            if c in self.df.columns
        ]

        return (
            self.df.sort_values("Composite Score", ascending=True)[columns]
            .head(n)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def score_rankings(self):
        ranking = {}

        score_columns = [c for c in self.df.columns if c.endswith("Score")]

        identifier = "Stock" if "Stock" in self.df.columns else self.df.columns[0]

        for score in score_columns:
            ranking[score] = (
                self.df.sort_values(score, ascending=False)[[identifier, score]]
                .head(10)
                .reset_index(drop=True)
            )

        return ranking

    # --------------------------------------------------

    def percentile_summary(self):
        score_columns = [c for c in self.df.columns if c.endswith("Score")]

        rows = []

        for column in score_columns:
            values = self.df[column]

            rows.append(
                {
                    "Score": column,
                    "P10": values.quantile(0.10),
                    "P25": values.quantile(0.25),
                    "Median": values.quantile(0.50),
                    "P75": values.quantile(0.75),
                    "P90": values.quantile(0.90),
                }
            )

        return pd.DataFrame(rows)

    # --------------------------------------------------

    def generate(self):
        logger.info("Generating Institutional Report...")

        report = {
            "Executive Summary": self.executive_summary(),
            "Recommendation Distribution": self.recommendation_distribution(),
            "Score Statistics": self.score_statistics(),
            "Percentile Summary": self.percentile_summary(),
            "Top Strategies": self.top_strategies(),
            "Bottom Strategies": self.bottom_strategies(),
        }

        report.update(self.score_rankings())

        logger.info("Institutional Report completed.")

        return report


if __name__ == "__main__":
    print("Import inside report_engine.py")
