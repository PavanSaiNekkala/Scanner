"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
risk_metrics.py

Purpose
-------
Derive institutional risk metrics from strategy statistics.

Institutional Risk Metrics
--------------------------
- Annual Loss
- Loss Velocity
- Downside Risk
- Drawdown Proxy
- Risk Adjusted Return
- Recovery Factor
- Capital Preservation
- Safety Margin
- Risk Quality

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
    Convert values safely to numeric.

    Invalid values become NaN.
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

    Handles:
    - Series / Series
    - Series / scalar
    - invalid divisions
    """

    a = numeric(a)

    b = numeric(b)

    result = np.divide(
        a,
        b,
        out=np.full_like(
            np.asarray(a, dtype=float),
            np.nan,
            dtype=float,
        ),
        where=(np.asarray(b) != 0),
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
    """
    Institutional Risk Calculation Engine.
    """

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
    # Column Preparation
    # --------------------------------------------------------

    def prepare_columns(self):
        """
        Normalize legacy columns.
        """

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
        """
        Annualized loss exposure.

        Formula:

        Average Loss × Loss Frequency

        """

        if "Losses" in self.df.columns:
            loss_frequency = safe_divide(
                self.df["Losses"],
                self.df["Years"],
            )

        else:
            loss_frequency = safe_divide(
                self.df["Trades"],
                self.df["Years"],
            )

        self.df["Annual Loss %"] = self.df["Avg loss%"].abs() * loss_frequency

        return self

    # --------------------------------------------------------
    # Loss Velocity
    # --------------------------------------------------------

    def loss_velocity(self):
        """
        Loss generated per holding day.
        """

        self.df["Loss Velocity"] = safe_divide(
            self.df["Avg loss%"].abs(),
            self.df["Avg days"],
        )

        return self

    # --------------------------------------------------------
    # Downside Risk
    # --------------------------------------------------------

    def downside_risk(self):
        """
        Trade frequency adjusted downside risk.

        """

        trade_frequency = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        self.df["Downside Risk"] = self.df["Avg loss%"].abs() * np.sqrt(
            trade_frequency.clip(lower=0)
        )

        return self

    # --------------------------------------------------------
    # Drawdown Proxy
    # --------------------------------------------------------

    def drawdown_proxy(self):
        """
        Estimate drawdown risk.

        Priority:

        1. Actual Max Drawdown %
        2. Trade-loss based estimate

        """

        if "Max Drawdown %" in self.df.columns:
            drawdown = self.df["Max Drawdown %"].abs()

        else:
            drawdown = self.df["Avg loss%"].abs() * np.log1p(self.df["Trades"])

        self.df["Drawdown Proxy"] = drawdown

        return self

    # --------------------------------------------------------
    # Risk Adjusted Return
    # --------------------------------------------------------

    def risk_adjusted_return(self):
        """
        Return generated per unit drawdown.

        Similar to Calmar Ratio.

        Formula:

        CAGR / Maximum Drawdown

        """

        if "Annual Return %" in self.df.columns:
            annual_return = self.df["Annual Return %"]

        else:
            annual_return = np.nan

        self.df["Risk Adjusted Return"] = safe_divide(
            annual_return,
            self.df["Drawdown Proxy"],
        )

        return self

    # --------------------------------------------------------
    # Stop Efficiency
    # --------------------------------------------------------

    def stop_efficiency(self):
        """
        Measures exit efficiency.

        Formula:

        Average Loss / Stop Loss

        Higher is worse.
        """

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
        """
        Reward to loss relationship.

        NOTE:
        Column retained for backward compatibility.

        Formula:

        Average Win / Average Loss

        """

        self.df["Downside Capture"] = safe_divide(
            self.df["Avg win%"],
            self.df["Avg loss%"].abs(),
        )

        return self

    # --------------------------------------------------------
    # Tail Risk
    # --------------------------------------------------------

    def tail_risk(self):
        """
        Approximate tail risk.

        Current implementation:

        Loss magnitude adjusted by holding duration.

        Future upgrade:

        Replace with CVaR 95%.

        """

        holding_factor = np.sqrt(self.df["Avg days"].clip(lower=0))

        self.df["Tail Risk"] = self.df["Avg loss%"].abs() * holding_factor

        return self

    # --------------------------------------------------------
    # Risk Reward Balance
    # --------------------------------------------------------

    def risk_reward_balance(self):
        """
        Reward generated per unit tail risk.

        """

        self.df["Risk Reward Balance"] = safe_divide(
            self.df["Reward Risk"],
            self.df["Tail Risk"],
        )

        return self

    # --------------------------------------------------------
    # Annual Risk
    # --------------------------------------------------------

    def annual_risk(self):
        """
        Annualized downside exposure.

        Formula:

        Downside Risk × sqrt(trades/year)

        """

        trade_frequency = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        self.df["Annual Risk"] = self.df["Downside Risk"] * np.sqrt(
            trade_frequency.clip(lower=0)
        )

        return self

    # --------------------------------------------------------
    # Loss Consistency
    # --------------------------------------------------------

    def loss_consistency(self):
        """
        Measures stability of losses.

        Higher means losses are
        more consistently controlled.

        """

        self.df["Loss Consistency"] = safe_divide(
            self.df["Annual Loss %"],
            self.df["Downside Risk"],
        )

        return self

    # --------------------------------------------------------
    # Recovery Factor
    # --------------------------------------------------------

    def recovery_factor(self):
        """
        Recovery capability.

        Formula:

        Net Profit / Maximum Drawdown

        """

        net_return = self.df["Net %"] if "Net %" in self.df.columns else np.nan

        self.df["Recovery Factor"] = safe_divide(
            net_return,
            self.df["Drawdown Proxy"],
        )

        return self

    # --------------------------------------------------------
    # Capital Preservation
    # --------------------------------------------------------

    def capital_preservation(self):
        """
        Measures return generated
        against annual risk.

        """

        self.df["Capital Preservation"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Annual Risk"],
        )

        return self

    # --------------------------------------------------------
    # Safety Margin
    # --------------------------------------------------------

    def safety_margin(self):
        """
        Risk buffer.

        Formula:

        Reward Risk - Loss Velocity

        """

        self.df["Safety Margin"] = self.df["Reward Risk"] - self.df["Loss Velocity"]

        return self

    # --------------------------------------------------------
    # Risk Quality
    # --------------------------------------------------------

    def risk_quality(self):
        """
        Composite institutional risk quality.

        Components:

        - Risk Adjusted Return
        - Recovery Factor
        - Capital Preservation
        - Loss Consistency

        """

        self.df["Risk Quality"] = (
            self.df["Risk Adjusted Return"] * 0.30
            + self.df["Recovery Factor"] * 0.25
            + self.df["Capital Preservation"] * 0.25
            + self.df["Loss Consistency"] * 0.20
        )

        return self

    # --------------------------------------------------------
    # Risk Efficiency
    # --------------------------------------------------------

    def risk_efficiency(self):
        """
        Measures return generated
        against risk taken.

        """

        self.df["Risk Efficiency"] = safe_divide(
            self.df["Risk Quality"],
            self.df["Annual Risk"],
        )

        return self

    # --------------------------------------------------------
    # Risk Score
    # --------------------------------------------------------

    def risk_score(self):
        """
        Institutional risk score.

        Higher is better.

        """

        self.df["Risk Score"] = (
            self.df["Risk Adjusted Return"] * 0.30
            + self.df["Recovery Factor"] * 0.25
            + self.df["Capital Preservation"] * 0.25
            + self.df["Safety Margin"] * 0.20
        )

        return self

    # --------------------------------------------------------
    # Normalization
    # --------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize risk metrics.

        Scale:

        0 - 100

        """

        metrics = [
            "Risk Adjusted Return",
            "Recovery Factor",
            "Capital Preservation",
            "Risk Quality",
            "Risk Efficiency",
            "Risk Score",
        ]

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            minimum = self.df[metric].min()

            maximum = self.df[metric].max()

            if pd.isna(minimum) or pd.isna(maximum):
                continue

            if maximum == minimum:
                self.df[f"{metric} Norm"] = 50.0

            else:
                self.df[f"{metric} Norm"] = (
                    (self.df[metric] - minimum) / (maximum - minimum) * 100
                )

        return self

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    def cleanup(self):
        """
        Clean invalid values.
        """

        derived_columns = [
            "Annual Loss %",
            "Loss Velocity",
            "Downside Risk",
            "Drawdown Proxy",
            "Risk Adjusted Return",
            "Stop Efficiency",
            "Downside Capture",
            "Tail Risk",
            "Risk Reward Balance",
            "Annual Risk",
            "Loss Consistency",
            "Recovery Factor",
            "Capital Preservation",
            "Safety Margin",
            "Risk Quality",
            "Risk Efficiency",
            "Risk Score",
        ]

        for column in derived_columns:
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
    # Rounding
    # --------------------------------------------------------

    def round_metrics(self):
        """
        Round derived metrics.
        """

        columns = [
            "Annual Loss %",
            "Loss Velocity",
            "Downside Risk",
            "Drawdown Proxy",
            "Risk Adjusted Return",
            "Stop Efficiency",
            "Downside Capture",
            "Tail Risk",
            "Risk Reward Balance",
            "Annual Risk",
            "Loss Consistency",
            "Recovery Factor",
            "Capital Preservation",
            "Safety Margin",
            "Risk Quality",
            "Risk Efficiency",
            "Risk Score",
        ]

        for column in columns:
            if column in self.df.columns:
                self.df[column] = self.df[column].round(4)

        return self

    # --------------------------------------------------------
    # Execution Pipeline
    # --------------------------------------------------------

    def run(self):
        """
        Execute complete risk pipeline.
        """

        logger.info("Calculating institutional risk metrics")

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
            .risk_quality()
            .risk_efficiency()
            .risk_score()
            .normalize_scores()
            .cleanup()
            .round_metrics()
            .df
        )

        logger.info("Risk metrics completed")

        return result


# ============================================================
# Convenience API
# ============================================================


def derive_risk_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Public risk metric interface.
    """

    return RiskMetrics(df).run()


__all__ = [
    "RiskMetrics",
    "derive_risk_metrics",
]
