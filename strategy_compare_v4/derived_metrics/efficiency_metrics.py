"""
===============================================================
Institutional Strategy Comparison Engine V3

Module
------
efficiency_metrics.py

Purpose
-------
Derive institutional efficiency metrics.

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

    return pd.to_numeric(

        series,

        errors="coerce"

    )


def safe_divide(a, b):

    a = numeric(a)

    b = numeric(b)

    return np.where(

        (b == 0)

        |

        (pd.isna(b)),

        np.nan,

        a / b

    )


# ============================================================
# Efficiency Metrics Engine
# ============================================================

class EfficiencyMetrics:

    def __init__(self, df):

        self.df = df.copy()

    # ---------------------------------------------------------

    def prepare_columns(self):

        cols = [

            "Trades",

            "Years",

            "Net %",

            "Avg days",

            "Profit Velocity",

            "Annual Return %",

            "Reward Risk",

            "Expectancy",

            "Holding Efficiency"

        ]

        for col in cols:

            if col in self.df.columns:

                self.df[col] = numeric(

                    self.df[col]

                )

        return self

    # ---------------------------------------------------------

    def capital_productivity(self):
        """
        Return generated per unit
        of capital turnover.
        """

        self.df["Capital Productivity"] = safe_divide(

            self.df["Annual Return %"],

            self.df["Capital Turnover"]

        )

        return self

    # ---------------------------------------------------------

    def holding_productivity(self):
        """
        Return generated per
        average holding day.
        """

        self.df["Holding Productivity"] = safe_divide(

            self.df["Net %"],

            self.df["Avg days"]

        )

        return self

    # ---------------------------------------------------------

    def utilization_score(self):
        """
        Combined utilization of
        capital and holding period.
        """

        self.df["Utilization Score"] = (

            self.df["Holding Utilization"]

            * 0.60

            +

            self.df["Capital Efficiency"]

            * 0.40

        )

        return self

    # ---------------------------------------------------------

    def time_productivity(self):
        """
        Measures annual return
        generated per occupied day.
        """

        self.df["Time Productivity"] = safe_divide(

            self.df["Annual Return %"],

            self.df["Annual Holding Days"]

        )

        return self

    # ---------------------------------------------------------

    def return_density(self):
        """
        Return generated per trade.
        """

        self.df["Return Density"] = safe_divide(

            self.df["Net %"],

            self.df["Trades"]

        )

        return self

    # ---------------------------------------------------------

    def trade_productivity(self):
        """
        Productivity of executed
        trades.
        """

        self.df["Trade Productivity"] = (

            self.df["Trade Efficiency"]

            *

            self.df["Reward Risk"]

        )

        return self

    # ---------------------------------------------------------

    def institutional_efficiency(self):
        """
        Institutional efficiency
        combining return, turnover,
        and utilization.
        """

        self.df["Institutional Efficiency"] = (

            self.df["Capital Efficiency"]

            * 0.40

            +

            self.df["Trade Efficiency"]

            * 0.30

            +

            self.df["Holding Utilization"]

            * 0.30

        )

        return self

    # ---------------------------------------------------------

    def capital_recovery(self):
        """
        Measures capital recovery
        speed.
        """

        self.df["Capital Recovery"] = safe_divide(

            self.df["Capital Turnover"],

            self.df["Avg days"]

        )

        return self

    # ---------------------------------------------------------

    def holding_stability(self):
        """
        Stability of holding period.
        Higher value indicates
        lower time variability.
        """

        self.df["Holding Stability"] = (

            1

            /

            (

                1

                +

                self.df["Avg days"]

            )

        )

        return self

    # ---------------------------------------------------------

    def efficiency_quality(self):
        """
        Weighted quality of
        institutional efficiency.
        """

        self.df["Efficiency Quality"] = (

            self.df["Institutional Efficiency"]

            * 0.45

            +

            self.df["Efficiency Velocity"]

            * 0.25

            +

            self.df["Trade Productivity"]

            * 0.30

        )

        return self

    # ---------------------------------------------------------

    def efficiency_consistency(self):
        """
        Measures consistency
        between productivity
        and utilization.
        """

        self.df["Efficiency Consistency"] = safe_divide(

            self.df["Efficiency Quality"],

            self.df["Holding Utilization"] + 1e-9

        )

        return self

    # ---------------------------------------------------------

    def institutional_efficiency_score(self):
        """
        Final institutional
        efficiency score.
        """

        self.df["Institutional Efficiency Score"] = (

            self.df["Efficiency Quality"]

            * 0.40

            +

            self.df["Capital Productivity"]

            * 0.20

            +

            self.df["Trade Productivity"]

            * 0.20

            +

            self.df["Holding Stability"]

            * 0.20

        )

        return self

    # ---------------------------------------------------------

    def efficiency_rank(self):
        """
        Percentile ranking based on the
        Institutional Efficiency Score.
        """

        self.df["Efficiency Rank"] = (

            self.df["Institutional Efficiency Score"]

            .rank(

                pct=True,

                ascending=True

            )

            * 100

        )

        return self

    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize major efficiency metrics
        to a 0-100 scale.
        """

        metrics = [

            "Capital Efficiency",
            "Trade Efficiency",
            "Institutional Efficiency",
            "Efficiency Quality",
            "Institutional Efficiency Score"

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

                    (

                        self.df[metric]

                        - minimum

                    )

                    /

                    (

                        maximum

                        - minimum

                    )

                    * 100

                )

        return self

    # ---------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid values.
        """

        self.df.replace(

            [

                np.inf,

                -np.inf

            ],

            np.nan,

            inplace=True

        )

        return self

    # ---------------------------------------------------------

    def round_metrics(self):
        """
        Round all derived metrics.
        """

        derived_cols = [

            "Annual Holding Days",
            "Capital Turnover",
            "Holding Utilization",
            "Time Efficiency",
            "Capital Efficiency",
            "Return Efficiency",
            "Trade Efficiency",
            "Edge Persistence",
            "Efficiency Velocity",
            "Capital Productivity",
            "Holding Productivity",
            "Utilization Score",
            "Time Productivity",
            "Return Density",
            "Trade Productivity",
            "Institutional Efficiency",
            "Capital Recovery",
            "Holding Stability",
            "Efficiency Quality",
            "Efficiency Consistency",
            "Institutional Efficiency Score",
            "Efficiency Rank"

        ]

        for col in derived_cols:

            if col in self.df.columns:

                self.df[col] = (

                    self.df[col]

                    .round(4)

                )

        return self

    # ---------------------------------------------------------

    def run(self):

        return (

            self.prepare_columns()

                .annual_holding_days()

                .capital_turnover()

                .holding_utilization()

                .time_efficiency()

                .capital_efficiency()

                .return_efficiency()

                .trade_efficiency()

                .edge_persistence()

                .efficiency_velocity()

                .capital_productivity()

                .holding_productivity()

                .utilization_score()

                .time_productivity()

                .return_density()

                .trade_productivity()

                .institutional_efficiency()

                .capital_recovery()

                .holding_stability()

                .efficiency_quality()

                .efficiency_consistency()

                .institutional_efficiency_score()

                .efficiency_rank()

                .normalize_scores()

                .cleanup()

                .round_metrics()

                .df

        )


# ============================================================
# Convenience Function
# ============================================================

def derive_efficiency_metrics(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Derive all institutional efficiency metrics.
    """

    return EfficiencyMetrics(df).run()