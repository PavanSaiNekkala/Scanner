"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
validation_metrics.py

Purpose
-------
Institutional-grade validation, anomaly detection,
and data quality scoring.

===============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategy_compare_v4.config.constants import (
    VALIDATION_STATUS,
)
from strategy_compare_v4.config.thresholds import (
    EXTREME_EXPECTANCY_THRESHOLD,
    EXTREME_RETURN_THRESHOLD,
)
from strategy_compare_v4.utils.helpers import (
    require_columns,
)
from strategy_compare_v4.utils.logger import (
    get_logger,
)
from strategy_compare_v4.utils.math_utils import (
    normalize,
    numeric,
    safe_divide,
)

logger = get_logger(__name__)


# ============================================================
# Validation Engine
# ============================================================


class ValidationMetrics:
    """
    Institutional Validation Engine.

    Responsible for validating strategy data,
    detecting anomalies and generating
    institutional-quality validation metrics.
    """

    def __init__(
        self,
        df: pd.DataFrame,
    ):
        self.df = df.copy()

    # ---------------------------------------------------------
    # Prepare Columns
    # ---------------------------------------------------------

    def prepare_columns(self):
        """
        Convert validation columns to numeric.
        """

        numeric_columns = [
            "Trades",
            "Win%",
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Annual Return %",
            "Avg days",
            "Years",
        ]

        require_columns(
            self.df,
            numeric_columns,
        )

        for column in numeric_columns:
            self.df[column] = numeric(self.df[column])

        logger.info(
            "Prepared %d validation columns.",
            len(numeric_columns),
        )

        return self

    # ---------------------------------------------------------
    # Missing Values
    # ---------------------------------------------------------

    def missing_values(self):
        """
        Count missing values per row.
        """

        self.df["Missing Values"] = self.df.isna().sum(axis=1)

        return self

    # ---------------------------------------------------------
    # Missing Percentage
    # ---------------------------------------------------------

    def missing_percent(self):
        """
        Calculate missing percentage.
        """

        total_columns = max(
            len(self.df.columns),
            1,
        )

        self.df["Missing %"] = self.df["Missing Values"] / total_columns * 100

        return self

    # ---------------------------------------------------------
    # Duplicate Rows
    # ---------------------------------------------------------

    def duplicate_rows(self):
        """
        Detect duplicate records.
        """

        self.df["Duplicate Row"] = self.df.duplicated().astype(int)

        return self

    # ---------------------------------------------------------
    # Zero Trade Flag
    # ---------------------------------------------------------

    def zero_trade_flag(self):
        self.df["Zero Trades"] = (self.df["Trades"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Win Rate
    # ---------------------------------------------------------

    def invalid_win_rate(self):
        self.df["Invalid Win%"] = (
            (self.df["Win%"] < 0) | (self.df["Win%"] > 100)
        ).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Reward Risk
    # ---------------------------------------------------------

    def invalid_reward_risk(self):
        self.df["Invalid Reward Risk"] = (self.df["Reward Risk"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Profit Factor
    # ---------------------------------------------------------

    def invalid_profit_factor(self):
        self.df["Invalid Profit Factor"] = (self.df["Profit Factor"] < 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Holding Period
    # ---------------------------------------------------------

    def invalid_holding_period(self):
        self.df["Invalid Holding"] = (self.df["Avg days"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Years
    # ---------------------------------------------------------

    def invalid_years(self):
        self.df["Invalid Years"] = (self.df["Years"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Z-Score Outlier Detection
    # ---------------------------------------------------------

    def zscore_outlier_detection(self):
        """
        Detect statistical outliers
        using Z-score analysis.
        """

        metrics = [
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Annual Return %",
        ]

        outliers = np.zeros(
            len(self.df),
            dtype=int,
        )

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            std = self.df[metric].std()

            if pd.isna(std) or std == 0:
                continue

            z_score = (self.df[metric] - self.df[metric].mean()) / std

            outliers += (np.abs(z_score) > 3).astype(int)

        self.df["ZScore Outliers"] = outliers

        return self

    # ---------------------------------------------------------
    # IQR Outlier Detection
    # ---------------------------------------------------------

    def iqr_outlier_detection(self):
        """
        Detect statistical outliers
        using the IQR method.
        """

        metrics = [
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Annual Return %",
        ]

        outliers = np.zeros(
            len(self.df),
            dtype=int,
        )

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            q1 = self.df[metric].quantile(0.25)

            q3 = self.df[metric].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr

            upper = q3 + 1.5 * iqr

            outliers += ((self.df[metric] < lower) | (self.df[metric] > upper)).astype(
                int
            )

        self.df["IQR Outliers"] = outliers

        return self

    # ---------------------------------------------------------
    # Completeness Score
    # ---------------------------------------------------------

    def completeness_score(self):
        """
        Calculate data completeness.
        """

        self.df["Completeness Score"] = (100 - self.df["Missing %"]).clip(
            lower=0,
            upper=100,
        )

        return self

    # ---------------------------------------------------------
    # Logical Integrity
    # ---------------------------------------------------------

    def logical_integrity(self):
        """
        Perform logical consistency checks.
        """

        errors = np.zeros(
            len(self.df),
            dtype=int,
        )

        if "Win%" in self.df.columns:
            errors += ((self.df["Win%"] < 0) | (self.df["Win%"] > 100)).astype(int)

        if "Profit Factor" in self.df.columns:
            errors += (self.df["Profit Factor"] <= 0).astype(int)

        if "Reward Risk" in self.df.columns:
            errors += (self.df["Reward Risk"] <= 0).astype(int)

        self.df["Logical Errors"] = errors

        return self

    # ---------------------------------------------------------
    # Extreme Return Flag
    # ---------------------------------------------------------

    def extreme_return_flag(self):
        """
        Flag unrealistic annual returns.
        """

        self.df["Extreme Return"] = (
            self.df["Annual Return %"] > EXTREME_RETURN_THRESHOLD
        )

        return self

    # ---------------------------------------------------------
    # Extreme Expectancy Flag
    # ---------------------------------------------------------

    def extreme_expectancy_flag(self):
        """
        Flag unrealistic expectancy values.
        """

        self.df["Extreme Expectancy"] = (
            self.df["Expectancy"] > EXTREME_EXPECTANCY_THRESHOLD
        )

        return self

    # ---------------------------------------------------------
    # Statistical Reliability
    # ---------------------------------------------------------

    def statistical_reliability(self):
        """
        Estimate statistical reliability
        based on trade sample size.
        """

        self.df["Statistical Reliability"] = (
            np.minimum(
                safe_divide(
                    self.df["Trades"],
                    100,
                ),
                1,
            )
            * 100
        )

        return self

    # ---------------------------------------------------------
    # Validation Consistency
    # ---------------------------------------------------------

    def consistency_score(self):
        """
        Compute validation consistency score.
        """

        penalties = (
            self.df["Logical Errors"]
            + self.df["ZScore Outliers"]
            + self.df["IQR Outliers"]
        )

        self.df["Validation Consistency"] = (100 - penalties * 10).clip(
            lower=0,
            upper=100,
        )

        return self

    # ---------------------------------------------------------
    # Data Confidence
    # ---------------------------------------------------------

    def confidence_score(self):
        """
        Calculate confidence in
        overall dataset quality.
        """

        self.df["Data Confidence"] = (
            self.df["Completeness Score"] * 0.40
            + self.df["Validation Consistency"] * 0.30
            + self.df["Statistical Reliability"] * 0.30
        )

        return self

    # ---------------------------------------------------------
    # Institutional Validation Score
    # ---------------------------------------------------------

    def institutional_validation_score(self):
        """
        Calculate overall institutional
        validation score.
        """

        self.df["Institutional Validation Score"] = (
            self.df["Data Confidence"] * 0.60
            + self.df["Completeness Score"] * 0.20
            + self.df["Validation Consistency"] * 0.20
        )

        return self

    # ---------------------------------------------------------
    # Validation Grade
    # ---------------------------------------------------------

    def validation_grade(self):
        """
        Assign institutional validation grade.
        """

        score = self.df["Institutional Validation Score"]

        self.df["Validation Grade"] = np.select(
            [
                score >= 95,
                score >= 90,
                score >= 80,
                score >= 70,
                score >= 60,
            ],
            [
                "Excellent",
                "Very Good",
                "Good",
                "Fair",
                "Poor",
            ],
            default="Critical",
        )

        return self

    # ---------------------------------------------------------
    # Validation Status
    # ---------------------------------------------------------

    def validation_status(self):
        """
        Determine overall validation status.
        """

        critical = (
            self.df["Zero Trades"].astype(bool)
            | self.df["Invalid Win%"].astype(bool)
            | self.df["Invalid Reward Risk"].astype(bool)
            | self.df["Invalid Profit Factor"].astype(bool)
            | self.df["Invalid Holding"].astype(bool)
            | self.df["Invalid Years"].astype(bool)
        )

        warnings = (
            (self.df["Missing %"].fillna(0) > 5)
            | (self.df["Logical Errors"].fillna(0) > 0)
            | (self.df["ZScore Outliers"].fillna(0) > 0)
            | (self.df["IQR Outliers"].fillna(0) > 0)
        )

        self.df[VALIDATION_STATUS] = np.select(
            [
                critical,
                warnings,
            ],
            [
                "FAILED",
                "WARNING",
            ],
            default="PASSED",
        )

        return self

    # ---------------------------------------------------------
    # Validation Rank
    # ---------------------------------------------------------

    def validation_rank(self):
        """
        Rank datasets by validation quality.
        """

        self.df["Validation Rank"] = (
            self.df["Institutional Validation Score"]
            .rank(
                ascending=False,
                method="dense",
            )
            .astype(int)
        )

        return self

    # ---------------------------------------------------------
    # Normalize Scores
    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize validation metrics.
        """

        metrics = [
            "Completeness Score",
            "Validation Consistency",
            "Statistical Reliability",
            "Data Confidence",
            "Institutional Validation Score",
        ]

        for metric in metrics:
            if metric in self.df.columns:
                self.df[f"{metric} (Norm)"] = normalize(self.df[metric])

        return self

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def cleanup(self):
        """
        Replace invalid numeric values.
        """

        self.df.replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
            inplace=True,
        )

        return self

    # ---------------------------------------------------------
    # Round Metrics
    # ---------------------------------------------------------

    def round_metrics(self):
        """
        Round all numeric validation metrics.
        """

        from strategy_compare_v4.utils.math_utils import (
            round_dataframe,
        )

        self.df = round_dataframe(
            self.df,
            decimals=2,
        )

        return self

    # ---------------------------------------------------------
    # Execute Engine
    # ---------------------------------------------------------

    def run(self):
        """
        Execute complete institutional
        validation pipeline.
        """

        logger.info("Running Institutional Validation Engine...")

        return (
            self.prepare_columns()
            .missing_values()
            .missing_percent()
            .duplicate_rows()
            .zero_trade_flag()
            .invalid_win_rate()
            .invalid_reward_risk()
            .invalid_profit_factor()
            .invalid_holding_period()
            .invalid_years()
            .zscore_outlier_detection()
            .iqr_outlier_detection()
            .completeness_score()
            .logical_integrity()
            .extreme_return_flag()
            .extreme_expectancy_flag()
            .statistical_reliability()
            .consistency_score()
            .confidence_score()
            .institutional_validation_score()
            .validation_grade()
            .validation_status()
            .validation_rank()
            .normalize_scores()
            .cleanup()
            .round_metrics()
            .df
        )


# ============================================================
# Convenience Function
# ============================================================


def derive_validation_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Derive institutional validation metrics.
    """

    logger.info("Deriving Institutional Validation Metrics...")

    return ValidationMetrics(df).run()
