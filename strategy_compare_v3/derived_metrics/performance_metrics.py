"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/performance_metrics.py

Performance Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class PerformanceMetricsEngine:
    """
    Generates performance related derived metrics.

    Input Fields
    ------------
    Win%
    Avg win%
    Avg loss%
    Expectancy%
    Trades
    Avg days
    Years


    Generated Fields
    ----------------
    Loss %
    Reward Risk Ratio
    Profit Factor
    Expected Return
    Annualized Expectancy
    Expectancy Per Trade
    Expectancy Per Day
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
    # LOSS %
    # ==================================================

    def loss_percentage(self):
        if "Win%" not in self.df.columns:
            return

        self.df["Loss %"] = 100 - self.df["Win%"]

    # ==================================================
    # REWARD RISK RATIO
    # ==================================================

    def reward_risk_ratio(self):
        required = {"Avg win%", "Avg loss%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Reward Risk Ratio"] = self.safe_divide(
            self.df["Avg win%"], self.df["Avg loss%"].abs()
        )

    # ==================================================
    # PROFIT FACTOR
    # ==================================================

    def profit_factor(self):
        required = {"Win%", "Loss %", "Avg win%", "Avg loss%"}

        if not required.issubset(self.df.columns):
            return

        numerator = self.df["Win%"] * self.df["Avg win%"]

        denominator = self.df["Loss %"] * self.df["Avg loss%"].abs()

        self.df["Profit Factor"] = self.safe_divide(numerator, denominator)

    # ==================================================
    # EXPECTED RETURN
    # ==================================================

    def expected_return(self):
        required = {"Win%", "Loss %", "Avg win%", "Avg loss%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Expected Return"] = (self.df["Win%"] / 100) * self.df["Avg win%"] - (
            self.df["Loss %"] / 100
        ) * self.df["Avg loss%"].abs()

    # ==================================================
    # EXPECTANCY PER TRADE
    # ==================================================

    def expectancy_per_trade(self):
        if not {"Expectancy%", "Trades"}.issubset(self.df.columns):
            return

        self.df["Expectancy Per Trade"] = self.safe_divide(
            self.df["Expectancy%"], self.df["Trades"]
        )

    # ==================================================
    # EXPECTANCY PER DAY
    # ==================================================

    def expectancy_per_day(self):
        if not {"Expectancy%", "Avg days"}.issubset(self.df.columns):
            return

        self.df["Expectancy Per Day"] = self.safe_divide(
            self.df["Expectancy%"], self.df["Avg days"]
        )

    # ==================================================
    # ANNUALIZED EXPECTANCY
    # ==================================================

    def annualized_expectancy(self):
        required = {"Expectancy%", "Trades", "Years"}

        if not required.issubset(self.df.columns):
            return

        trades_year = self.safe_divide(self.df["Trades"], self.df["Years"])

        self.df["Annualized Expectancy"] = self.df["Expectancy%"] * trades_year

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating Performance Metrics...")

        self.loss_percentage()

        self.reward_risk_ratio()

        self.profit_factor()

        self.expected_return()

        self.expectancy_per_trade()

        self.expectancy_per_day()

        self.annualized_expectancy()

        logger.info("Performance Metrics completed.")

        return self.df


if __name__ == "__main__":
    print("Import PerformanceMetricsEngine")
