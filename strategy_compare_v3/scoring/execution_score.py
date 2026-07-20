"""
============================================================
Institutional Strategy Comparison Engine V3

File : scoring/execution_score.py

Institutional Execution Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import numpy as np
import pandas as pd


from core.logger import get_logger

logger = get_logger(__name__)


class ExecutionScoreEngine:
    """
    Institutional Execution Quality Scoring.

    Generates:

        Execution Score


    Supported Inputs:

        Execution Quality
        Signal Quality
        Holding Efficiency
        Trade Quality
        Expectancy Per Trade
        Capital Efficiency
        Opportunity Capture

    """

    DEFAULT_WEIGHTS = {
        "Execution Quality": 0.25,
        "Signal Quality": 0.20,
        "Holding Efficiency": 0.15,
        "Trade Quality": 0.15,
        "Expectancy Per Trade": 0.10,
        "Capital Efficiency": 0.10,
        "Opportunity Capture": 0.05,
    }

    def __init__(self, dataframe: pd.DataFrame, weights: dict | None = None):
        self.df = dataframe.copy()

        self.weights = weights if weights else self.DEFAULT_WEIGHTS

    # ==================================================
    # NORMALIZE COLUMNS
    # ==================================================

    def normalize_columns(self):
        mapping = {
            "Execution_Quality": "Execution Quality",
            "Signal_Quality": "Signal Quality",
            "Holding_Efficiency": "Holding Efficiency",
            "Trade_Quality": "Trade Quality",
            "Expectancy_Per_Trade": "Expectancy Per Trade",
            "Capital_Efficiency": "Capital Efficiency",
            "Opportunity_Capture": "Opportunity Capture",
        }

        for source, target in mapping.items():
            if source in self.df.columns and target not in self.df.columns:
                self.df[target] = self.df[source]

    # ==================================================
    # FALLBACK FEATURE GENERATION
    # ==================================================

    def generate_missing_features(self):
        # Holding Efficiency

        if "Holding Efficiency" not in self.df.columns:
            if "Expectancy%" in self.df.columns and "Avg days" in self.df.columns:
                self.df["Holding Efficiency"] = self.df["Expectancy%"] / self.df[
                    "Avg days"
                ].replace(0, np.nan)

        # Expectancy Per Trade

        if "Expectancy Per Trade" not in self.df.columns:
            if "Expectancy%" in self.df.columns and "Trades" in self.df.columns:
                self.df["Expectancy Per Trade"] = self.df["Expectancy%"] / self.df[
                    "Trades"
                ].replace(0, np.nan)

        # Capital Efficiency

        if "Capital Efficiency" not in self.df.columns:
            if "Expectancy%" in self.df.columns and "entry_price" in self.df.columns:
                self.df["Capital Efficiency"] = self.df["Expectancy%"] / self.df[
                    "entry_price"
                ].replace(0, np.nan)

        # Trade Quality fallback

        if "Trade Quality" not in self.df.columns:
            if "Win %" in self.df.columns and "Profit Factor" in self.df.columns:
                self.df["Trade Quality"] = (
                    self.df["Win %"] * self.df["Profit Factor"] / 100
                )

        # Execution Quality fallback

        if "Execution Quality" not in self.df.columns:
            components = []

            for col in ["Trade Quality", "Signal Quality", "Holding Efficiency"]:
                if col in self.df.columns:
                    components.append(self.df[col])

            if components:
                self.df["Execution Quality"] = pd.concat(components, axis=1).mean(
                    axis=1
                )

        # Signal Quality fallback

        if "Signal Quality" not in self.df.columns:
            if "Edge Ratio" in self.df.columns:
                self.df["Signal Quality"] = self.df["Edge Ratio"] * 50

        # Opportunity Capture fallback

        if "Opportunity Capture" not in self.df.columns:
            if "Win %" in self.df.columns:
                self.df["Opportunity Capture"] = self.df["Win %"]

    # ==================================================
    # NORMALIZATION
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
        logger.info("Generating Execution Score...")

        self.normalize_columns()

        self.generate_missing_features()

        score = pd.Series(0.0, index=self.df.index)

        total_weight = 0

        for feature, weight in self.weights.items():
            if feature not in self.df.columns:
                logger.warning("Skipping missing execution feature: %s", feature)

                continue

            normalized = self.normalize(self.df[feature])

            score += normalized * weight

            total_weight += weight

        if total_weight == 0:
            self.df["Execution Score"] = 0

        else:
            self.df["Execution Score"] = (score / total_weight).round(2)

        logger.info("Execution Score generated successfully.")

        return self.df[["Execution Score"]]


if __name__ == "__main__":
    print("Import ExecutionScoreEngine inside scoring_engine.py")
