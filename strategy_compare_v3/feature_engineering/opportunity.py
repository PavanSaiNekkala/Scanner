"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/opportunity.py

Production Opportunity Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class OpportunityEngine:
    """
    Institutional Opportunity Feature Engineering.

    Generates:

    Trades / Year
    Signal Frequency
    Opportunity Density
    Opportunity Velocity
    Opportunity Capture
    Opportunity Efficiency
    Opportunity Strength
    Opportunity Potential
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # =====================================================
    # SAFE DIVISION
    # =====================================================

    @staticmethod
    def safe_divide(a, b):
        return np.where(b == 0, np.nan, a / b)

    # =====================================================
    # TRADES PER YEAR
    # =====================================================

    def trades_per_year(self):
        if "Trades / Year" in self.df.columns:
            return

        if "Trades" in self.df.columns:
            if "Avg days" in self.df.columns:
                days = self.df["Avg days"]

            elif "days_held" in self.df.columns:
                days = self.df["days_held"]

            else:
                return

            self.df["Trades / Year"] = self.safe_divide(self.df["Trades"] * 365, days)

    # =====================================================
    # SIGNAL FREQUENCY
    # =====================================================

    def signal_frequency(self):
        if "Signal Frequency" in self.df.columns:
            return

        if "Signals today" in self.df.columns:
            if "Trades" in self.df.columns:
                self.df["Signal Frequency"] = self.safe_divide(
                    self.df["Signals today"], self.df["Trades"]
                )

                return

        # Trade level fallback

        if "Trades / Year" in self.df.columns:
            self.df["Signal Frequency"] = self.df["Trades / Year"] / 365

    # =====================================================
    # OPPORTUNITY DENSITY
    # =====================================================

    def opportunity_density(self):
        if "Opportunity Density" in self.df.columns:
            return

        if "Trades / Year" in self.df.columns:
            self.df["Opportunity Density"] = self.df["Trades / Year"] / 365

    # =====================================================
    # OPPORTUNITY VELOCITY
    # =====================================================

    def opportunity_velocity(self):
        required = {"Expectancy%", "days_held"}

        if required.issubset(self.df.columns):
            self.df["Opportunity Velocity"] = self.safe_divide(
                self.df["Expectancy%"], self.df["days_held"]
            )

            return

        required = {"Expectancy%", "Avg days"}

        if required.issubset(self.df.columns):
            self.df["Opportunity Velocity"] = self.safe_divide(
                self.df["Expectancy%"], self.df["Avg days"]
            )

    # =====================================================
    # OPPORTUNITY CAPTURE
    # =====================================================

    def opportunity_capture(self):
        required = {"Win %", "Edge Ratio"}

        if required.issubset(self.df.columns):
            self.df["Opportunity Capture"] = (
                self.df["Win %"] * self.df["Edge Ratio"] / 100
            )

            return

        if "Win %" in self.df.columns:
            self.df["Opportunity Capture"] = self.df["Win %"] / 100

    # =====================================================
    # OPPORTUNITY EFFICIENCY
    # =====================================================

    def opportunity_efficiency(self):
        required = {"Profit Factor", "Trades"}

        if required.issubset(self.df.columns):
            self.df["Opportunity Efficiency"] = self.safe_divide(
                self.df["Profit Factor"], self.df["Trades"]
            )

    # =====================================================
    # OPPORTUNITY STRENGTH
    # =====================================================

    def opportunity_strength(self):
        required = {"Expectancy%", "Profit Factor"}

        if required.issubset(self.df.columns):
            self.df["Opportunity Strength"] = (
                self.df["Expectancy%"] * self.df["Profit Factor"]
            )

    # =====================================================
    # OPPORTUNITY POTENTIAL
    # =====================================================

    def opportunity_potential(self):
        required = {"Opportunity Density", "Opportunity Strength"}

        if required.issubset(self.df.columns):
            self.df["Opportunity Potential"] = (
                self.df["Opportunity Density"] * self.df["Opportunity Strength"]
            )

    # =====================================================
    # GENERATE
    # =====================================================

    def generate(self):
        logger.info("Generating Opportunity Features...")

        self.trades_per_year()

        self.signal_frequency()

        self.opportunity_density()

        self.opportunity_velocity()

        self.opportunity_capture()

        self.opportunity_efficiency()

        self.opportunity_strength()

        self.opportunity_potential()

        logger.info("Opportunity feature engineering completed.")

        return self.df


if __name__ == "__main__":
    print("Import inside feature_engine.py")
