"""
===========================================================
Institutional Strategy Comparison Engine V3
Module : performance_metrics.py
Author : OpenAI

Purpose
-------
Derive institutional performance metrics from backtest
results.

All calculations are vectorized using pandas/numpy.

Input
-----
DataFrame containing columns such as

Trades
Years
Win%
Net %
Avg win%
Avg loss%
Avg days
Expectancy%

Output
------
Original dataframe + derived metrics

===========================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ----------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------


def numeric(series):
    """
    Convert any column to numeric.
    Invalid values become NaN.
    """
    return pd.to_numeric(series, errors="coerce")


def safe_divide(a, b):
    """
    Safe division avoiding divide-by-zero.
    """
    a = numeric(a)
    b = numeric(b)

    return np.where(b == 0, np.nan, a / b)


# ----------------------------------------------------------
# Performance Metrics Engine
# ----------------------------------------------------------


class PerformanceMetrics:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # ------------------------------------------------------

    def prepare_columns(self):
        # Normalize legacy column names

        rename_map = {
            "Avg Win %": "Avg win%",
            "Avg Loss %": "Avg loss%",
        }

        for new_name, legacy_name in rename_map.items():
            if new_name in self.df.columns and legacy_name not in self.df.columns:
                self.df[legacy_name] = self.df[new_name]

        numeric_cols = [
            "Trades",
            "Years",
            "Win%",
            "Net %",
            "Annual Return %",
            "Reward Risk",
            "Profit Factor",
            "Expectancy",
            "Avg Win %",
            "Avg Loss %",
            "Avg win%",
            "Avg loss%",
            "Avg days",
            "Expectancy%",
        ]

        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = numeric(self.df[col])

        return self

    # ------------------------------------------------------

    def annual_trades(self):
        self.df["Trades / Year"] = safe_divide(self.df["Trades"], self.df["Years"])

        return self

    # ------------------------------------------------------

    def annual_return(self):
        # Already calculated by Summary Engine
        if "Annual Return %" in self.df.columns:
            return self

        # Legacy Statistics.xlsx calculation
        if "Net %" in self.df.columns:
            self.df["Annual Return %"] = safe_divide(
                self.df["Net %"],
                self.df["Years"],
            )

        return self

    # ------------------------------------------------------

    def reward_risk(self):
        if "Reward Risk" in self.df.columns:
            return self

        avg_win = (
            self.df["Avg Win %"]
            if "Avg Win %" in self.df.columns
            else self.df["Avg win%"]
        )

        avg_loss = (
            self.df["Avg Loss %"]
            if "Avg Loss %" in self.df.columns
            else self.df["Avg loss%"]
        )

        self.df["Reward Risk"] = safe_divide(
            avg_win,
            avg_loss.abs(),
        )

        return self

    # ------------------------------------------------------

    def expectancy(self):
        if "Expectancy" in self.df.columns:
            return self

        avg_win = (
            self.df["Avg Win %"]
            if "Avg Win %" in self.df.columns
            else self.df["Avg win%"]
        )

        avg_loss = (
            self.df["Avg Loss %"]
            if "Avg Loss %" in self.df.columns
            else self.df["Avg loss%"]
        )

        win_rate = self.df["Win%"] / 100
        loss_rate = 1 - win_rate

        self.df["Expectancy"] = win_rate * avg_win - loss_rate * avg_loss.abs()

        return self

    # ------------------------------------------------------

    def profit_factor(self):
        if "Profit Factor" in self.df.columns:
            return self

        avg_win = (
            self.df["Avg Win %"]
            if "Avg Win %" in self.df.columns
            else self.df["Avg win%"]
        )

        avg_loss = (
            self.df["Avg Loss %"]
            if "Avg Loss %" in self.df.columns
            else self.df["Avg loss%"]
        )

        gross_profit = self.df["Trades"] * (self.df["Win%"] / 100) * avg_win

        gross_loss = self.df["Trades"] * (1 - self.df["Win%"] / 100) * avg_loss.abs()

        self.df["Profit Factor"] = safe_divide(
            gross_profit,
            gross_loss,
        )

        return self

    # ------------------------------------------------------

    def return_per_trade(self):
        if "Net %" in self.df.columns:
            self.df["Return / Trade"] = safe_divide(self.df["Net %"], self.df["Trades"])

        elif "Annual Return %" in self.df.columns:
            self.df["Return / Trade"] = safe_divide(
                self.df["Annual Return %"], self.df["Trades / Year"]
            )

        else:
            self.df["Return / Trade"] = np.nan

        return self

    # ------------------------------------------------------

    def return_per_day(self):
        total_days = self.df["Trades"] * self.df["Avg days"]

        if "Net %" in self.df.columns:
            value = self.df["Net %"]

        elif "Annual Return %" in self.df.columns:
            value = self.df["Annual Return %"] * self.df["Years"]

        else:
            value = np.nan

        self.df["Return / Day"] = safe_divide(value, total_days)

        return self

    # ------------------------------------------------------

    def holding_efficiency(self):
        if "Net %" in self.df.columns:
            value = self.df["Net %"]

        elif "Annual Return %" in self.df.columns:
            value = self.df["Annual Return %"] * self.df["Years"]

        else:
            value = np.nan

        self.df["Holding Efficiency"] = safe_divide(value, self.df["Avg days"])

        return self

    # ------------------------------------------------------

    def profit_velocity(self):
        self.df["Profit Velocity"] = safe_divide(
            self.df["Annual Return %"], self.df["Avg days"]
        )

        return self

    # ------------------------------------------------------

    def win_loss_ratio(self):
        wins = self.df["Trades"] * self.df["Win%"] / 100

        losses = self.df["Trades"] - wins

        self.df["Win Loss Ratio"] = safe_divide(wins, losses)

        return self

    # ------------------------------------------------------

    def expectancy_ratio(self):
        avg_loss = (
            self.df["Avg Loss %"]
            if "Avg Loss %" in self.df.columns
            else self.df["Avg loss%"]
        )

        self.df["Expectancy Ratio"] = safe_divide(self.df["Expectancy"], avg_loss.abs())

        return self

    # ------------------------------------------------------

    def capital_turnover(self):
        self.df["Capital Turnover"] = safe_divide(
            self.df["Trades"], self.df["Avg days"]
        )

        return self

    # ------------------------------------------------------

    def edge_per_trade(self):
        self.df["Edge / Trade"] = safe_divide(self.df["Expectancy"], self.df["Trades"])

        return self

    # ------------------------------------------------------

    def annual_edge(self):
        self.df["Annual Edge"] = self.df["Expectancy"] * self.df["Trades / Year"]

        return self

    # ------------------------------------------------------

    def return_consistency(self):
        self.df["Return Consistency"] = safe_divide(
            self.df["Annual Return %"], self.df["Profit Velocity"]
        )

        return self

    # ------------------------------------------------------

    def trade_efficiency(self):
        self.df["Trade Efficiency"] = self.df["Reward Risk"] * self.df["Win%"] / 100

        return self

    # ------------------------------------------------------

    def score_inputs(self):
        cols = [
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Profit Velocity",
            "Trade Efficiency",
            "Holding Efficiency",
        ]

        for c in cols:
            self.df[c] = self.df[c].replace([np.inf, -np.inf], np.nan)

        return self

    # ------------------------------------------------------

    def run(self):
        return (
            self.prepare_columns()
            .annual_trades()
            .annual_return()
            .reward_risk()
            .expectancy()
            .profit_factor()
            .return_per_trade()
            .return_per_day()
            .holding_efficiency()
            .profit_velocity()
            .win_loss_ratio()
            .expectancy_ratio()
            .capital_turnover()
            .edge_per_trade()
            .annual_edge()
            .return_consistency()
            .trade_efficiency()
            .score_inputs()
            .df
        )


# ----------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------


def derive_performance_metrics(df: pd.DataFrame):
    """
    Main entry point.
    """

    return PerformanceMetrics(df).run()
