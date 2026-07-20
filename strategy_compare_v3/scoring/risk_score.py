"""
============================================================
Institutional Strategy Comparison Engine V3

File : scoring/risk_score.py

Institutional Risk Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import numpy as np
import pandas as pd


from core.logger import get_logger

logger = get_logger(__name__)


class RiskScoreEngine:
    """
    Institutional Risk Score Calculation.

    Creates:

        Risk Score


    Supported Inputs:

        Reward Risk Ratio
        Profit Factor
        Avg loss%
        Stop %
        Expectancy Per Risk
        Expectancy%

    """

    DEFAULT_WEIGHTS = {
        "Reward Risk Ratio": 0.30,
        "Profit Factor": 0.20,
        "Avg loss%": 0.20,
        "Stop %": 0.15,
        "Expectancy Per Risk": 0.15,
    }

    def __init__(self, dataframe: pd.DataFrame, weights: dict | None = None):
        self.df = dataframe.copy()

        self.weights = weights if weights else self.DEFAULT_WEIGHTS

    # ==================================================
    # COLUMN NORMALIZATION
    # ==================================================

    def normalize_columns(self):
        mapping = {
            "Avg_lossPct": "Avg loss%",
            "Stop_Pct": "Stop %",
            "Reward_Risk_Ratio": "Reward Risk Ratio",
            "Profit_Factor": "Profit Factor",
            "ExpectancyPct": "Expectancy%",
        }

        for source, target in mapping.items():
            if source in self.df.columns and target not in self.df.columns:
                self.df[target] = self.df[source]

        # Generate Expectancy Per Risk fallback

        if "Expectancy Per Risk" not in self.df.columns:
            if "Expectancy%" in self.df.columns and "Avg loss%" in self.df.columns:
                self.df["Expectancy Per Risk"] = self.df["Expectancy%"] / self.df[
                    "Avg loss%"
                ].abs().replace(0, np.nan)

    # ==================================================
    # VALIDATE
    # ==================================================

    def validate(self):
        missing = [column for column in self.weights if column not in self.df.columns]

        if missing:
            logger.warning("Risk score missing columns: %s", missing)

            return False

        return True

    # ==================================================
    # NORMALIZE SCORE
    # ==================================================

    @staticmethod
    def normalize(series):
        minimum = series.min()

        maximum = series.max()

        if maximum == minimum:
            return pd.Series(50, index=series.index)

        return (series - minimum) / (maximum - minimum) * 100

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating Risk Score...")

        self.normalize_columns()

        score = pd.Series(0.0, index=self.df.index)

        total_weight = 0

        for feature, weight in self.weights.items():
            if feature not in self.df.columns:
                continue

            values = self.df[feature].copy()

            # Lower risk is better

            if feature in ["Avg loss%", "Stop %"]:
                values = -values

            normalized = self.normalize(values)

            score += normalized * weight

            total_weight += weight

        if total_weight == 0:
            self.df["Risk Score"] = 0

        else:
            self.df["Risk Score"] = (score / total_weight).round(2)

        logger.info("Risk Score generated successfully.")

        return self.df[["Risk Score"]]


if __name__ == "__main__":
    print("Import RiskScoreEngine inside scoring_engine.py")
