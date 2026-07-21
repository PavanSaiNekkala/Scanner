"""
===============================================================
Institutional Strategy Comparison Engine V4

Module
------
scoring_metrics.py

Purpose
-------
Aggregate all derived metrics into institutional
scores, rankings and recommendations.

===============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    INSTITUTION_RANK,
)
from strategy_compare_v4.config.weights import (
    COMPOSITE_WEIGHTS,
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
# Scoring Engine
# ============================================================


class ScoringMetrics:
    """
    Institutional Scoring Engine.

    Responsible for calculating institutional
    scores, rankings and recommendations.
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
        Convert required columns to numeric.
        """

        required = [
            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Annual Return %",
            "Risk Adjusted Return",
            "Holding Efficiency",
            "Profit Velocity",
            "Winning Exit %",
            "Institutional Exit Score",
            "Institutional Opportunity Score",
            "Institutional Efficiency Score",
        ]

        require_columns(
            self.df,
            required,
        )

        for column in required:
            self.df[column] = numeric(self.df[column])

        logger.info(
            "Prepared %d scoring columns.",
            len(required),
        )

        return self

    # ---------------------------------------------------------
    # Edge Score
    # ---------------------------------------------------------

    def edge_score(self):
        """
        Calculate institutional edge score.
        """

        self.df["Edge Score"] = (
            normalize(self.df["Expectancy"]) * 0.35
            + normalize(self.df["Profit Factor"]) * 0.30
            + normalize(self.df["Reward Risk"]) * 0.20
            + normalize(self.df["Winning Exit %"]) * 0.15
        )

        return self

    # ---------------------------------------------------------
    # Reliability Score
    # ---------------------------------------------------------

    def reliability_score(self):
        """
        Calculate reliability score.
        """

        self.df["Reliability Score"] = (
            normalize(self.df["Institutional Exit Score"]) * 0.40
            + normalize(self.df["Institutional Opportunity Score"]) * 0.35
            + normalize(self.df["Institutional Efficiency Score"]) * 0.25
        )

        return self

    # ---------------------------------------------------------
    # Opportunity Score
    # ---------------------------------------------------------

    def opportunity_score(self):
        """
        Calculate opportunity score.
        """

        self.df["Opportunity Score"] = (
            normalize(self.df["Profit Velocity"]) * 0.60
            + normalize(self.df["Annual Return %"]) * 0.40
        )

        return self

    # ---------------------------------------------------------
    # Efficiency Score
    # ---------------------------------------------------------

    def efficiency_score(self):
        """
        Calculate efficiency score.
        """

        self.df["Efficiency Score"] = (
            normalize(self.df["Holding Efficiency"]) * 0.50
            + normalize(self.df["Institutional Efficiency Score"]) * 0.50
        )

        return self

    # ---------------------------------------------------------
    # Risk Score
    # ---------------------------------------------------------

    def risk_score(self):
        """
        Calculate institutional risk score.
        Higher Risk Adjusted Return indicates
        lower investment risk.
        """

        self.df["Risk Score"] = (
            normalize(self.df["Risk Adjusted Return"]) * 0.70
            + normalize(self.df["Institutional Exit Score"]) * 0.30
        )

        return self

    # ---------------------------------------------------------
    # Return Score
    # ---------------------------------------------------------

    def return_score(self):
        """
        Calculate return generation score.
        """

        self.df["Return Score"] = (
            normalize(self.df["Annual Return %"]) * 0.60
            + normalize(self.df["Profit Velocity"]) * 0.40
        )

        return self

    # ---------------------------------------------------------
    # Consistency Score
    # ---------------------------------------------------------

    def consistency_score(self):
        """
        Measure consistency of strategy performance.
        """

        self.df["Consistency Score"] = (
            normalize(self.df["Institutional Exit Score"]) * 0.35
            + normalize(self.df["Institutional Opportunity Score"]) * 0.35
            + normalize(self.df["Institutional Efficiency Score"]) * 0.30
        )

        return self

    # ---------------------------------------------------------
    # Institutional Strength
    # ---------------------------------------------------------

    def institutional_strength(self):
        """
        Overall institutional strength.
        """

        self.df["Institutional Strength"] = (
            self.df["Edge Score"] * 0.30
            + self.df["Reliability Score"] * 0.30
            + self.df["Opportunity Score"] * 0.20
            + self.df["Efficiency Score"] * 0.20
        )

        return self

    # ---------------------------------------------------------
    # Composite Score
    # ---------------------------------------------------------

    def composite_score(self):
        """
        Calculate the master institutional score
        using centralized configuration weights.
        """

        self.df[COMPOSITE_SCORE] = (
            self.df["Edge Score"] * COMPOSITE_WEIGHTS["Edge Score"]
            + self.df["Reliability Score"] * COMPOSITE_WEIGHTS["Reliability Score"]
            + self.df["Risk Score"] * COMPOSITE_WEIGHTS["Risk Score"]
            + self.df["Opportunity Score"] * COMPOSITE_WEIGHTS["Opportunity Score"]
            + self.df["Efficiency Score"] * COMPOSITE_WEIGHTS["Efficiency Score"]
            + self.df["Return Score"] * COMPOSITE_WEIGHTS["Return Score"]
        )

        return self

    # ---------------------------------------------------------
    # Confidence Score
    # ---------------------------------------------------------

    def confidence_score(self):
        """
        Estimate confidence that the strategy
        can reproduce historical performance.
        """

        self.df["Confidence Score"] = (
            self.df["Reliability Score"] * 0.50
            + self.df["Consistency Score"] * 0.30
            + self.df["Risk Score"] * 0.20
        )

        return self

    # ---------------------------------------------------------
    # Stability Score
    # ---------------------------------------------------------

    def stability_score(self):
        """
        Long-term stability score.
        """

        self.df["Stability Score"] = (
            self.df["Reliability Score"] * 0.40
            + self.df["Risk Score"] * 0.30
            + self.df["Efficiency Score"] * 0.30
        )

        return self

    # ---------------------------------------------------------
    # Performance Score
    # ---------------------------------------------------------

    def performance_score(self):
        """
        Overall trading performance score.
        """

        self.df["Performance Score"] = (
            self.df["Return Score"] * 0.40
            + self.df["Edge Score"] * 0.35
            + self.df["Efficiency Score"] * 0.25
        )

        return self

    # ---------------------------------------------------------
    # Alpha Score
    # ---------------------------------------------------------

    def alpha_score(self):
        """
        Calculate excess trading edge after
        adjusting for risk.
        """

        self.df["Alpha Score"] = self.df["Edge Score"] - self.df["Risk Score"] * 0.25

        return self

    # ---------------------------------------------------------

    # Institutional Grade

    # ---------------------------------------------------------

    def institutional_grade(self):
        """

        Assign institutional letter grade.

        """

        score = self.df[COMPOSITE_SCORE]

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

    # ---------------------------------------------------------
    # Risk Grade
    # ---------------------------------------------------------

    def risk_grade(self):
        """

        Assign institutional risk grade.

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

    # ---------------------------------------------------------
    # Percentile Rank
    # ---------------------------------------------------------

    def percentile_rank(self):
        """

        Calculate percentile ranking.

        """

        self.df["Percentile Rank"] = (
            self.df[COMPOSITE_SCORE].rank(
                pct=True,
                ascending=True,
            )
            * 100
        )

        return self

    # ---------------------------------------------------------
    # Institution Rank
    # ---------------------------------------------------------

    def overall_rank(self):
        """

        Calculate institutional ranking.

        """

        self.df[INSTITUTION_RANK] = (
            self.df[COMPOSITE_SCORE]
            .rank(
                ascending=False,
                method="dense",
            )
            .astype(int)
        )

        return self

    # ---------------------------------------------------------
    # Final Institutional Score
    # ---------------------------------------------------------

    def final_institutional_score(self):
        """

        Calculate final institutional score.

        """

        self.df["Final Institutional Score"] = (
            self.df[COMPOSITE_SCORE] * 0.70 + self.df["Confidence Score"] * 0.30
        )

        return self

    # ---------------------------------------------------------
    # Recommendation
    # ---------------------------------------------------------

    def recommendation(self):
        """

        Assign institutional recommendation.

        """

        from strategy_compare_v4.config.recommendations import (
            assign_recommendations,
        )

        self.df = assign_recommendations(self.df)

        return self

    # ---------------------------------------------------------
    # Normalize Scores
    # ---------------------------------------------------------

    def normalize_scores(self):
        """

        Normalize institutional scores.

        """

        metrics = [
            "Edge Score",
            "Reliability Score",
            "Risk Score",
            "Opportunity Score",
            "Efficiency Score",
            "Return Score",
            "Consistency Score",
            "Institutional Strength",
            COMPOSITE_SCORE,
            "Confidence Score",
            "Stability Score",
            "Performance Score",
            "Alpha Score",
            "Final Institutional Score",
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

        Replace invalid values.

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

        Round all numeric metrics.

        """

        numeric_columns = self.df.select_dtypes(include="number").columns

        self.df[numeric_columns] = self.df[numeric_columns].round(2)

        return self

    # ---------------------------------------------------------
    # Sort Results
    # ---------------------------------------------------------

    def sort_results(self):
        """

        Sort final institutional output.

        """

        self.df = self.df.sort_values(
            by=[
                INSTITUTION_RANK,
                COMPOSITE_SCORE,
            ],
            ascending=[
                True,
                False,
            ],
        ).reset_index(
            drop=True,
        )

        return self

    # ---------------------------------------------------------
    # Execute Engine
    # ---------------------------------------------------------

    def run(self):
        """

        Execute complete institutional

        scoring pipeline.

        """

        logger.info("Running Institutional Scoring Engine...")

        return (
            self.prepare_columns()
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
            .institutional_grade()
            .risk_grade()
            .percentile_rank()
            .overall_rank()
            .final_institutional_score()
            .recommendation()
            .normalize_scores()
            .cleanup()
            .round_metrics()
            .sort_results()
            .df
        )


# ============================================================
# Convenience Function
# ============================================================


def derive_scoring_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """

    Derive institutional scoring metrics.

    """

    logger.info("Deriving Institutional Scoring Metrics...")

    return ScoringMetrics(df).run()
