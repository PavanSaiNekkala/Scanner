"""
============================================================
Institutional Strategy Comparison Engine V3
File : recommendation/recommendation_engine.py

Recommendation Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import pandas as pd

from core.logger import get_logger
from recommendation.thresholds import RecommendationThresholds

logger = get_logger(__name__)


class RecommendationEngine:
    """
    Institutional Recommendation Engine.

    Generates recommendations from the
    Composite Score.
    """

    SCORE_COLUMN = "Composite Score"

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()

    # --------------------------------------------------

    def validate(self):

        if self.SCORE_COLUMN not in self.df.columns:

            raise ValueError(

                f"'{self.SCORE_COLUMN}' column not found."

            )

    # --------------------------------------------------

    def generate_recommendation(self):

        self.df["Recommendation"] = (

            self.df[self.SCORE_COLUMN]

            .apply(

                RecommendationThresholds.get_label

            )

        )

    # --------------------------------------------------

    def generate_color(self):

        self.df["Recommendation Color"] = (

            self.df[self.SCORE_COLUMN]

            .apply(

                RecommendationThresholds.get_color

            )

        )

    # --------------------------------------------------

    def recommendation_rank(self):

        ranking = {

            "STRONG BUY": 1,

            "BUY": 2,

            "ACCUMULATE": 3,

            "WATCH": 4,

            "HOLD": 5,

            "REDUCE": 6,

            "SELL": 7,

            "AVOID": 8

        }

        self.df["Recommendation Rank"] = (

            self.df["Recommendation"]

            .map(ranking)

            .astype(int)

        )

    # --------------------------------------------------

    def confidence(self):

        """
        Confidence is based on the
        Composite Score itself.
        """

        self.df["Recommendation Confidence"] = (

            self.df[self.SCORE_COLUMN]

            .clip(0, 100)

            .round(2)

        )

    # --------------------------------------------------

    def sort(self):

        self.df = (

            self.df

            .sort_values(

                by=[

                    "Recommendation Rank",

                    self.SCORE_COLUMN

                ],

                ascending=[

                    True,

                    False

                ]

            )

            .reset_index(

                drop=True

            )

        )

    # --------------------------------------------------

    def generate(self):

        logger.info(

            "Generating Recommendations..."

        )

        self.validate()

        self.generate_recommendation()

        self.generate_color()

        self.recommendation_rank()

        self.confidence()

        self.sort()

        logger.info(

            "Recommendation generation completed."

        )

        return self.df


if __name__ == "__main__":

    print(

        "Import inside main.py"

    )