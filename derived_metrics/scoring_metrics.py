"""
===============================================================
Institutional Strategy Comparison Engine V3

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


# ============================================================
# Utility Functions
# ============================================================

def numeric(series):

    return pd.to_numeric(

        series,

        errors="coerce"

    )


def normalize(series):

    """
    Min-Max normalization (0-100)
    """

    series = numeric(series)

    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):

        return pd.Series(
            np.nan,
            index=series.index
        )

    if maximum == minimum:

        return pd.Series(
            50.0,
            index=series.index
        )

    return (

        (series - minimum)

        /

        (maximum - minimum)

        * 100

    )


# ============================================================
# Scoring Engine
# ============================================================

class ScoringMetrics:

    def __init__(self, df):

        self.df = df.copy()

    # ---------------------------------------------------------

    def prepare_columns(self):

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

            "Institutional Efficiency Score"

        ]

        for col in required:

            if col in self.df.columns:

                self.df[col] = numeric(

                    self.df[col]

                )

        return self
    
    # ---------------------------------------------------------

    def composite_score(self):
        """
        Master institutional score.
        """

        self.df["Composite Score"] = (

            self.df["Edge Score"] * 0.25

            +

            self.df["Reliability Score"] * 0.20

            +

            self.df["Risk Score"] * 0.15

            +

            self.df["Opportunity Score"] * 0.15

            +

            self.df["Efficiency Score"] * 0.15

            +

            self.df["Return Score"] * 0.10

        )

        return self

    # ---------------------------------------------------------

    def confidence_score(self):
        """
        Confidence that strategy
        performance is repeatable.
        """

        self.df["Confidence Score"] = (

            self.df["Reliability Score"] * 0.50

            +

            self.df["Consistency Score"] * 0.30

            +

            self.df["Risk Score"] * 0.20

        )

        return self

    # ---------------------------------------------------------

    def stability_score(self):
        """
        Long-term stability score.
        """

        self.df["Stability Score"] = (

            self.df["Reliability Score"] * 0.40

            +

            self.df["Risk Score"] * 0.30

            +

            self.df["Efficiency Score"] * 0.30

        )

        return self

    # ---------------------------------------------------------

    def performance_score(self):
        """
        Measures overall trading performance.
        """

        self.df["Performance Score"] = (

            self.df["Return Score"] * 0.40

            +

            self.df["Edge Score"] * 0.35

            +

            self.df["Efficiency Score"] * 0.25

        )

        return self

    # ---------------------------------------------------------

    def alpha_score(self):
        """
        Measures excess trading edge.
        """

        self.df["Alpha Score"] = (

            self.df["Edge Score"]

            -

            self.df["Risk Score"] * 0.25

        )

        return self

    # ---------------------------------------------------------

    def institutional_grade(self):
        """
        Letter grade based on Composite Score.
        """

        score = self.df["Composite Score"]

        self.df["Institutional Grade"] = np.select(

            [

                score >= 90,

                score >= 80,

                score >= 70,

                score >= 60,

                score >= 50

            ],

            [

                "A+",

                "A",

                "B",

                "C",

                "D"

            ],

            default="F"

        )

        return self

    # ---------------------------------------------------------

    def risk_grade(self):
        """
        Risk grade.
        """

        risk = self.df["Risk Score"]

        self.df["Risk Grade"] = np.select(

            [

                risk >= 90,

                risk >= 75,

                risk >= 60,

                risk >= 45

            ],

            [

                "Low",

                "Moderate",

                "Elevated",

                "High"

            ],

            default="Very High"

        )

        return self

    # ---------------------------------------------------------

    def percentile_rank(self):
        """
        Percentile rank across strategies.
        """

        self.df["Percentile Rank"] = (

            self.df["Composite Score"]

            .rank(

                pct=True,

                ascending=True

            )

            * 100

        )

        return self

    # ---------------------------------------------------------

    def overall_rank(self):
        """
        Overall institutional rank.
        """

        self.df["Institution Rank"] = (

            self.df["Composite Score"]

            .rank(

                ascending=False,

                method="dense"

            )

            .astype(int)

        )

        return self

    # ---------------------------------------------------------

    def final_institutional_score(self):
        """
        Final score after confidence adjustment.
        """

        self.df["Final Institutional Score"] = (

            self.df["Composite Score"] * 0.70

            +

            self.df["Confidence Score"] * 0.30

        )

        return self
    
    # ---------------------------------------------------------

    def recommendation(self):
        """
        Institutional recommendation based on
        Final Institutional Score.
        """

        score = self.df["Final Institutional Score"]

        conditions = [

            score >= 90,

            (score >= 80) & (score < 90),

            (score >= 70) & (score < 80),

            (score >= 60) & (score < 70),

            (score >= 50) & (score < 60)

        ]

        choices = [

            "Strong Buy",

            "Buy",

            "Watch",

            "Improve",

            "Avoid"

        ]

        self.df["Recommendation"] = np.select(

            conditions,

            choices,

            default="Reject"

        )

        return self

    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize major institutional scores.
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

            "Composite Score",

            "Confidence Score",

            "Stability Score",

            "Performance Score",

            "Alpha Score",

            "Final Institutional Score"

        ]

        for metric in metrics:

            if metric not in self.df.columns:

                continue

            self.df[f"{metric} (Norm)"] = normalize(

                self.df[metric]

            )

        return self

    # ---------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid numeric values.
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
        Round all institutional scores.
        """

        score_cols = [

            "Edge Score",

            "Reliability Score",

            "Opportunity Score",

            "Efficiency Score",

            "Risk Score",

            "Return Score",

            "Consistency Score",

            "Institutional Strength",

            "Composite Score",

            "Confidence Score",

            "Stability Score",

            "Performance Score",

            "Alpha Score",

            "Final Institutional Score",

            "Percentile Rank"

        ]

        for col in score_cols:

            if col in self.df.columns:

                self.df[col] = self.df[col].round(2)

        return self

    # ---------------------------------------------------------

    def sort_results(self):
        """
        Sort strategies from best to worst.
        """

        self.df = self.df.sort_values(

            by=[

                "Institution Rank",

                "Composite Score"

            ],

            ascending=[

                True,

                False

            ]

        ).reset_index(

            drop=True

        )

        return self

    # ---------------------------------------------------------

    def run(self):

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
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Derive all institutional scoring metrics.
    """

    return ScoringMetrics(df).run()