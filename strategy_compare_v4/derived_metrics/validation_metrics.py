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

    REQUIRED_COLUMNS = {
        "Trades",
        "Win%",
        "Expectancy",
        "Profit Factor",
        "Reward Risk",
        "Annual Return %",
        "Avg days",
        "Years",
    }

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

        require_columns(
            self.df,
            self.REQUIRED_COLUMNS,
        )

        for column in self.REQUIRED_COLUMNS:
            self.df[column] = numeric(
                self.df[column],
            )

        logger.info(
            "Prepared %d validation columns.",
            len(self.REQUIRED_COLUMNS),
        )

        return self

    # ---------------------------------------------------------
    # Missing Value Count
    # ---------------------------------------------------------

    def missing_values(self):
        """
        Calculate missing value count per row.
        """

        self.df["Missing Values"] = self.df.isna().sum(axis=1)

        return self

    # ---------------------------------------------------------
    # Missing Value Percentage
    # ---------------------------------------------------------

    def missing_percent(self):
        """
        Calculate missing percentage.

        Uses original validation columns
        instead of dynamically changing
        derived columns.
        """

        total_columns = len(
            self.REQUIRED_COLUMNS,
        )

        if total_columns == 0:
            self.df["Missing %"] = 0

        else:
            self.df["Missing %"] = self.df["Missing Values"] / total_columns * 100

        return self

    # ---------------------------------------------------------
    # Duplicate Rows
    # ---------------------------------------------------------

    def duplicate_rows(self):
        """
        Detect duplicate strategy records.

        Duplicate detection is performed
        only on original validation fields.
        """

        self.df["Duplicate Row"] = self.df.duplicated(
            subset=list(self.REQUIRED_COLUMNS),
        ).astype(int)

        return self

    # ---------------------------------------------------------
    # Zero Trade Flag
    # ---------------------------------------------------------

    def zero_trade_flag(self):
        """
        Detect strategies without trades.
        """

        self.df["Zero Trades"] = (self.df["Trades"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Win Rate
    # ---------------------------------------------------------

    def invalid_win_rate(self):
        """
        Detect invalid win percentage.
        """

        self.df["Invalid Win%"] = (
            (self.df["Win%"] < 0) | (self.df["Win%"] > 100)
        ).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Reward Risk
    # ---------------------------------------------------------

    def invalid_reward_risk(self):
        """
        Detect invalid reward-risk ratio.
        """

        self.df["Invalid Reward Risk"] = (self.df["Reward Risk"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Profit Factor
    # ---------------------------------------------------------

    def invalid_profit_factor(self):
        """
        Detect invalid profit factor.
        """

        self.df["Invalid Profit Factor"] = (self.df["Profit Factor"] < 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Holding Period
    # ---------------------------------------------------------

    def invalid_holding_period(self):
        """
        Detect invalid holding periods.
        """

        self.df["Invalid Holding"] = (self.df["Avg days"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Invalid Years
    # ---------------------------------------------------------

    def invalid_years(self):
        """
        Detect invalid backtest duration.
        """

        self.df["Invalid Years"] = (self.df["Years"] <= 0).astype(int)

        return self

    # ---------------------------------------------------------
    # Z Score Outliers
    # ---------------------------------------------------------

    def zscore_outliers(self):
        """
        Detect statistical outliers.

        Uses important performance metrics.
        """

        metrics = [
            "Annual Return %",
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
        ]

        zscore_flags = []

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            series = numeric(self.df[metric])

            mean = series.mean()

            std = series.std()

            if pd.isna(std) or std == 0:
                continue

            z_score = (series - mean) / std

            zscore_flags.append(z_score.abs() > 3)

        if zscore_flags:
            self.df["ZScore Outliers"] = pd.concat(
                zscore_flags,
                axis=1,
            ).sum(axis=1)

        else:
            self.df["ZScore Outliers"] = 0

        return self

    # ---------------------------------------------------------
    # IQR Outliers
    # ---------------------------------------------------------

    def iqr_outliers(self):
        """
        Detect extreme values using
        interquartile range.
        """

        metrics = [
            "Annual Return %",
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
        ]

        flags = []

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            series = numeric(self.df[metric])

            q1 = series.quantile(0.25)

            q3 = series.quantile(0.75)

            iqr = q3 - q1

            if pd.isna(iqr) or iqr == 0:
                continue

            lower = q1 - (1.5 * iqr)

            upper = q3 + (1.5 * iqr)

            flags.append((series < lower) | (series > upper))

        if flags:
            self.df["IQR Outliers"] = pd.concat(
                flags,
                axis=1,
            ).sum(axis=1)

        else:
            self.df["IQR Outliers"] = 0

        return self

    # ---------------------------------------------------------
    # Extreme Return Detection
    # ---------------------------------------------------------

    def extreme_return(self):
        """
        Detect unrealistic returns.

        Both positive and negative
        extremes are considered.
        """

        self.df["Extreme Return"] = (
            self.df["Annual Return %"].abs() > EXTREME_RETURN_THRESHOLD
        ).astype(int)

        return self

    # ---------------------------------------------------------
    # Extreme Expectancy Detection
    # ---------------------------------------------------------

    def extreme_expectancy(self):
        """
        Detect unrealistic expectancy values.
        """

        self.df["Extreme Expectancy"] = (
            self.df["Expectancy"].abs() > EXTREME_EXPECTANCY_THRESHOLD
        ).astype(int)

        return self

    # ---------------------------------------------------------
    # Logical Error Detection
    # ---------------------------------------------------------

    def logical_errors(self):
        """
        Detect impossible combinations.

        Examples:

        - Winning percentage invalid
        - No trades but returns exist
        - Invalid risk metrics
        """

        errors = (
            self.df["Zero Trades"]
            + self.df["Invalid Win%"]
            + self.df["Invalid Reward Risk"]
            + self.df["Invalid Profit Factor"]
            + self.df["Invalid Holding"]
            + self.df["Invalid Years"]
        )

        self.df["Logical Errors"] = errors

        return self

    # ---------------------------------------------------------
    # Completeness Score
    # ---------------------------------------------------------

    def completeness_score(self):
        """
        Measures availability of
        required data.
        """

        self.df["Completeness Score"] = 100 - (self.df["Missing %"])

        self.df["Completeness Score"] = self.df["Completeness Score"].clip(
            0,
            100,
        )

        return self

    # ---------------------------------------------------------
    # Statistical Reliability
    # ---------------------------------------------------------

    def statistical_reliability(self):
        """
        Institutional reliability score.

        Trade quantity + historical duration.

        Formula:

        Trades     70%
        Years      30%

        """

        trade_quality = np.minimum(
            safe_divide(
                self.df["Trades"],
                100,
            ),
            1,
        )

        time_quality = np.minimum(
            safe_divide(
                self.df["Years"],
                3,
            ),
            1,
        )

        self.df["Statistical Reliability"] = trade_quality * 70 + time_quality * 30

        return self

    # ---------------------------------------------------------
    # Validation Consistency
    # ---------------------------------------------------------

    def validation_consistency(self):
        """
        Final validation quality score.

        Logical errors have higher penalty.
        """

        penalty = (
            self.df["Logical Errors"] * 15
            + self.df["ZScore Outliers"] * 5
            + self.df["IQR Outliers"] * 5
            + self.df["Extreme Return"] * 10
            + self.df["Extreme Expectancy"] * 10
        )

        self.df["Validation Consistency"] = (100 - penalty).clip(
            0,
            100,
        )

        return self

    # ---------------------------------------------------------
    # Final Validation Score
    # ---------------------------------------------------------

    def validation_score(self):
        """
        Final institutional validation score.

        Weighting:

        Completeness          30%
        Statistical Reliability 40%
        Validation Consistency  30%

        """

        self.df["Validation Score"] = (
            self.df["Completeness Score"] * 0.30
            + self.df["Statistical Reliability"] * 0.40
            + self.df["Validation Consistency"] * 0.30
        )

        return self

    # ---------------------------------------------------------
    # Validation Status
    # ---------------------------------------------------------

    def validation_status(self):
        """
        Assign validation quality status.
        """

        score = self.df["Validation Score"]

        self.df[VALIDATION_STATUS] = np.select(
            [
                score >= 90,
                score >= 75,
                score >= 60,
                score >= 40,
            ],
            [
                "PASS",
                "PASS_WITH_WARNING",
                "REVIEW",
                "FAIL",
            ],
            default="FAIL",
        )

        return self

    # ---------------------------------------------------------
    # Normalize Metrics
    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize validation metrics.
        """

        metrics = [
            "Completeness Score",
            "Statistical Reliability",
            "Validation Consistency",
            "Validation Score",
        ]

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            self.df[f"{metric} Norm"] = normalize(self.df[metric])

        return self

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def cleanup(self):
        """
        Clean invalid numeric values.
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
    # Round Metrics
    # ---------------------------------------------------------

    def round_metrics(self):
        """
        Round validation metrics.
        """

        numeric_columns = self.df.select_dtypes(
            include="number",
        ).columns

        self.df[numeric_columns] = self.df[numeric_columns].round(2)

        return self

    # ---------------------------------------------------------
    # Run Validation Pipeline
    # ---------------------------------------------------------

    def run(self):
        """
        Execute complete validation pipeline.
        """

        logger.info("Running Validation Metrics Engine...")

        result = (
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
            .zscore_outliers()
            .iqr_outliers()
            .extreme_return()
            .extreme_expectancy()
            .logical_errors()
            .completeness_score()
            .statistical_reliability()
            .validation_consistency()
            .validation_score()
            .validation_status()
            .normalize_scores()
            .cleanup()
            .round_metrics()
            .df
        )

        logger.info("Validation Metrics completed.")

        return result


# ============================================================
# Public API
# ============================================================


def derive_validation_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Public validation interface.
    """

    logger.info("Deriving validation metrics...")

    return ValidationMetrics(df).run()


__all__ = [
    "ValidationMetrics",
    "derive_validation_metrics",
]
