"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
opportunity_metrics.py

Purpose
-------
Derive institutional opportunity and execution metrics
from strategy backtest results.

===============================================================
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from strategy_compare_v4.utils.helpers import (
    normalize,
    require_columns,
)

logger = logging.getLogger(__name__)


# ============================================================
# Utility Functions
# ============================================================


def numeric(series):
    """
    Safely convert values
    to numeric.
    """

    return pd.to_numeric(
        series,
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
    Safe vectorized division.
    """

    a = numeric(a)

    b = numeric(b)

    return a.divide(b.where((b != 0) & (~b.isna())))


# ============================================================
# Opportunity Metrics
# ============================================================


class OpportunityMetrics:
    """
    Institutional Opportunity Metrics Engine.
    """

    REQUIRED_COLUMNS = {
        "Trades",
        "Years",
        "Avg days",
        "Win%",
    }

    def __init__(
        self,
        df: pd.DataFrame,
    ):
        self.df = df.copy()

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self):
        """
        Validate mandatory columns.
        """

        require_columns(
            self.df,
            self.REQUIRED_COLUMNS,
        )

        return self

    # ---------------------------------------------------------
    # Prepare Columns
    # ---------------------------------------------------------

    def prepare_columns(self):
        """
        Standardize column names
        and convert numerics.
        """

        aliases = {
            "Average Days": "Avg days",
            "Trades/Year": "Trades / Year",
            "Annual Return": "Annual Return %",
            "Winning %": "Win%",
        }

        for old, new in aliases.items():
            if old in self.df.columns and new not in self.df.columns:
                self.df.rename(
                    columns={
                        old: new,
                    },
                    inplace=True,
                )

        numeric_columns = [
            "Signals today",
            "Trades",
            "Years",
            "Avg days",
            "Win%",
            "Annual Return %",
        ]

        for column in numeric_columns:
            if column in self.df.columns:
                self.df[column] = numeric(self.df[column])

        return self

    # ---------------------------------------------------------

    def trades_per_year(self):
        """
        Average trades executed
        per calendar year.
        """

        self.df["Trades / Year"] = safe_divide(
            self.df["Trades"],
            self.df["Years"],
        )

        return self

    # ---------------------------------------------------------

    def signals_per_year(self):
        """
        Estimate annual opportunity count.

        Uses executed trades as
        opportunity proxy when
        historical signals are unavailable.

        """

        self.df["Signals / Year"] = (
            self.df["Trades / Year"]
        )

        return self

    # ---------------------------------------------------------

    def signal_conversion(self):
        """
        Execution conversion proxy.

        Historical signal count is unavailable.

        Uses executed trade consistency.

        """

        self.df["Signal Conversion"] = 1.0

        return self

    # ---------------------------------------------------------

    def opportunity_utilization(self):
        """
        Opportunity utilization.

        Formula:

        Trade Frequency /
        Maximum Observed Trade Frequency

        """

        max_frequency = (
            self.df["Trades / Year"]
            .max()
        )


        self.df["Opportunity Utilization"] = safe_divide(
            self.df["Trades / Year"],
            max_frequency,
        ) * 100


        return self

    # ---------------------------------------------------------

    def trade_density(self):
        """
        Trades generated per
        average holding day.
        """

        self.df["Trade Density"] = safe_divide(
            self.df["Trades"],
            self.df["Avg days"],
        )

        return self

    # ---------------------------------------------------------

    def holding_occupancy(self):
        """
        Fraction of annual time
        occupied by positions.

        """

        occupancy = safe_divide(
            self.df["Trades"] * self.df["Avg days"],
            self.df["Years"] * 365.25,
        )


        self.df["Holding Occupancy"] = occupancy.clip(
            lower=0,
            upper=1,
        )


        self.df["Capital Utilization"] = (
            self.df["Holding Occupancy"]
        )


        return self

    # ---------------------------------------------------------

    def idle_time_ratio(self):
        """
        Fraction of annual time
        spent without positions.
        """

        self.df["Idle Time Ratio"] = 1 - self.df["Holding Occupancy"]

        return self

    # ---------------------------------------------------------

    def opportunity_coverage(self):
        """
        Percentage of annual market
        participation.
        """

        self.df["Capital Deployment %"] = self.df["Capital Utilization"] * 100

        return self

    # ---------------------------------------------------------

    def capacity_score(self):
        """
        Institutional capacity score.

        Components:

        Trade Density        50%
        Trade Availability   30%
        Capital Utilization  20%

        """

        trade_density = normalize(
            self.df["Trade Density"]
        )

        availability = normalize(
            self.df["Trade Availability"]
        )

        utilization = normalize(
            self.df["Capital Utilization"]
        )


        self.df["Capacity Score"] = (
            trade_density * 0.50
            +
            availability * 0.30
            +
            utilization * 0.20
        )

        return self
    
    # ---------------------------------------------------------

    def opportunity_velocity(self):
        """
        Opportunities generated
        per holding day.
        """

        self.df["Opportunity Velocity"] = safe_divide(
            self.df["Trades / Year"],
            self.df["Avg days"],
        )

        return self

    # ---------------------------------------------------------

    def trade_availability(self):
        """
        Executable trade ratio.
        """

        if "Signals / Year" in self.df.columns:
            availability = safe_divide(
                self.df["Trades / Year"],
                self.df["Signals / Year"],
            )

            self.df["Trade Availability"] = availability.clip(
                lower=0,
                upper=1,
            )

        else:
            self.df["Trade Availability"] = 1.0

        return self

    # ---------------------------------------------------------

    def signal_saturation(self):
        """
        Signals generated
        per executed trade.
        """

        if "Signals today" in self.df.columns:
            self.df["Signal Saturation"] = safe_divide(
                self.df["Signals / Year"],
                self.df["Trades / Year"],
            )

        else:
            self.df["Signal Saturation"] = 1.0

        return self

    # ---------------------------------------------------------

    def execution_efficiency(self):
        """
        Measures profitable execution quality.

        Formula:

        Win Rate × Reward Risk

        """

        self.df["Execution Efficiency"] = (
            self.df["Win%"]
            /
            100
        ) * self.df["Reward Risk"]


        return self

    # ---------------------------------------------------------

    def market_coverage(self):
        """
        Percentage of annual
        market participation.
        """

        self.df["Market Coverage"] = self.df["Holding Occupancy"] * 100

        return self

    # ---------------------------------------------------------

    def opportunity_quality(self):
        """
        Overall opportunity quality.
        """

        execution = normalize(self.df["Execution Efficiency"])

        density = normalize(self.df["Trade Density"])

        self.df["Opportunity Quality"] = (
            execution * 0.50
            + density * 0.30
            + self.df["Trades / Year"].pipe(normalize) * 0.20
        )

        return self

    # ---------------------------------------------------------

    def capacity_utilization(self):
        """
        Effective utilization of
        available trading capacity.
        """

        self.df["Capacity Utilization"] = (
            self.df["Capacity Score"] * self.df["Holding Occupancy"]
        )

        return self

    # ---------------------------------------------------------

    def annual_signal_efficiency(self):
        """
        Annualized signal efficiency.
        """

        self.df["Annual Signal Efficiency"] = (
            self.df["Execution Efficiency"] * self.df["Trades / Year"]
        )

        return self

    # ---------------------------------------------------------

    def trade_opportunity_ratio(self):
        """
        Executed trade opportunity ratio.

        Historical signal generation unavailable.

        """

        self.df["Trade Opportunity Ratio"] = 1.0

        return self

    # ---------------------------------------------------------

    def opportunity_persistence(self):
        """
        Persistence of opportunities.

        Formula:

        Trade Density /
        (1 + Idle Time Ratio)

        """

        self.df["Opportunity Persistence"] = safe_divide(
            self.df["Trade Density"],
            (
                1 +
                self.df["Idle Time Ratio"]
            ),
        )


        return self

    # ---------------------------------------------------------

    def execution_consistency(self):
        """
        Execution quality adjusted
        for average holding period.
        """

        self.df["Execution Consistency"] = safe_divide(
            self.df["Execution Efficiency"],
            self.df["Avg days"],
        )

        return self

    # ---------------------------------------------------------

    def institutional_opportunity_score(self):
        """
        Institutional opportunity score.

        """

        quality = normalize(
            self.df["Opportunity Quality"]
        )

        capacity = normalize(
            self.df["Capacity Score"]
        )

        execution = normalize(
            self.df["Execution Efficiency"]
        )

        density = normalize(
            self.df["Trade Density"]
        )


        self.df["Institutional Opportunity Score"] = (
            quality * 0.35
            +
            capacity * 0.25
            +
            execution * 0.20
            +
            density * 0.20
        )


        return self

    # ---------------------------------------------------------

    def opportunity_rank(self):
        """
        Institutional percentile
        ranking.
        """

        self.df["Opportunity Rank"] = (
            self.df["Institutional Opportunity Score"].rank(
                pct=True,
                ascending=True,
                method="average",
            )
            * 100
        )

        return self

    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Create normalized versions
        of major opportunity metrics.
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

            self.df[f"{metric} (Norm)"] = normalize(self.df[metric])

        return self

    # ---------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid values
        from numeric columns.
        """

        numeric_columns = self.df.select_dtypes(
            include="number",
        ).columns

        self.df[numeric_columns] = (
            self.df[numeric_columns]
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

    # ---------------------------------------------------------

    def round_metrics(self):
        """
        Round all numeric metrics.
        """

        numeric_columns = self.df.select_dtypes(
            include="number",
        ).columns

        self.df[numeric_columns] = self.df[numeric_columns].round(4)

        return self

    # ---------------------------------------------------------

    def run(self):
        """
        Execute complete
        opportunity metrics engine.
        """

        logger.info("Running Opportunity Metrics...")

        result = (
            self.prepare_columns()
            .validate()
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

        logger.info("Opportunity Metrics completed.")

        return result


# ============================================================
# Convenience Function
# ============================================================


def derive_opportunity_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Derive institutional
    opportunity metrics.
    """

    logger.info("Deriving Opportunity Metrics...")

    return OpportunityMetrics(df).run()
