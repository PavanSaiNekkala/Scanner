"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
scoring_metrics.py

Purpose
-------
Aggregate derived metrics into institutional
scores, rankings and recommendations.

Institutional Scoring Model

Components:

1. Edge Quality
2. Reliability
3. Risk Control
4. Efficiency
5. Opportunity
6. Return Capability

===============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    INSTITUTION_RANK,
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
)

logger = get_logger(__name__)


# ============================================================
# Institutional Scoring Engine
# ============================================================


class ScoringMetrics:
    """
    Institutional scoring framework.

    Converts derived metrics into
    portfolio ranking scores.
    """

    REQUIRED_COLUMNS = [
        "Expectancy",
        "Profit Factor",
        "Reward Risk",
        "Annual Return %",
        "Risk Adjusted Return",
        "Holding Efficiency",
        "Profit Velocity",
        "Winning Exit %",
        "Validation Score",
        "Validation Consistency",
        "Capital Preservation",
        "Safety Margin",
        "Time Efficiency",
        "Trade Density",
        "Institutional Exit Score",
        "Institutional Opportunity Score",
        "Institutional Efficiency Score",
    ]

    def __init__(
        self,
        df: pd.DataFrame,
    ):

        self.df = df.copy()

        # cache normalized values

        self.norm: dict[str, pd.Series] = {}

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def validate(self):
        """
        Validate mandatory columns.
        """

        require_columns(
            self.df,
            self.REQUIRED_COLUMNS,
        )

        return self

    # --------------------------------------------------------
    # Prepare Columns
    # --------------------------------------------------------

    def prepare_columns(self):
        """
        Normalize legacy fields
        and convert values.
        """

        rename_map = {
            "Avg Win %": "Avg win%",
            "Avg Loss %": "Avg loss%",
            "Maximum Drawdown %": "Max Drawdown %",
            "Total Return %": "Net %",
            "Net Profit %": "Net %",
        }

        for old, new in rename_map.items():
            if old in self.df.columns and new not in self.df.columns:
                self.df[new] = self.df[old]

        for column in self.REQUIRED_COLUMNS:
            self.df[column] = numeric(self.df[column])

        logger.info(
            "Prepared scoring metrics: %d",
            len(self.REQUIRED_COLUMNS),
        )

        return self

    # --------------------------------------------------------
    # Normalization Cache
    # --------------------------------------------------------

    def norm_col(
        self,
        column: str,
    ) -> pd.Series:
        """
        Cached normalization.

        Converts metrics into
        comparable 0-100 scale.
        """

        if column not in self.norm:
            self.norm[column] = normalize(self.df[column])

        return self.norm[column]

    # --------------------------------------------------------
    # Edge Score
    # --------------------------------------------------------

    def edge_score(self):
        """
        Measure trading edge quality.

        Components:

        Expectancy       35%
        Profit Factor    30%
        Reward Risk      20%
        Winning Exit     15%

        """

        self.df["Edge Score"] = (
            self.norm_col("Expectancy") * 0.35
            + self.norm_col("Profit Factor") * 0.30
            + self.norm_col("Reward Risk") * 0.20
            + self.norm_col("Winning Exit %") * 0.15
        )

        return self

    # --------------------------------------------------------
    # Reliability Score
    # --------------------------------------------------------

    def reliability_score(self):
        """
        Measures strategy reliability.

        Components:

        Exit Quality        30%
        Validation          25%
        Consistency         25%
        Efficiency          20%

        """

        self.df["Reliability Score"] = (
            self.norm_col("Institutional Exit Score") * 0.30
            +
            self.norm_col("Validation Score") * 0.25
            +
            self.norm_col("Consistency Score") * 0.25
            +
            self.norm_col("Institutional Efficiency Score") * 0.20
        )

        return self

    # --------------------------------------------------------
    # Opportunity Score
    # --------------------------------------------------------

    def opportunity_score(self):
        """
        Measures opportunity availability.

        """

        self.df["Opportunity Score"] = (
            self.norm_col(
                "Institutional Opportunity Score"
            ) * 0.60
            +
            self.norm_col(
                "Profit Velocity"
            ) * 0.25
            +
            self.norm_col(
                "Trade Density"
            ) * 0.15
        )

        return self
    
    # --------------------------------------------------------
    # Efficiency Score
    # --------------------------------------------------------

    def efficiency_score(self):
        """
        Measure capital and time efficiency.

        """

        self.df["Efficiency Score"] = (
            self.norm_col(
                "Institutional Efficiency Score"
            ) * 0.50
            +
            self.norm_col(
                "Holding Efficiency"
            ) * 0.25
            +
            self.norm_col(
                "Time Efficiency"
            ) * 0.25
        )

        return self

    # --------------------------------------------------------
    # Risk Score
    # --------------------------------------------------------

    def risk_score(self):
        """
        Institutional risk quality.

        """

        self.df["Risk Score"] = (
            self.norm_col(
                "Risk Adjusted Return"
            ) * 0.40
            +
            self.norm_col(
                "Institutional Exit Score"
            ) * 0.25
            +
            self.norm_col(
                "Capital Preservation"
            ) * 0.20
            +
            self.norm_col(
                "Safety Margin"
            ) * 0.15
        )

        return self

    # --------------------------------------------------------
    # Return Score
    # --------------------------------------------------------

    def return_score(self):
        """
        Controlled return capability.
        """

        self.df["Return Score"] = (
            self.norm_col("Annual Return %") * 0.40
            +
            self.norm_col("Profit Velocity") * 0.30
            +
            self.norm_col("Expectancy") * 0.30
        )

        return self

    # --------------------------------------------------------
    # Consistency Score
    # --------------------------------------------------------

    def consistency_score(self):
        """
        Measures stability and repeatability.

        Components:

        Validation Quality     40%
        Exit Stability         30%
        Efficiency Stability  20%
        Opportunity Stability 10%

        """

        self.df["Consistency Score"] = (

            self.norm_col(
                "Validation Score"
            )
            *
            0.40

            +

            self.norm_col(
                "Institutional Exit Score"
            )
            *
            0.30

            +

            self.norm_col(
                "Institutional Efficiency Score"
            )
            *
            0.20

            +

            self.norm_col(
                "Institutional Opportunity Score"
            )
            *
            0.10

        )

        return self

    # --------------------------------------------------------
    # Institutional Strength
    # --------------------------------------------------------

    def institutional_strength(self):

        self.df["Institutional Strength"] = (
            self.df["Edge Score"] * 0.25
            +
            self.df["Reliability Score"] * 0.25
            +
            self.df["Risk Score"] * 0.25
            +
            self.df["Efficiency Score"] * 0.15
            +
            self.df["Opportunity Score"] * 0.10
        )

        return self

    # --------------------------------------------------------
    # Composite Score
    # --------------------------------------------------------

    def composite_score(self):
        """
        Master institutional score.

        Formula:

        Edge              20%
        Reliability       20%
        Risk              20%
        Efficiency        10%
        Opportunity       10%
        Consistency       10%
        Validation        10%

        """

        self.df[COMPOSITE_SCORE] = (

            self.df["Edge Score"] * 0.20

            +

            self.df["Reliability Score"] * 0.20

            +

            self.df["Risk Score"] * 0.20

            +

            self.df["Efficiency Score"] * 0.10

            +

            self.df["Opportunity Score"] * 0.10

            +

            self.df["Consistency Score"] * 0.10

            +

            self.df["Validation Score"] * 0.10

        )

        return self

    # --------------------------------------------------------
    # Confidence Score
    # --------------------------------------------------------

    def confidence_score(self):
        """
        Confidence that historical
        performance can continue.

        """

        self.df["Confidence Score"] = (
            self.df["Reliability Score"] * 0.50
            + self.df["Consistency Score"] * 0.30
            + self.df["Risk Score"] * 0.20
        )

        return self

    # --------------------------------------------------------
    # Stability Score
    # --------------------------------------------------------

    def stability_score(self):
        """
        Long-term institutional stability.

        """

        self.df["Stability Score"] = (
            self.df["Reliability Score"] * 0.40
            + self.df["Risk Score"] * 0.40
            + self.df["Efficiency Score"] * 0.20
        )

        return self

    # --------------------------------------------------------
    # Performance Score
    # --------------------------------------------------------

    def performance_score(self):
        """
        Overall performance quality.

        """

        self.df["Performance Score"] = (
            self.df["Return Score"] * 0.35
            + self.df["Edge Score"] * 0.35
            + self.df["Efficiency Score"] * 0.30
        )

        return self

    # --------------------------------------------------------
    # Alpha Score
    # --------------------------------------------------------

    def alpha_score(self):

        self.df["Alpha Score"] = (
            self.df["Edge Score"]
            -
            (
                self.df["Risk Score"]
                *
                0.25
            )
        )

        return self
    
    # --------------------------------------------------------
    # Institutional Grade
    # --------------------------------------------------------

    def institutional_grade(self):
        """
        Assign institutional quality grade.

        """

        score = self.df[
            "Final Institutional Score"
        ]

        self.df["Institutional Grade"] = np.select(
            [
                score >= 90,
                score >= 80,
                score >= 70,
                score >= 60,
                score >= 50,
            ],
            [
                "A+",
                "A",
                "B",
                "C",
                "D",
            ],
            default="F",
        )

        return self

    # --------------------------------------------------------
    # Risk Grade
    # --------------------------------------------------------

    def risk_grade(self):
        """
        Classify investment risk level.

        Higher Risk Score =
        Better risk quality.

        """

        risk = self.df["Risk Score"]

        self.df["Risk Grade"] = np.select(
            [
                risk >= 90,
                risk >= 75,
                risk >= 60,
                risk >= 45,
            ],
            [
                "Low",
                "Moderate",
                "Elevated",
                "High",
            ],
            default="Very High",
        )

        return self

    # --------------------------------------------------------
    # Percentile Rank
    # --------------------------------------------------------

    def percentile_rank(self):

        self.df["Percentile Rank"] = (
            self.df[
                "Final Institutional Score"
            ]
            .rank(
                pct=True,
                ascending=True,
                method="average",
            )
            *
            100
        )

        return self

    # --------------------------------------------------------
    # Institution Rank
    # --------------------------------------------------------

    def overall_rank(self):
        """
        Calculate final institutional ranking.
        """

        ranking_column = (
            "Final Institutional Score"
            if "Final Institutional Score"
            in self.df.columns
            else COMPOSITE_SCORE
        )


        self.df[INSTITUTION_RANK] = (
            self.df[ranking_column]
            .rank(
                ascending=False,
                method="dense",
            )
            .astype(int)
        )

        return self
    
    # --------------------------------------------------------
    # Final Institutional Score
    # --------------------------------------------------------

    def final_institutional_score(self):
        """
        Final institutional decision score.
        """

        self.df["Final Institutional Score"] = (

            self.df[COMPOSITE_SCORE] * 0.80

            +

            self.df["Confidence Score"] * 0.20

        )

        return self

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    def recommendation(self):
        """
        Apply institutional
        recommendation engine.

        """

        from strategy_compare_v4.config.recommendations import (
            assign_recommendations,
        )

        self.df = assign_recommendations(self.df)

        return self

    # --------------------------------------------------------
    # Normalize Scores
    # --------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize institutional
        scores to 0-100.
        """

        metrics = [
            "Edge Score",
            "Reliability Score",
            "Risk Score",
            "Opportunity Score",
            "Efficiency Score",
            "Return Score",
            "Validation Consistency",
            "Institutional Strength",
            COMPOSITE_SCORE,
            "Confidence Score",
            "Stability Score",
            "Performance Score",
            "Alpha Score",
            "Final Institutional Score",
        ]

        for metric in metrics:
            if metric not in self.df.columns:
                continue

            self.df[f"{metric} (Norm)"] = normalize(self.df[metric])

        return self

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid numeric values.
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

    # --------------------------------------------------------
    # Round Metrics
    # --------------------------------------------------------

    def round_metrics(self):
        """
        Round numeric metrics.
        """

        numeric_columns = self.df.select_dtypes(
            include="number",
        ).columns

        self.df[numeric_columns] = self.df[numeric_columns].round(2)

        return self

    # --------------------------------------------------------
    # Sort Results
    # --------------------------------------------------------

    def sort_results(self):
        """
        Sort final institutional ranking.
        """

        self.df = self.df.sort_values(
            by=[
                INSTITUTION_RANK,
                "Final Institutional Score",
            ],
            ascending=[
                True,
                False,
            ],
        ).reset_index(
            drop=True,
        )

        return self

    # --------------------------------------------------------
    # Execute Engine
    # --------------------------------------------------------

    def run(self):
        """
        Execute complete scoring pipeline.
        """

        logger.info("Running Institutional Scoring Engine...")

        result = (
            self.prepare_columns()
            .validate()
            .edge_score()
            .reliability_score()
            .opportunity_score()
            .efficiency_score()
            .risk_score()
            .return_score()
            .consistency_score()
            .institutional_strength()
            .composite_score()
            .confidence_score()
            .stability_score()
            .performance_score()
            .alpha_score()
            .final_institutional_score()
            .institutional_grade()
            .risk_grade()
            .percentile_rank()
            .overall_rank()
            .recommendation()
            .normalize_scores()
            .cleanup()
            .round_metrics()
            .sort_results()
            .df
        )

        logger.info("Institutional Scoring Engine completed.")

        return result


# ============================================================
# Convenience Function
# ============================================================


def derive_scoring_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Public scoring interface.
    """

    logger.info("Deriving Institutional Scoring Metrics...")

    return ScoringMetrics(df).run()


__all__ = [
    "ScoringMetrics",
    "derive_scoring_metrics",
]
