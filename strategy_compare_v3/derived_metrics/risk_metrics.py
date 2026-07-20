"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/risk_metrics.py

Risk Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class RiskMetricsEngine:
    """
    Generates risk related derived metrics.

    Input Fields
    ------------
    Win%
    Loss %
    Avg loss%
    Avg win%
    Expectancy%
    Reward Risk Ratio
    Profit Factor
    Stop %
    Stop Ratio


    Generated Fields
    ----------------
    Risk Exposure
    Risk Adjusted Expectancy
    Risk Reward Quality
    Stop Efficiency
    Loss Pressure
    Recovery Factor
    Risk Efficiency
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
    # RISK EXPOSURE
    # ==================================================

    def risk_exposure(self):
        required = {"Loss %", "Avg loss%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Risk Exposure"] = self.df["Loss %"] * self.df["Avg loss%"].abs() / 100

    # ==================================================
    # RISK ADJUSTED EXPECTANCY
    # ==================================================

    def risk_adjusted_expectancy(self):
        required = {"Expectancy%", "Avg loss%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Risk Adjusted Expectancy"] = self.safe_divide(
            self.df["Expectancy%"], self.df["Avg loss%"].abs()
        )

    # ==================================================
    # RISK REWARD QUALITY
    # ==================================================

    def risk_reward_quality(self):
        required = {"Reward Risk Ratio", "Win%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Risk Reward Quality"] = (
            self.df["Reward Risk Ratio"] * self.df["Win%"] / 100
        )

    # ==================================================
    # STOP EFFICIENCY
    # ==================================================

    def stop_efficiency(self):
        if "Stop %" not in self.df.columns:
            return

        self.df["Stop Efficiency"] = 100 - self.df["Stop %"].abs()

    # ==================================================
    # LOSS PRESSURE
    # ==================================================

    def loss_pressure(self):
        required = {"Loss %", "Avg loss%"}

        if not required.issubset(self.df.columns):
            return

        self.df["Loss Pressure"] = self.df["Loss %"] * self.df["Avg loss%"].abs()

    # ==================================================
    # RECOVERY FACTOR
    # ==================================================

    def recovery_factor(self):
        required = {"Expectancy%", "Risk Exposure"}

        if not required.issubset(self.df.columns):
            return

        self.df["Recovery Factor"] = self.safe_divide(
            self.df["Expectancy%"], self.df["Risk Exposure"]
        )

    # ==================================================
    # RISK EFFICIENCY
    # ==================================================

    def risk_efficiency(self):
        required = {"Reward Risk Ratio", "Risk Exposure"}

        if not required.issubset(self.df.columns):
            return

        self.df["Risk Efficiency"] = self.safe_divide(
            self.df["Reward Risk Ratio"], self.df["Risk Exposure"]
        )

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating Risk Metrics...")

        self.risk_exposure()

        self.risk_adjusted_expectancy()

        self.risk_reward_quality()

        self.stop_efficiency()

        self.loss_pressure()

        self.recovery_factor()

        self.risk_efficiency()

        logger.info("Risk Metrics completed.")

        return self.df


if __name__ == "__main__":
    print("Import RiskMetricsEngine")
