"""
===============================================================
Institutional Strategy Comparison Engine V3

Module
------
opportunity_metrics.py

Purpose
-------
Derive opportunity and execution metrics from strategy
backtest results.

Author
------
OpenAI

===============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ============================================================
# Utility Functions
# ============================================================


def numeric(series):
    return pd.to_numeric(series, errors="coerce")


def safe_divide(a, b):
    a = numeric(a)

    b = numeric(b)

    return np.where((b == 0) | (pd.isna(b)), np.nan, a / b)


# ============================================================
# Opportunity Metrics
# ============================================================


class OpportunityMetrics:
    def __init__(self, df):
        self.df = df.copy()

    # --------------------------------------------------------

    def prepare_columns(self):
        cols = [
            "Signals today",
            "Trades",
            "Years",
            "Avg days",
            "Win%",
            "Annual Return %",
        ]

        for col in cols:
            if col in self.df.columns:
                self.df[col] = numeric(self.df[col])

        return self

    # --------------------------------------------------------

    def trades_per_year(self):
        self.df["Trades / Year"] = safe_divide(self.df["Trades"], self.df["Years"])

        return self

    # --------------------------------------------------------

    def signals_per_year(self):
        if "Signals today" in self.df.columns:
            self.df["Signals / Year"] = self.df["Signals today"] * 252

        else:
            self.df["Signals / Year"] = self.df["Trades / Year"]

        return self

    # --------------------------------------------------------

    def signal_conversion(self):
        if "Signals today" in self.df.columns:
            self.df["Signal Conversion"] = safe_divide(
                self.df["Trades"], self.df["Signals today"]
            )

        else:
            self.df["Signal Conversion"] = 1.0

        return self

    # --------------------------------------------------------

    def opportunity_utilization(self):
        self.df["Opportunity Utilization"] = self.df["Signal Conversion"] * 100

        return self

    # --------------------------------------------------------

    def trade_density(self):
        self.df["Trade Density"] = safe_divide(self.df["Trades"], self.df["Avg days"])

        return self

    # --------------------------------------------------------

    def holding_occupancy(self):
        self.df["Holding Occupancy"] = np.clip(
            safe_divide(
                self.df["Trades"] * self.df["Avg days"], self.df["Years"] * 365.25
            ),
            0,
            1,
        )

        return self

    # --------------------------------------------------------

    def idle_time_ratio(self):
        self.df["Idle Time Ratio"] = 1 - self.df["Holding Occupancy"]

        return self

    # --------------------------------------------------------

    def opportunity_coverage(self):
        self.df["Opportunity Coverage"] = self.df["Holding Occupancy"] * 100

        return self

    # --------------------------------------------------------

    def capacity_score(self):
        self.df["Capacity Score"] = (
            self.df["Trade Density"] * 0.40
            + self.df["Signal Conversion"] * 25
            + self.df["Holding Occupancy"] * 35
        )

        return self

    # --------------------------------------------------------

    def opportunity_velocity(self):
        """
        Opportunities generated
        per holding day.
        """

        self.df["Opportunity Velocity"] = safe_divide(
            self.df["Trades / Year"], self.df["Avg days"]
        )

        return self

    # --------------------------------------------------------

    def trade_availability(self):
        """
        Fraction of signals
        becoming executable trades.
        """

        if "Signals today" in self.df.columns:
            self.df["Trade Availability"] = safe_divide(
                self.df["Trades"], self.df["Signals today"]
            )

        else:
            self.df["Trade Availability"] = 1.0

        return self

    # --------------------------------------------------------

    def signal_saturation(self):
        if "Signals today" in self.df.columns:
            self.df["Signal Saturation"] = safe_divide(
                self.df["Signals today"], self.df["Trades"]
            )

        else:
            self.df["Signal Saturation"] = 1.0

        return self

    # --------------------------------------------------------

    def execution_efficiency(self):
        """
        Winning trades generated
        from available opportunities.
        """

        self.df["Execution Efficiency"] = (
            self.df["Signal Conversion"] * self.df["Win%"] / 100
        )

        return self

    # --------------------------------------------------------

    def market_coverage(self):
        """
        Annual participation.
        """

        self.df["Market Coverage"] = self.df["Holding Occupancy"] * 100

        return self

    # --------------------------------------------------------

    def opportunity_quality(self):
        """
        Weighted opportunity quality.
        """

        self.df["Opportunity Quality"] = (
            self.df["Execution Efficiency"] * 0.40
            + self.df["Trade Density"] * 0.35
            + self.df["Signal Conversion"] * 0.25
        )

        return self

    # --------------------------------------------------------

    def capacity_utilization(self):
        """
        Utilization of available
        opportunities.
        """

        self.df["Capacity Utilization"] = (
            self.df["Capacity Score"] * self.df["Holding Occupancy"]
        )

        return self

    # --------------------------------------------------------

    def annual_signal_efficiency(self):
        """
        Signal efficiency
        normalized annually.
        """

        self.df["Annual Signal Efficiency"] = (
            self.df["Execution Efficiency"] * self.df["Trades / Year"]
        )

        return self

    # --------------------------------------------------------

    def trade_opportunity_ratio(self):
        if "Signals today" in self.df.columns:
            self.df["Trade Opportunity Ratio"] = safe_divide(
                self.df["Trades"], self.df["Signals today"]
            )

        else:
            self.df["Trade Opportunity Ratio"] = 1.0

        return self

    # --------------------------------------------------------

    def opportunity_persistence(self):
        """
        Persistence of opportunities.
        """

        self.df["Opportunity Persistence"] = safe_divide(
            self.df["Trade Density"], self.df["Idle Time Ratio"] + 1e-9
        )

        return self

    # --------------------------------------------------------

    def execution_consistency(self):
        """
        Execution quality
        adjusted for holding period.
        """

        self.df["Execution Consistency"] = safe_divide(
            self.df["Execution Efficiency"], self.df["Avg days"]
        )

        return self

    # --------------------------------------------------------

    def institutional_opportunity_score(self):
        """
        Institutional composite score.
        """

        self.df["Institutional Opportunity Score"] = (
            self.df["Opportunity Quality"] * 0.35
            + self.df["Capacity Score"] * 0.25
            + self.df["Execution Efficiency"] * 0.20
            + self.df["Trade Density"] * 0.20
        )

        return self

    # --------------------------------------------------------

    def opportunity_rank(self):
        """
        Percentile rank based on
        Institutional Opportunity Score.
        """

        self.df["Opportunity Rank"] = (
            self.df["Institutional Opportunity Score"].rank(pct=True, ascending=True)
            * 100
        )

        return self

    # --------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize major opportunity metrics
        to a 0–100 scale using Min-Max scaling.
        """

        metrics = [
            "Capacity Score",
            "Opportunity Quality",
            "Execution Efficiency",
            "Trade Density",
            "Institutional Opportunity Score",
        ]

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            minimum = self.df[metric].min()
            maximum = self.df[metric].max()

            if pd.isna(minimum) or pd.isna(maximum):
                continue

            if maximum == minimum:
                self.df[f"{metric} (Norm)"] = 50.0

            else:
                self.df[f"{metric} (Norm)"] = (
                    (self.df[metric] - minimum) / (maximum - minimum) * 100
                )

        return self

    # --------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid values.
        """

        self.df.replace([np.inf, -np.inf], np.nan, inplace=True)

        return self

    # --------------------------------------------------------

    def round_metrics(self):
        """
        Round all derived opportunity metrics.
        """

        derived_cols = [
            "Trades / Year",
            "Signals / Year",
            "Signal Conversion",
            "Opportunity Utilization",
            "Trade Density",
            "Holding Occupancy",
            "Idle Time Ratio",
            "Opportunity Coverage",
            "Capacity Score",
            "Opportunity Velocity",
            "Trade Availability",
            "Signal Saturation",
            "Execution Efficiency",
            "Market Coverage",
            "Opportunity Quality",
            "Capacity Utilization",
            "Annual Signal Efficiency",
            "Trade Opportunity Ratio",
            "Opportunity Persistence",
            "Execution Consistency",
            "Institutional Opportunity Score",
            "Opportunity Rank",
        ]

        for col in derived_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].round(4)

        return self

    # --------------------------------------------------------

    def run(self):
        return (
            self.prepare_columns()
            .trades_per_year()
            .signals_per_year()
            .signal_conversion()
            .opportunity_utilization()
            .trade_density()
            .holding_occupancy()
            .idle_time_ratio()
            .opportunity_coverage()
            .capacity_score()
            .opportunity_velocity()
            .trade_availability()
            .signal_saturation()
            .execution_efficiency()
            .market_coverage()
            .opportunity_quality()
            .capacity_utilization()
            .annual_signal_efficiency()
            .trade_opportunity_ratio()
            .opportunity_persistence()
            .execution_consistency()
            .institutional_opportunity_score()
            .opportunity_rank()
            .normalize_scores()
            .cleanup()
            .round_metrics()
            .df
        )


# ============================================================
# Convenience Function
# ============================================================


def derive_opportunity_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main entry point for
    opportunity metrics.
    """

    return OpportunityMetrics(df).run()
