"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
performance_metrics.py

Purpose
-------
Derive institutional performance metrics from backtest
results.

Input
-----
Summary DataFrame containing:

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
Original dataframe + derived performance metrics

===============================================================
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================
# Utility Functions
# ============================================================


def numeric(value):
    """
    Safe numeric conversion.
    """

    return pd.to_numeric(
        value,
        errors="coerce",
    ).replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )


def safe_divide(a, b):
    """
    Safe division.
    """

    a = numeric(a)

    b = numeric(b)

    result = np.where(
        (b == 0) | pd.isna(b),
        np.nan,
        a / b,
    )

    return pd.Series(result).replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )


# ============================================================
# Performance Metrics Engine
# ============================================================


class PerformanceMetrics:
    REQUIRED_COLUMNS = {
        "Trades",
        "Years",
        "Win%",
    }

    def __init__(
        self,
        df: pd.DataFrame,
    ):

        self.df = df.copy()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def validate(self):

        missing = self.REQUIRED_COLUMNS - set(self.df.columns)

        if missing:
            raise KeyError(f"Missing required columns: {sorted(missing)}")

        return self

    # --------------------------------------------------------
    # Column Preparation
    # --------------------------------------------------------

    def prepare_columns(self):

        aliases = {
            "Avg Win %": "Avg win%",
            "Average Win %": "Avg win%",
            "Avg Loss %": "Avg loss%",
            "Average Loss %": "Avg loss%",
            "Maximum Drawdown %": "Max Drawdown %",
            "Max Drawdown": "Max Drawdown %",
            "Total Return %": "Net %",
            "Net Profit %": "Net %",
        }

        for source, target in aliases.items():
            if source in self.df.columns and target not in self.df.columns:
                self.df[target] = self.df[source]

        numeric_columns = [
            "Trades",
            "Years",
            "Win%",
            "Net %",
            "Annual Return %",
            "Reward Risk",
            "Profit Factor",
            "Expectancy",
            "Avg win%",
            "Avg loss%",
            "Avg days",
            "Expectancy%",
        ]

        for column in numeric_columns:
            if column in self.df.columns:
                self.df[column] = numeric(self.df[column])

        return self

    # --------------------------------------------------------
    # Annual Trades
    # --------------------------------------------------------

    def annual_trades(self):

        self.df["Trades / Year"] = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        return self

    # --------------------------------------------------------
    # Annual Return (CAGR)
    # --------------------------------------------------------

    def annual_return(self):

        if "Annual Return %" in self.df.columns:
            return self

        if "Net %" in self.df.columns and "Years" in self.df.columns:
            total_return = numeric(self.df["Net %"])

            years = numeric(self.df["Years"])

            self.df["Annual Return %"] = (
                (
                    1 + total_return / 100
                )
                **
                (
                    1 / years
                )
                - 1
            ) * 100

        return self

    # --------------------------------------------------------
    # Reward Risk
    # --------------------------------------------------------

    def reward_risk(self):

        if "Reward Risk" in self.df.columns:
            return self

        self.df["Reward Risk"] = safe_divide(
            self.df["Avg win%"],
            self.df["Avg loss%"].abs(),
        )

        return self

    # --------------------------------------------------------
    # Expectancy
    # --------------------------------------------------------

    def expectancy(self):

        if "Expectancy" in self.df.columns:
            return self

        win_rate = self.df["Win%"] / 100

        loss_rate = 1 - win_rate

        self.df["Expectancy"] = (
            win_rate * self.df["Avg win%"] - loss_rate * self.df["Avg loss%"].abs()
        )

        return self

    # --------------------------------------------------------
    # Profit Factor
    # --------------------------------------------------------

    def profit_factor(self):

        if "Profit Factor" in self.df.columns:
            return self

        gross_profit = self.df["Trades"] * self.df["Win%"] / 100 * self.df["Avg win%"]

        gross_loss = (
            self.df["Trades"] * (1 - self.df["Win%"] / 100) * self.df["Avg loss%"].abs()
        )

        self.df["Profit Factor"] = safe_divide(
            gross_profit,
            gross_loss,
        )

        return self

    # --------------------------------------------------------
    # Return Per Trade
    # --------------------------------------------------------

    def return_per_trade(self):

        value = self.df["Net %"] if "Net %" in self.df.columns else np.nan

        self.df["Return / Trade"] = safe_divide(
            value,
            self.df["Trades"],
        )

        return self

    # --------------------------------------------------------
    # Return Per Day
    # --------------------------------------------------------

    def return_per_day(self):

        if (
            "Annual Return %" not in self.df.columns
            or "Avg days" not in self.df.columns
        ):
            self.df["Return / Day"] = np.nan
            return self


        self.df["Return / Day"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Avg days"],
        )


        return self


    # --------------------------------------------------------
    # Holding Efficiency
    # --------------------------------------------------------

    def holding_efficiency(self):

        if (
            "Annual Return %" not in self.df.columns
            or "Avg days" not in self.df.columns
        ):
            self.df["Holding Efficiency"] = np.nan
            return self


        self.df["Holding Efficiency"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Avg days"],
        )


        return self
    
    # --------------------------------------------------------
    # Profit Velocity
    # --------------------------------------------------------

    def profit_velocity(self):

        self.df["Profit Velocity"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Avg days"],
        )

        return self

    # --------------------------------------------------------
    # Win Loss Ratio
    # --------------------------------------------------------

    def win_loss_ratio(self):

        wins = self.df["Trades"] * self.df["Win%"] / 100

        losses = self.df["Trades"] - wins

        self.df["Win Loss Ratio"] = safe_divide(
            wins,
            losses,
        )

        return self

    # --------------------------------------------------------
    # Expectancy Ratio
    # --------------------------------------------------------

    def expectancy_ratio(self):

        self.df["Expectancy Ratio"] = safe_divide(
            self.df["Expectancy"],
            self.df["Avg loss%"].abs(),
        )

        return self

    # --------------------------------------------------------
    # Capital Turnover
    # --------------------------------------------------------

    def capital_turnover(self):

        if (
            "Trades / Year" not in self.df.columns
            or "Avg days" not in self.df.columns
        ):
            self.df["Capital Turnover Proxy"] = np.nan
            return self


        self.df["Capital Turnover Proxy"] = (
            safe_divide(
                self.df["Trades / Year"] * 365,
                self.df["Avg days"],
            )
        )


        return self
    
    # --------------------------------------------------------
    # Edge Per Trade
    # --------------------------------------------------------

    def edge_per_trade(self):

        if "Expectancy" not in self.df.columns:
            self.df["Edge / Trade"] = np.nan
            return self


        self.df["Edge / Trade"] = (
            self.df["Expectancy"]
        )

        return self

    # --------------------------------------------------------
    # Annual Edge
    # --------------------------------------------------------

    def annual_edge(self):

        self.df["Annual Edge"] = self.df["Expectancy"] * self.df["Trades / Year"]

        return self

    # --------------------------------------------------------
    # Return Consistency
    # --------------------------------------------------------

    def edge_consistency(self):

        self.df["Edge Consistency"] = safe_divide(
            self.df["Expectancy"],
            self.df["Avg loss%"].abs(),
        )

        return self
    
    # --------------------------------------------------------
    # Trade Efficiency
    # --------------------------------------------------------

    def trade_efficiency(self):

        self.df["Trade Efficiency"] = self.df["Reward Risk"] * self.df["Win%"] / 100

        return self

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    def score_inputs(self):

        columns = [
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Profit Velocity",
            "Trade Efficiency",
            "Holding Efficiency",
        ]

        for column in columns:
            if column in self.df.columns:
                self.df[column] = (
                    self.df[column]
                    .replace(
                        [
                            np.inf,
                            -np.inf,
                        ],
                        np.nan,
                    )
                    .fillna(0.0)
                )

        return self

    # --------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------

    def run(self):

        logger.info("Calculating performance metrics")

        result = (
            self.prepare_columns()
            .validate()
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
            .edge_consistency()
            .trade_efficiency()
            .score_inputs()
            .df
        )

        logger.info("Performance metrics completed")

        return result


# ============================================================
# Convenience Function
# ============================================================


def derive_performance_metrics(
    df: pd.DataFrame,
):
    """
    Main entry point.
    """

    return PerformanceMetrics(df).run()
