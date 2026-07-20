"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/reliability_metrics.py

Reliability Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class ReliabilityMetricsEngine:
    """
    Generates reliability and confidence metrics.

    Input Fields
    ------------
    Trades
    Years
    Win%
    Avg days
    Expectancy%


    Generated Fields
    ----------------
    Trades / Year
    Trades / Month
    Trade Confidence
    Backtest Quality
    Sample Reliability
    Consistency Factor
    Strategy Maturity
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # ==================================================
    # SAFE DIVIDE
    # ==================================================

    @staticmethod
    def safe_divide(a, b):
        return np.where(b == 0, np.nan, a / b)

    # ==================================================
    # TRADES PER YEAR
    # ==================================================

    def trades_per_year(self):
        required = {"Trades", "Years"}

        if not required.issubset(self.df.columns):
            return

        self.df["Trades / Year"] = self.safe_divide(self.df["Trades"], self.df["Years"])

    # ==================================================
    # TRADES PER MONTH
    # ==================================================

    def trades_per_month(self):
        if "Trades / Year" not in self.df.columns:
            return

        self.df["Trades / Month"] = self.df["Trades / Year"] / 12

    # ==================================================
    # TRADE CONFIDENCE
    # ==================================================

    def trade_confidence(self):
        required = {"Trades", "Win%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Trade Confidence"] = self.df["Trades"] * self.df["Win%"] / 100

    # ==================================================
    # BACKTEST QUALITY
    # ==================================================

    def backtest_quality(self):
        required = {"Trades", "Years"}

        if not required.issubset(self.df.columns):
            return

        self.df["Backtest Quality"] = self.df["Trades"] * self.df["Years"]

    # ==================================================
    # SAMPLE RELIABILITY
    # ==================================================

    def sample_reliability(self):
        required = {"Trades", "Years"}

        if not required.issubset(self.df.columns):
            return

        self.df["Sample Reliability"] = np.log1p(self.df["Trades"]) * self.df["Years"]

    # ==================================================
    # CONSISTENCY FACTOR
    # ==================================================

    def consistency_factor(self):
        required = {"Win%", "Years"}

        if not required.issubset(self.df.columns):
            return

        self.df["Consistency Factor"] = self.df["Win%"] * self.df["Years"] / 100

    # ==================================================
    # STRATEGY MATURITY
    # ==================================================

    def strategy_maturity(self):
        required = {"Trades", "Years", "Win%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Strategy Maturity"] = (
            np.log1p(self.df["Trades"]) * self.df["Years"]
        ) * (self.df["Win%"] / 100)

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating Reliability Metrics...")

        self.trades_per_year()

        self.trades_per_month()

        self.trade_confidence()

        self.backtest_quality()

        self.sample_reliability()

        self.consistency_factor()

        self.strategy_maturity()

        logger.info("Reliability Metrics completed.")

        return self.df


if __name__ == "__main__":
    print("Import ReliabilityMetricsEngine")
