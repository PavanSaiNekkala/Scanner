"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
exit_metrics.py

Purpose
-------
Derive institutional exit behaviour metrics
from strategy backtest results.

Metrics Covered
---------------
- Target Exit Behaviour
- Trailing Exit Behaviour
- Stop Dependency
- Time Dependency
- Exit Diversity
- Exit Concentration
- Exit Entropy
- Exit Quality
- Institutional Exit Score

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


# ===============================================================
# Utility Functions
# ===============================================================


def numeric(value):
    """
    Safely convert values to numeric.

    Supports:
    - Series
    - ndarray
    - scalar

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
    Safe division.

    Handles:
    - Series / Series
    - Series / scalar
    - scalar / Series
    - scalar / scalar
    """

    a = numeric(a)

    b = numeric(b)

    # Scalar / Scalar
    if np.isscalar(a) and np.isscalar(b):
        if b == 0 or pd.isna(b):
            return np.nan

        return a / b

    # Series / Series
    if isinstance(a, pd.Series) and isinstance(b, pd.Series):
        return a.divide(b.where((b != 0) & (~b.isna()))).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

    # Series / Scalar

    if isinstance(
        a,
        pd.Series,
    ):
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

    # Scalar / Series

    if isinstance(
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

    return np.nan


# ===============================================================
# Exit Metrics Engine
# ===============================================================


class ExitMetrics:
    """
    Institutional Exit Metrics Engine.
    """

    REQUIRED_COLUMNS = {
        "Trades",
        "Target #",
        "Trail #",
        "Stop #",
        "Time #",
        "Avg days",
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
        Standardize columns
        and convert numeric fields.
        """

        aliases = {
            "Target Count": "Target #",
            "Trail Count": "Trail #",
            "Stop Count": "Stop #",
            "Time Count": "Time #",
            "Average Days": "Avg days",
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
            "Trades",
            "Target #",
            "Trail #",
            "Stop #",
            "Time #",
            "Win%",
            "Avg days",
        ]

        for column in numeric_columns:
            if column in self.df.columns:
                self.df[column] = numeric(self.df[column])

        return self

    # ---------------------------------------------------------
    # Target Exit %
    # ---------------------------------------------------------

    def target_exit_percentage(self):
        """
        Percentage of trades exited
        through target booking.
        """

        self.df["Target Exit %"] = (
            safe_divide(
                self.df["Target #"],
                self.df["Trades"],
            )
            * 100
        )

        return self

    # ---------------------------------------------------------
    # Trailing Exit %
    # ---------------------------------------------------------

    def trailing_exit_percentage(self):
        """
        Percentage of trades exited
        through trailing stop.
        """

        self.df["Trailing Exit %"] = (
            safe_divide(
                self.df["Trail #"],
                self.df["Trades"],
            )
            * 100
        )

        return self

    # ---------------------------------------------------------
    # Stop Dependency
    # ---------------------------------------------------------

    def stop_dependency(self):
        """
        Measures dependence on stop losses.

        Higher value means higher risk.
        """

        self.df["Stop Dependency"] = (
            safe_divide(
                self.df["Stop #"],
                self.df["Trades"],
            )
            * 100
        )

        return self

    # ---------------------------------------------------------
    # Time Dependency
    # ---------------------------------------------------------

    def time_dependency(self):
        """
        Measures percentage of exits
        caused by time expiration.
        """

        self.df["Time Dependency"] = (
            safe_divide(
                self.df["Time #"],
                self.df["Trades"],
            )
            * 100
        )

        return self

    # ---------------------------------------------------------
    # Winning Exit %
    # ---------------------------------------------------------

    def winning_exit_percentage(self):
        """
        Measures profitable exit behaviour.
        """

        self.df["Winning Exit %"] = (
            self.df["Target Exit %"]
            +
            self.df["Trailing Exit %"]
        ).clip(
            0,
            100,
        )

        self.df["Winning Exit"] = (
            self.df["Winning Exit %"]
        )

        return self

    # ---------------------------------------------------------
    # Losing Exit %
    # ---------------------------------------------------------

    def losing_exit_percentage(self):
        """
        Losing exit behaviour.
        """

        self.df["Losing Exit %"] = (
            self.df["Stop Dependency"]
            +
            self.df["Time Dependency"]
        ).clip(
            0,
            100,
        )

        self.df["Losing Exit"] = (
            self.df["Losing Exit %"]
        )
        
        return self
    
    # ---------------------------------------------------------
    # Exit Diversity
    # ---------------------------------------------------------

    def exit_diversity(self):
        """
        Shannon entropy based exit diversity.

        Formula:

        -Σ(p × log2(p))

        Higher:
            balanced exits

        Lower:
            concentrated exits

        """

        components = [
            "Target #",
            "Trail #",
            "Stop #",
            "Time #",
        ]


        total = self.df[components].sum(axis=1)

        entropy = 0


        for column in components:

            probability = safe_divide(
                self.df[column],
                total,
            )


            probability = probability.replace(
                0,
                np.nan,
            )


            entropy += (
                probability
                *
                np.log2(probability)
            )


        self.df["Exit Entropy"] = (
            -entropy.fillna(0)
        )

        return self
    
    # ---------------------------------------------------------
    # Exit Distribution Score
    # ---------------------------------------------------------

    def exit_distribution_score(self):
        """
        Normalize exit entropy.

        Higher means more stable
        exit distribution.
        """

        max_entropy = np.log2(4)

        self.df["Exit Diversity Score"] = safe_divide(
            self.df["Exit Entropy"],
            max_entropy,
        )

        return self

    # ---------------------------------------------------------
    # Exit Concentration
    # ---------------------------------------------------------

    def exit_concentration(self):
        """
        Measures dominance of one exit type.
        """

        components = [
            "Target #",
            "Trail #",
            "Stop #",
            "Time #",
        ]

        total = self.df[components].sum(axis=1)

        shares = []

        for column in components:
            shares.append(
                safe_divide(
                    self.df[column],
                    total,
                )
            )

        concentration = pd.concat(
            shares,
            axis=1,
        ).max(axis=1)

        self.df["Exit Concentration"] = concentration

        return self

    # ---------------------------------------------------------
    # Exit Efficiency
    # ---------------------------------------------------------

    def exit_efficiency(self):
        """
        Measures exit quality.

        Higher is better.
        """

        win_quality = (
            self.df["Winning Exit %"]
        )


        diversity = (
            self.df["Exit Diversity Score"]
            *
            100
        )


        stop_quality = (
            100
            -
            self.df["Stop Dependency"]
        )


        self.df["Exit Efficiency"] = (
            win_quality * 0.50
            +
            diversity * 0.30
            +
            stop_quality * 0.20
        ).clip(
            0,
            100,
        )


        return self

    # ---------------------------------------------------------
    # Exit Robustness
    # ---------------------------------------------------------

    def exit_robustness(self):

        self.df["Exit Robustness"] = (

            normalize(
                self.df["Exit Diversity Score"]
            )
            *
            0.40

            +

            safe_divide(
                self.df["Winning Exit %"],
                100,
            )
            *
            0.40

            +

            (
                1 -
                safe_divide(
                    self.df["Stop Dependency"],
                    100,
                )
            )
            *
            0.20

        ) * 100


        return self

    # ---------------------------------------------------------
    # Institutional Exit Score
    # ---------------------------------------------------------

    def institutional_exit_score(self):
        """
        Final institutional exit score.
        """

        concentration_penalty = (
            1 -
            (
                0.5
                *
                self.df["Exit Concentration"]
            )
        )


        self.df["Institutional Exit Score"] = (

            self.df["Exit Efficiency"] * 0.45

            +

            self.df["Exit Robustness"] * 0.35

            +

            (
                self.df["Exit Diversity Score"]
                *
                100
            )
            *
            0.20

        )


        self.df["Institutional Exit Score"] *= (
            concentration_penalty
        )


        self.df["Institutional Exit Score"] = (
            self.df["Institutional Exit Score"]
            .clip(
                0,
                100,
            )
        )


        return self

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid values.
        """

        columns = [
            "Target Exit %",
            "Trailing Exit %",
            "Stop Dependency",
            "Time Dependency",
            "Winning Exit %",
            "Losing Exit %",
            "Exit Entropy",
            "Exit Diversity Score",
            "Exit Concentration",
            "Exit Efficiency",
            "Exit Robustness",
            "Institutional Exit Score",
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
                    .round(4)
                )

        return self

    # ---------------------------------------------------------
    # Run Pipeline
    # ---------------------------------------------------------

    def run(self):

        logger.info("Calculating exit metrics")

        result = (
            self.prepare_columns()
            .validate()
            .target_exit_percentage()
            .trailing_exit_percentage()
            .stop_dependency()
            .time_dependency()
            .winning_exit_percentage()
            .losing_exit_percentage()
            .exit_diversity()
            .exit_distribution_score()
            .exit_concentration()
            .exit_efficiency()
            .exit_robustness()
            .institutional_exit_score()
            .cleanup()
            .df
        )

        logger.info("Exit metrics completed")

        return result


# ===============================================================
# Convenience Function
# ===============================================================


def derive_exit_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Public API wrapper.
    """

    return ExitMetrics(df).run()


__all__ = [
    "ExitMetrics",
    "derive_exit_metrics",
]
