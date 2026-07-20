"""
============================================================
Institutional Strategy Comparison Engine V3

File : reports/strategy_comparison_report.py

Strategy Comparison Report Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import pandas as pd
import numpy as np

from core.logger import get_logger

logger = get_logger(__name__)


class StrategyComparisonReport:
    """
    Institutional Strategy Comparison Engine.


    Input
    -----

    Batch processed dataframe


    Required Columns

    Strategy
    Stock
    Composite Score
    Performance Score
    Reliability Score
    Risk Score
    Efficiency Score
    Opportunity Score



    Output

    Strategy ranking
    Stock ranking
    Strategy statistics

    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate(self):
        required = {"Strategy", "Composite Score"}

        missing = [col for col in required if col not in self.df.columns]

        if missing:
            raise ValueError(f"Missing columns: {missing}")

    # ==================================================
    # STRATEGY SUMMARY
    # ==================================================

    def strategy_summary(self):
        summary = (
            self.df.groupby("Strategy")
            .agg(
                Strategies_Count=("Stock", "count"),
                Average_Composite=("Composite Score", "mean"),
                Median_Composite=("Composite Score", "median"),
                Maximum_Score=("Composite Score", "max"),
                Minimum_Score=("Composite Score", "min"),
                Score_Volatility=("Composite Score", "std"),
            )
            .reset_index()
        )

        return summary

    # ==================================================
    # STRATEGY RANK
    # ==================================================

    def strategy_ranking(self):
        summary = self.strategy_summary()

        summary["Strategy Rank"] = (
            summary["Average_Composite"]
            .rank(ascending=False, method="dense")
            .astype(int)
        )

        return summary.sort_values("Strategy Rank")

    # ==================================================
    # BEST STOCKS
    # ==================================================

    def top_stocks(self, n=10):
        return self.df.sort_values("Composite Score", ascending=False).head(n)

    # ==================================================
    # SCORE DISTRIBUTION
    # ==================================================

    def score_statistics(self):
        numeric = self.df.select_dtypes(include=np.number)

        return numeric.describe().T

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating Strategy Comparison Report...")

        self.validate()

        result = {
            "Strategy Ranking": self.strategy_ranking(),
            "Top Stocks": self.top_stocks(),
            "Score Statistics": self.score_statistics(),
        }

        logger.info("Strategy Comparison Report completed.")

        return result


if __name__ == "__main__":
    print("Import StrategyComparisonReport")
