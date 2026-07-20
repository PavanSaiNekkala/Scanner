"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/expectancy.py

Production Expectancy Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class ExpectancyEngine:
    """
    Institutional Expectancy Feature Engineering.

    Input Columns
    -------------
    Win_Pct
    Avg_winPct
    Avg_lossPct
    Trades
    ExpectancyPct
    Avg_days
    Reward Risk Ratio


    Generated Columns
    -----------------
    Calculated Expectancy
    Expectancy%
    Expectancy Difference
    Expectancy Per Trade
    Expectancy Per Day
    Expectancy Efficiency
    Expectancy Quality
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
    # CALCULATE EXPECTANCY
    # ==================================================

    def calculate_expectancy(self):
        required = {"Win_Pct", "Avg_winPct", "Avg_lossPct"}

        if not required.issubset(self.df.columns):
            logger.warning(
                "Calculated Expectancy skipped. Missing %s",
                required - set(self.df.columns),
            )

            return

        win_rate = self.df["Win_Pct"] / 100

        loss_rate = 1 - win_rate

        self.df["Calculated Expectancy"] = (
            win_rate * self.df["Avg_winPct"] - loss_rate * self.df["Avg_lossPct"].abs()
        )

    # ==================================================
    # STANDARDIZE EXPECTANCY COLUMN
    # ==================================================

    def standardize_expectancy(self):
        if "ExpectancyPct" in self.df.columns:
            self.df["Expectancy%"] = self.df["ExpectancyPct"]

    # ==================================================
    # EXPECTANCY DIFFERENCE
    # ==================================================

    def expectancy_difference(self):
        required = {"Expectancy%", "Calculated Expectancy"}

        if not required.issubset(self.df.columns):
            return

        self.df["Expectancy Difference"] = (
            self.df["Expectancy%"] - self.df["Calculated Expectancy"]
        )

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
        if not {"Expectancy%", "Avg_days"}.issubset(self.df.columns):
            return

        self.df["Expectancy Per Day"] = self.safe_divide(
            self.df["Expectancy%"], self.df["Avg_days"]
        )

    # ==================================================
    # EXPECTANCY EFFICIENCY
    # ==================================================

    def expectancy_efficiency(self):
        if not {"Calculated Expectancy", "Reward Risk Ratio"}.issubset(self.df.columns):
            return

        self.df["Expectancy Efficiency"] = self.safe_divide(
            self.df["Calculated Expectancy"], self.df["Reward Risk Ratio"]
        )

    # ==================================================
    # EXPECTANCY QUALITY
    # ==================================================

    def expectancy_quality(self):
        if "Calculated Expectancy" not in self.df.columns:
            return

        score = self.df["Calculated Expectancy"]

        conditions = [score >= 2, score >= 1, score >= 0]

        choices = ["Excellent", "Good", "Average"]

        self.df["Expectancy Quality"] = np.select(conditions, choices, default="Poor")

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating Expectancy Features...")

        self.standardize_expectancy()

        self.calculate_expectancy()

        self.expectancy_difference()

        self.expectancy_per_trade()

        self.expectancy_per_day()

        self.expectancy_efficiency()

        self.expectancy_quality()

        logger.info("Expectancy feature engineering completed.")

        return self.df


if __name__ == "__main__":
    print("Import ExpectancyEngine inside feature_engine.py")
