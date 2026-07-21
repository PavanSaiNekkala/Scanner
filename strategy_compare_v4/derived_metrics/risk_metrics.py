"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
risk_metrics.py

Purpose
-------
Derive institutional risk metrics from backtest results.

Metrics Covered
---------------
- Annual Loss
- Loss Velocity
- Downside Risk
- Drawdown Proxy
- Risk Adjusted Return
- Tail Risk
- Recovery Factor
- Capital Preservation
- Safety Margin

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
# Risk Metrics Engine
# ============================================================


class RiskMetrics:
    REQUIRED_COLUMNS = {
        "Trades",
        "Years",
        "Avg loss%",
        "Avg win%",
        "Reward Risk",
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
    # Prepare Columns
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
            "Net %",
            "Avg loss%",
            "Avg win%",
            "Avg days",
            "Stop %",
            "Reward Risk",
            "Profit Factor",
            "Annual Return %",
            "Holding Efficiency",
            "Max Drawdown %",
        ]

        for column in numeric_columns:
            if column in self.df.columns:
                self.df[column] = numeric(self.df[column])

        return self

    # --------------------------------------------------------
    # Annual Loss
    # --------------------------------------------------------

    def annual_loss(self):

        self.df["Annual Loss %"] = self.df["Avg loss%"].abs() * safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        return self

    # --------------------------------------------------------
    # Loss Velocity
    # --------------------------------------------------------

    def loss_velocity(self):

        self.df["Loss Velocity"] = safe_divide(
            self.df["Avg loss%"].abs(),
            self.df["Avg days"],
        )

        return self

    # --------------------------------------------------------
    # Downside Risk
    # --------------------------------------------------------

    def downside_risk(self):

        trade_frequency = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        self.df["Downside Risk"] = self.df["Avg loss%"].abs() * np.sqrt(
            trade_frequency.clip(
                lower=0,
            )
        )

        return self

    # --------------------------------------------------------
    # Drawdown Proxy
    # --------------------------------------------------------

    def drawdown_proxy(self):

        if "Max Drawdown %" in self.df.columns:
            self.df["Drawdown Proxy"] = self.df["Max Drawdown %"].abs()

        else:
            self.df["Drawdown Proxy"] = self.df["Avg loss%"].abs() * np.log1p(
                self.df["Trades"]
            )

        return self

    # --------------------------------------------------------
    # Risk Adjusted Return
    # --------------------------------------------------------

    def risk_adjusted_return(self):

        self.df["Risk Adjusted Return"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Drawdown Proxy"],
        )

        return self

    # --------------------------------------------------------
    # Stop Efficiency
    # --------------------------------------------------------

    def stop_efficiency(self):

        if "Stop %" in self.df.columns:
            self.df["Stop Efficiency"] = safe_divide(
                self.df["Avg loss%"].abs(),
                self.df["Stop %"].abs(),
            )

        else:
            self.df["Stop Efficiency"] = np.nan

        return self

    # --------------------------------------------------------
    # Downside Capture
    # --------------------------------------------------------

    def downside_capture(self):

        self.df["Downside Capture"] = safe_divide(
            self.df["Avg win%"],
            self.df["Avg loss%"].abs(),
        )

        return self

    # --------------------------------------------------------
    # Tail Risk
    # --------------------------------------------------------

    def tail_risk(self):

        days = self.df["Avg days"] if "Avg days" in self.df.columns else 1

        self.df["Tail Risk"] = self.df["Avg loss%"].abs() * np.sqrt(days)

        return self

    # --------------------------------------------------------
    # Risk Reward Balance
    # --------------------------------------------------------

    def risk_reward_balance(self):

        self.df["Risk Reward Balance"] = safe_divide(
            self.df["Reward Risk"],
            self.df["Tail Risk"],
        )

        return self

    # --------------------------------------------------------
    # Annual Risk
    # --------------------------------------------------------

    def annual_risk(self):

        trade_frequency = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        self.df["Annual Risk"] = self.df["Drawdown Proxy"] * np.sqrt(
            trade_frequency.clip(
                lower=0,
            )
        )

        return self

    # --------------------------------------------------------
    # Loss Consistency
    # --------------------------------------------------------

    def loss_consistency(self):

        self.df["Loss Consistency"] = safe_divide(
            self.df["Annual Loss %"],
            self.df["Downside Risk"],
        )

        return self

    # --------------------------------------------------------
    # Recovery Factor
    # --------------------------------------------------------

    def recovery_factor(self):

        if "Net %" in self.df.columns:
            value = self.df["Net %"]

        elif "Annual Return %" in self.df.columns:
            value = self.df["Annual Return %"] * self.df["Years"]

        else:
            value = np.nan

        self.df["Recovery Factor"] = safe_divide(
            value,
            self.df["Drawdown Proxy"],
        )

        return self

    # --------------------------------------------------------
    # Capital Preservation
    # --------------------------------------------------------

    def capital_preservation(self):

        self.df["Capital Preservation"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Annual Risk"],
        )

        return self

    # --------------------------------------------------------
    # Safety Margin
    # --------------------------------------------------------

    def safety_margin(self):

        self.df["Safety Margin"] = self.df["Reward Risk"] - self.df["Loss Velocity"]

        return self

    # --------------------------------------------------------
    # Downside Efficiency
    # --------------------------------------------------------

    def downside_efficiency(self):

        self.df["Downside Efficiency"] = safe_divide(
            self.df["Holding Efficiency"],
            self.df["Tail Risk"],
        )

        return self

    # --------------------------------------------------------
    # Risk Score Inputs
    # --------------------------------------------------------

    def risk_score_inputs(self):

        columns = [
            "Drawdown Proxy",
            "Risk Adjusted Return",
            "Recovery Factor",
            "Capital Preservation",
            "Safety Margin",
            "Tail Risk",
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
    # Run Pipeline
    # --------------------------------------------------------

    def run(self):

        logger.info("Calculating risk metrics")

        result = (
            self.prepare_columns()
            .validate()
            .annual_loss()
            .loss_velocity()
            .downside_risk()
            .drawdown_proxy()
            .risk_adjusted_return()
            .stop_efficiency()
            .downside_capture()
            .tail_risk()
            .risk_reward_balance()
            .annual_risk()
            .loss_consistency()
            .recovery_factor()
            .capital_preservation()
            .safety_margin()
            .downside_efficiency()
            .risk_score_inputs()
            .df
        )

        logger.info("Risk metrics completed")

        return result


# ============================================================
# Convenience Function
# ============================================================


def derive_risk_metrics(
    df: pd.DataFrame,
):

    return RiskMetrics(df).run()
