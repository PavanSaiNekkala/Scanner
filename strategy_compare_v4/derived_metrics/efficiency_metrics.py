"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
efficiency_metrics.py

Purpose
-------
Derive institutional efficiency metrics from strategy
performance statistics.

Author
------
OpenAI

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

    Supports:
    - pandas Series
    - numpy arrays
    - scalar values

    Invalid values become NaN.
    """

    converted = pd.to_numeric(
        value,
        errors="coerce",
    )

    if isinstance(
        converted,
        pd.Series,
    ):
        return converted.replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

    if isinstance(
        converted,
        np.ndarray,
    ):
        return pd.Series(converted).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

    if pd.isna(converted):
        return np.nan

    return float(converted)


def safe_divide(a, b):
    """
    Safe division supporting:

    - Series / Series
    - Series / scalar
    - scalar / Series
    - scalar / scalar
    """

    a = numeric(a)
    b = numeric(b)

    # -----------------------------------------
    # Scalar / Scalar
    # -----------------------------------------

    if np.isscalar(a) and np.isscalar(b):
        if b == 0 or pd.isna(b):
            return np.nan

        return a / b

    # -----------------------------------------
    # Series / Scalar
    # -----------------------------------------

    if isinstance(
        a,
        pd.Series,
    ) and np.isscalar(b):
        if b == 0 or pd.isna(b):
            return pd.Series(
                np.nan,
                index=a.index,
            )

        return (a / b).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

    # -----------------------------------------
    # Scalar / Series
    # -----------------------------------------

    if np.isscalar(a) and isinstance(
        b,
        pd.Series,
    ):
        return (
            a
            / b.replace(
                0,
                np.nan,
            )
        ).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

    # -----------------------------------------
    # Series / Series
    # -----------------------------------------

    return a.divide(b.where((b != 0) & (~b.isna()))).replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )


# ============================================================
# Efficiency Metrics Engine
# ============================================================


class EfficiencyMetrics:
    REQUIRED_COLUMNS = {
        "Trades",
        "Years",
        "Avg days",
    }

    def __init__(
        self,
        df: pd.DataFrame,
    ):
        self.df = df.copy()

    # ---------------------------------------------------------

    def validate(self):

        missing = self.REQUIRED_COLUMNS.difference(self.df.columns)

        if missing:
            raise KeyError(f"Missing required columns: {sorted(missing)}")

        return self

    # ---------------------------------------------------------

    def prepare_columns(self):
        """
        Normalize legacy column names and convert all
        required columns to numeric.
        """

        rename_map = {
            "Avg Win %": "Avg win%",
            "Avg Loss %": "Avg loss%",
            "Maximum Drawdown %": "Max Drawdown %",
            "Total Return %": "Net %",
            "Net Profit %": "Net %",
        }

        for new_name, legacy_name in rename_map.items():
            if new_name in self.df.columns and legacy_name not in self.df.columns:
                self.df[legacy_name] = self.df[new_name]

        numeric_cols = [
            "Trades",
            "Years",
            "Net %",
            "Net Profit %",
            "Total Return %",
            "Annual Return %",
            "Avg days",
            "Profit Factor",
            "Profit Velocity",
            "Reward Risk",
            "Expectancy",
            "Holding Efficiency",
            "Capital Turnover",
            "Trade Efficiency",
            "Avg win%",
            "Avg loss%",
        ]

        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = numeric(self.df[col])

        return self

    # ---------------------------------------------------------

    def annual_holding_days(self):
        """
        Total holding days utilized
        per year.
        """

        self.df["Annual Holding Days"] = safe_divide(
            self.df["Avg days"] * self.df["Trades"],
            self.df["Years"],
        )

        return self

    # ---------------------------------------------------------

    def capital_turnover(self):
        """
        Capital rotation frequency proxy.

        Formula:

        Trades / Years

        Represents:
        Average number of completed trades
        executed annually.

        """

        self.df["Capital Turnover"] = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        return self

    # ---------------------------------------------------------

    def holding_utilization(self):
        """
        Fraction of a calendar year
        capital remains deployed.
        """

        self.df["Holding Utilization"] = safe_divide(
            self.df["Annual Holding Days"],
            365.25,
        )

        self.df["Capital Exposure Ratio"] = np.minimum(
            self.df["Holding Utilization"],
            1.0,
        )

        return self

    # ---------------------------------------------------------

    def time_efficiency(self):
        """
        Annual return generated
        per holding day.
        """

        self.df["Time Efficiency"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Avg days"],
        )

        return self

    # ---------------------------------------------------------

    def capital_efficiency(self):
        """
        Return generated per unit
        of capital exposure.

        Formula:

        Annual Return %
        ----------------
        Capital Exposure Ratio

        """

        self.df["Capital Efficiency"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Capital Exposure Ratio"],
        )

        return self

    # ---------------------------------------------------------

    def return_efficiency(self):
        """
        Measures edge generation rate.

        Formula:

        Expectancy × Annual Trade Frequency

        """

        self.df["Return Efficiency"] = (
            self.df["Expectancy"]
            *
            self.df["Capital Turnover"]
        )

        return self

    # ---------------------------------------------------------

    def trade_efficiency(self):
        """
        Combined trade quality
        using expectancy and
        reward-risk ratio.
        """

        self.df["Trade Efficiency"] = self.df["Expectancy"] * self.df["Profit Factor"]

        return self

    # ---------------------------------------------------------

    def edge_persistence(self):
        """
        Sustainable trading edge
        after considering holding
        utilization.
        """

        self.df["Edge Persistence"] = (
            self.df["Trade Efficiency"] * self.df["Holding Utilization"]
        )

        return self

    # ---------------------------------------------------------

    def efficiency_velocity(self):
        """
        Speed of edge generation.

        Formula:

        Trade Efficiency × log(1 + Capital Turnover)

        """

        self.df["Efficiency Velocity"] = (
            self.df["Trade Efficiency"]
            *
            np.log1p(
                self.df["Capital Turnover"]
            )
        )

        return self

    # ---------------------------------------------------------

    def capital_productivity(self):
        """
        Return generated per unit
        capital exposure.

        Formula:

        Annual Return %
        ----------------
        Holding Utilization

        """

        self.df["Capital Productivity"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Holding Utilization"],
        )

        return self

    # ---------------------------------------------------------

    def holding_productivity(self):
        """
        Return generated per occupied
        holding period.

        Formula:

        Annual Return %
        ----------------
        Annual Holding Days

        """

        self.df["Holding Productivity"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Annual Holding Days"],
        )

        return self
    # ---------------------------------------------------------

    def normalize_base_metrics(self):
        """
        Normalize metrics before combining.
        """

        metrics = [
            "Capital Efficiency",
            "Trade Efficiency",
            "Capital Productivity",
            "Trade Productivity",
            "Efficiency Velocity",
            "Return Density",
            "Capital Recovery",
            "Holding Productivity",
            "Institutional Efficiency",
            "Efficiency Quality",
        ]

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            minimum = self.df[metric].min()

            maximum = self.df[metric].max()

            if maximum == minimum:
                self.df[f"{metric} Norm"] = 50.0

            else:
                self.df[f"{metric} Norm"] = (
                    (self.df[metric] - minimum) / (maximum - minimum)
                ) * 100

        return self

    # ---------------------------------------------------------

    def utilization_score(self):
        """
        Combined utilization of
        capital and holding period.
        """

        self.df["Utilization Score"] = (
            self.df["Holding Utilization"] * 0.60
            + self.df["Capital Efficiency Norm"] * 0.40
        )

        return self

    # ---------------------------------------------------------

    def time_productivity(self):
        """
        Annual return generated
        per occupied holding day.
        """

        self.df["Time Productivity"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Annual Holding Days"],
        )

        return self

    # ---------------------------------------------------------

    def return_density(self):
        """
        Edge generated per trade.

        Formula:

        Expectancy × Profit Factor

        """

        self.df["Return Density"] = (
            self.df["Expectancy"]
            *
            self.df["Profit Factor"]
        )

        return self
    
    # ---------------------------------------------------------

    def trade_productivity(self):
        """
        Productivity of
        executed trades.
        """

        self.df["Trade Productivity"] = (
            self.df["Expectancy"]
            * self.df["Profit Factor"]
            * np.log1p(self.df["Trades"])
        )

        return self

    # ---------------------------------------------------------

    def institutional_efficiency(self):
        """
        Composite institutional efficiency.

        Components:

        - Capital Efficiency
        - Trade Efficiency
        - Holding Utilization

        All components normalized to 0-100.

        """

        holding_score = (
            self.df["Holding Utilization"]
            *
            100
        )


        self.df["Institutional Efficiency"] = (
            self.df["Capital Efficiency Norm"] * 0.40
            +
            self.df["Trade Efficiency Norm"] * 0.30
            +
            holding_score * 0.30
        )

        return self

    # ---------------------------------------------------------

    def capital_recovery(self):
        """
        Measures return recovery speed.

        Formula:

        Annual Return %
        ----------------
        Average Holding Days

        """

        self.df["Capital Recovery"] = safe_divide(
            self.df["Annual Return %"],
            self.df["Avg days"],
        )

        return self

    # ---------------------------------------------------------

    def holding_stability(self):
        """
        Stability of
        holding duration.
        """

        self.df["Holding Stability"] = safe_divide(
            1,
            1 + self.df["Avg days"],
        )

        return self

    # ---------------------------------------------------------

    def efficiency_quality(self):
        """
        Overall efficiency quality.

        """

        self.df["Efficiency Quality"] = (
            self.df["Institutional Efficiency"] * 0.45
            +
            self.df["Efficiency Velocity Norm"] * 0.25
            +
            self.df["Trade Productivity Norm"] * 0.30
        )

        return self

    # ---------------------------------------------------------

    def efficiency_consistency(self):
        """
        Measures sustainability of efficiency.

        Formula:

        Efficiency Quality × Holding Utilization

        Higher means efficiency is
        consistently achieved over exposure.

        """

        self.df["Efficiency Consistency"] = (
            self.df["Efficiency Quality"]
            *
            self.df["Holding Utilization"]
        )

        return self

    # ---------------------------------------------------------

    def institutional_efficiency_score(self):
        """
        Final institutional efficiency score.

        Scale:

        0 - 100

        """

        holding_score = (
            self.df["Holding Stability"]
            *
            100
        )


        self.df["Institutional Efficiency Score"] = (
            self.df["Efficiency Quality"] * 0.40
            +
            self.df["Capital Productivity Norm"] * 0.20
            +
            self.df["Trade Productivity Norm"] * 0.20
            +
            holding_score * 0.20
        )


        return self

    # ---------------------------------------------------------

    def efficiency_rank(self):
        """
        Percentile ranking.

        Higher score = better rank.

        """

        self.df["Efficiency Rank"] = (
            self.df["Institutional Efficiency Score"]
            .rank(
                pct=True,
                ascending=True,
            )
            *
            100
        )

        return self

    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize major
        efficiency metrics
        to a 0-100 scale.
        """

        metrics = [
            "Capital Efficiency",
            "Trade Efficiency",
            "Institutional Efficiency",
            "Efficiency Quality",
            "Institutional Efficiency Score",
        ]

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            minimum = self.df[metric].min()
            maximum = self.df[metric].max()

            if pd.isna(minimum) or pd.isna(maximum):
                continue

            if minimum == maximum:
                self.df[f"{metric} (Norm)"] = 50.0

            else:
                self.df[f"{metric} (Norm)"] = (
                    (self.df[metric] - minimum) / (maximum - minimum) * 100
                )

        return self

    # ---------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid values from
        all derived metrics.
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
            "Efficiency Rank",
        ]

        for col in derived_cols:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col]
                    .replace(
                        [np.inf, -np.inf],
                        np.nan,
                    )
                    .fillna(0.0)
                )

        return self

    # ---------------------------------------------------------

    def round_metrics(self):
        """
        Round all derived metrics
        to four decimal places.
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
            "Efficiency Rank",
        ]

        for col in derived_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].round(4)

        return self

    # ---------------------------------------------------------

    def run(self):

        logger.info("Calculating efficiency metrics")

        result = (
            self.prepare_columns()
            .validate()
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
            .time_productivity()
            .return_density()
            .trade_productivity()
            .normalize_base_metrics()
            .utilization_score()
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

        logger.info("Efficiency metrics completed")

        return result


# ============================================================
# Convenience Function
# ============================================================


def derive_efficiency_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Derive all institutional
    efficiency metrics.
    """

    return EfficiencyMetrics(df).run()
