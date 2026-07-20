"""
===============================================================
Institutional Strategy Comparison Engine V3

Module
------
exit_metrics.py

Purpose
-------
Derive exit behaviour metrics from backtest results.

Author
------
OpenAI

===============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ===============================================================
# Utility Functions
# ===============================================================


def numeric(series):
    """
    Convert a Series to numeric.
    Invalid values become NaN.
    """
    return pd.to_numeric(series, errors="coerce")


def safe_divide(a, b):
    """
    Division without divide-by-zero.
    """

    a = numeric(a)
    b = numeric(b)

    return np.where((b == 0) | (pd.isna(b)), np.nan, a / b)


# ===============================================================
# Exit Metrics Engine
# ===============================================================


class ExitMetrics:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # -----------------------------------------------------------

    def prepare_columns(self):
        cols = ["Trades", "Target #", "Trail #", "Stop #", "Time #", "Win%", "Avg days"]

        for col in cols:
            if col in self.df.columns:
                self.df[col] = numeric(self.df[col])

        return self

    # -----------------------------------------------------------

    def target_exit_pct(self):
        """
        Percentage of exits
        through Target.
        """

        self.df["Target Exit %"] = (
            safe_divide(self.df["Target #"], self.df["Trades"]) * 100
        )

        return self

    # -----------------------------------------------------------

    def trailing_exit_pct(self):
        self.df["Trailing Exit %"] = (
            safe_divide(self.df["Trail #"], self.df["Trades"]) * 100
        )

        return self

    # -----------------------------------------------------------

    def stop_exit_pct(self):
        self.df["Stop Exit %"] = safe_divide(self.df["Stop #"], self.df["Trades"]) * 100

        return self

    # -----------------------------------------------------------

    def time_exit_pct(self):
        self.df["Time Exit %"] = safe_divide(self.df["Time #"], self.df["Trades"]) * 100

        return self

    # -----------------------------------------------------------

    def winning_exit_pct(self):
        """
        Winning exits are

        Target +

        Trail

        """

        winners = self.df["Target #"] + self.df["Trail #"]

        self.df["Winning Exit %"] = safe_divide(winners, self.df["Trades"]) * 100

        return self

    # -----------------------------------------------------------

    def losing_exit_pct(self):
        """
        Losing exits

        Stop +

        Time

        """

        losers = self.df["Stop #"] + self.df["Time #"]

        self.df["Losing Exit %"] = safe_divide(losers, self.df["Trades"]) * 100

        return self

    # -----------------------------------------------------------

    def target_capture_ratio(self):
        """
        Target exits
        versus
        winning exits.
        """

        winners = self.df["Target #"] + self.df["Trail #"]

        self.df["Target Capture"] = safe_divide(self.df["Target #"], winners)

        return self

    # -----------------------------------------------------------

    def trailing_capture_ratio(self):
        winners = self.df["Target #"] + self.df["Trail #"]

        self.df["Trailing Capture"] = safe_divide(self.df["Trail #"], winners)

        return self

    # -----------------------------------------------------------

    def stop_dependency(self):
        self.df["Stop Dependency"] = safe_divide(self.df["Stop #"], self.df["Trades"])

        return self

    # -----------------------------------------------------------

    def time_dependency(self):
        """
        Percentage of exits
        caused by timeout.
        """

        self.df["Time Dependency"] = safe_divide(self.df["Time #"], self.df["Trades"])

        return self

    # -----------------------------------------------------------

    def exit_diversity(self):
        """
        Number of exit types
        actually used.
        """

        exit_cols = ["Target #", "Trail #", "Stop #", "Time #"]

        self.df["Exit Diversity"] = (self.df[exit_cols] > 0).sum(axis=1)

        return self

    # -----------------------------------------------------------

    def exit_concentration(self):
        """
        Largest exit type
        as % of all trades.
        """

        exit_cols = ["Target #", "Trail #", "Stop #", "Time #"]

        self.df["Exit Concentration"] = safe_divide(
            self.df[exit_cols].max(axis=1), self.df["Trades"]
        )

        return self

    # -----------------------------------------------------------

    def exit_balance(self):
        """
        Measures balance
        between winning
        and losing exits.
        """

        winners = self.df["Target #"] + self.df["Trail #"]

        losers = self.df["Stop #"] + self.df["Time #"]

        self.df["Exit Balance"] = 1 - np.abs(
            safe_divide(winners, self.df["Trades"])
            - safe_divide(losers, self.df["Trades"])
        )

        return self

    # -----------------------------------------------------------

    def exit_entropy(self):
        """
        Shannon entropy of
        exit distribution.
        """

        exits = self.df[["Target #", "Trail #", "Stop #", "Time #"]].copy()

        totals = exits.sum(axis=1)

        probs = exits.div(totals, axis=0)

        entropy = -(probs * np.log2(probs.replace(0, np.nan))).sum(axis=1)

        self.df["Exit Entropy"] = entropy

        return self

    # -----------------------------------------------------------

    def exit_stability(self):
        """
        Higher entropy
        implies more
        diversified exits.
        """

        self.df["Exit Stability"] = safe_divide(self.df["Exit Entropy"], np.log2(4))

        return self

    # -----------------------------------------------------------

    def exit_efficiency(self):
        """
        Winning exits
        per average
        holding day.
        """

        self.df["Exit Efficiency"] = safe_divide(
            self.df["Winning Exit %"], self.df["Avg days"]
        )

        return self

    # -----------------------------------------------------------

    def exit_robustness(self):
        """
        Penalize strategies
        relying heavily
        on stop exits.
        """

        self.df["Exit Robustness"] = self.df["Winning Exit %"] - self.df["Stop Exit %"]

        return self

    # -----------------------------------------------------------

    def exit_consistency(self):
        """
        Ratio of
        target exits
        to stop exits.
        """

        self.df["Exit Consistency"] = safe_divide(
            self.df["Target #"], self.df["Stop #"]
        )

        return self

    # -----------------------------------------------------------

    def exit_quality(self):
        """
        Composite quality
        of exit behaviour.
        """

        self.df["Exit Quality"] = (
            (self.df["Winning Exit %"] * 0.40)
            + (self.df["Target Exit %"] * 0.25)
            + (self.df["Trailing Exit %"] * 0.15)
            + (self.df["Exit Stability"] * 100 * 0.20)
        )

        return self

    # -----------------------------------------------------------

    def institutional_exit_score(self):
        """
        Institutional score
        scaled 0-100.
        """

        score = (
            self.df["Exit Quality"]
            - self.df["Stop Exit %"] * 0.20
            - self.df["Time Exit %"] * 0.10
        )

        self.df["Institutional Exit Score"] = score.clip(0, 100)

        return self

    # -----------------------------------------------------------

    def cleanup(self):
        """
        Clean invalid values before returning.
        """

        self.df.replace([np.inf, -np.inf], np.nan, inplace=True)

        metric_cols = [
            "Target Exit %",
            "Trailing Exit %",
            "Stop Exit %",
            "Time Exit %",
            "Winning Exit %",
            "Losing Exit %",
            "Target Capture",
            "Trailing Capture",
            "Stop Dependency",
            "Time Dependency",
            "Exit Diversity",
            "Exit Concentration",
            "Exit Balance",
            "Exit Entropy",
            "Exit Stability",
            "Exit Efficiency",
            "Exit Robustness",
            "Exit Consistency",
            "Exit Quality",
            "Institutional Exit Score",
        ]

        for col in metric_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(0)

        return self

    # -----------------------------------------------------------

    def round_metrics(self):
        """
        Round derived metrics.
        """

        metric_cols = [
            "Target Exit %",
            "Trailing Exit %",
            "Stop Exit %",
            "Time Exit %",
            "Winning Exit %",
            "Losing Exit %",
            "Target Capture",
            "Trailing Capture",
            "Stop Dependency",
            "Time Dependency",
            "Exit Diversity",
            "Exit Concentration",
            "Exit Balance",
            "Exit Entropy",
            "Exit Stability",
            "Exit Efficiency",
            "Exit Robustness",
            "Exit Consistency",
            "Exit Quality",
            "Institutional Exit Score",
        ]

        for col in metric_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].round(4)

        return self

    # -----------------------------------------------------------

    def run(self):
        return (
            self.prepare_columns()
            .target_exit_pct()
            .trailing_exit_pct()
            .stop_exit_pct()
            .time_exit_pct()
            .winning_exit_pct()
            .losing_exit_pct()
            .target_capture_ratio()
            .trailing_capture_ratio()
            .stop_dependency()
            .time_dependency()
            .exit_diversity()
            .exit_concentration()
            .exit_balance()
            .exit_entropy()
            .exit_stability()
            .exit_efficiency()
            .exit_robustness()
            .exit_consistency()
            .exit_quality()
            .institutional_exit_score()
            .cleanup()
            .round_metrics()
            .df
        )


# ===============================================================
# Convenience Function
# ===============================================================


def derive_exit_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive all exit-related institutional metrics.
    """

    return ExitMetrics(df).run()
