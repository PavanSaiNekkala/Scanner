"""
===========================================================
Institutional Strategy Comparison Engine V3
Module : risk_metrics.py

Purpose
-------
Derive institutional risk metrics from backtest results.

Author : OpenAI
===========================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------

def numeric(series):
    return pd.to_numeric(series, errors="coerce")


def safe_divide(a, b):

    a = numeric(a)
    b = numeric(b)

    return np.where(
        (b == 0) | (pd.isna(b)),
        np.nan,
        a / b
    )


# ---------------------------------------------------------
# Risk Metrics Engine
# ---------------------------------------------------------

class RiskMetrics:

    def __init__(self, df):

        self.df = df.copy()

    # -----------------------------------------------------

    def prepare_columns(self):

        cols = [

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
            "Holding Efficiency"

        ]

        for c in cols:

            if c in self.df.columns:

                self.df[c] = numeric(self.df[c])

        return self

    # -----------------------------------------------------

    def annual_loss(self):

        self.df["Annual Loss %"] = (

            self.df["Avg loss%"].abs()

            *

            safe_divide(
                self.df["Trades"],
                self.df["Years"]
            )

        )

        return self

    # -----------------------------------------------------

    def loss_velocity(self):

        self.df["Loss Velocity"] = safe_divide(

            self.df["Avg loss%"].abs(),

            self.df["Avg days"]

        )

        return self

    # -----------------------------------------------------

    def downside_risk(self):

        self.df["Downside Risk"] = (

            self.df["Avg loss%"].abs()

            *

            np.sqrt(

                safe_divide(

                    self.df["Trades"],

                    self.df["Years"]

                )

            )

        )

        return self

    # -----------------------------------------------------

    def drawdown_proxy(self):

        self.df["Drawdown Proxy"] = (

            self.df["Avg loss%"].abs()

            *

            np.log1p(

                self.df["Trades"]

            )

        )

        return self

    # -----------------------------------------------------

    def risk_adjusted_return(self):

        self.df["Risk Adjusted Return"] = safe_divide(

            self.df["Annual Return %"],

            self.df["Drawdown Proxy"]

        )

        return self

    # -----------------------------------------------------

    def stop_efficiency(self):

        if "Stop %" in self.df.columns:

            self.df["Stop Efficiency"] = safe_divide(

                self.df["Avg loss%"].abs(),

                self.df["Stop %"].abs()

            )

        else:

            self.df["Stop Efficiency"] = np.nan

        return self

    # -----------------------------------------------------

    def downside_capture(self):

        self.df["Downside Capture"] = safe_divide(

            self.df["Avg win%"],

            self.df["Avg loss%"].abs()

        )

        return self

    # -----------------------------------------------------

    def tail_risk(self):

        self.df["Tail Risk"] = (

            self.df["Avg loss%"].abs()

            *

            np.sqrt(

                self.df["Avg days"]

            )

        )

        return self

    # -----------------------------------------------------

    def risk_reward_balance(self):

        self.df["Risk Reward Balance"] = safe_divide(

            self.df["Reward Risk"],

            self.df["Tail Risk"]

        )

        return self

    # -----------------------------------------------------

    def annual_risk(self):

        self.df["Annual Risk"] = (

            self.df["Drawdown Proxy"]

            *

            safe_divide(

                self.df["Trades"],

                self.df["Years"]

            )

        )

        return self

    # -----------------------------------------------------

    def loss_consistency(self):

        self.df["Loss Consistency"] = safe_divide(

            self.df["Annual Loss %"],

            self.df["Downside Risk"]

        )

        return self

    # -----------------------------------------------------

    def recovery_factor(self):

        self.df["Recovery Factor"] = safe_divide(

            self.df["Net %"],

            self.df["Drawdown Proxy"]

        )

        return self

    # -----------------------------------------------------

    def capital_preservation(self):

        self.df["Capital Preservation"] = safe_divide(

            self.df["Annual Return %"],

            self.df["Annual Risk"]

        )

        return self

    # -----------------------------------------------------

    def safety_margin(self):

        self.df["Safety Margin"] = (

            self.df["Reward Risk"]

            -

            self.df["Loss Velocity"]

        )

        return self

    # -----------------------------------------------------

    def downside_efficiency(self):

        self.df["Downside Efficiency"] = safe_divide(

            self.df["Holding Efficiency"],

            self.df["Tail Risk"]

        )

        return self

    # -----------------------------------------------------

    def risk_score_inputs(self):

        cols = [

            "Drawdown Proxy",
            "Risk Adjusted Return",
            "Recovery Factor",
            "Capital Preservation",
            "Safety Margin",
            "Tail Risk"

        ]

        for c in cols:

            self.df[c] = self.df[c].replace(

                [np.inf, -np.inf],

                np.nan

            )

        return self

    # -----------------------------------------------------

    def run(self):

        return (

            self.prepare_columns()

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


# ---------------------------------------------------------
# Convenience Function
# ---------------------------------------------------------

def derive_risk_metrics(df: pd.DataFrame):

    return RiskMetrics(df).run()