"""
============================================================
Institutional Strategy Comparison Engine V3
File : scoring/edge_score.py

Edge Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class EdgeScoreEngine:
    """
    Computes Edge Score using normalized
    strategy performance metrics.
    """

    DEFAULT_WEIGHTS = {

        "Expectancy%": 0.30,

        "Profit Factor": 0.25,

        "Reward Risk Ratio": 0.20,

        "Win %": 0.15,

        "Edge Ratio": 0.10,

    }

    def __init__(

        self,

        dataframe: pd.DataFrame,

        weights: dict | None = None

    ):

        self.df = dataframe.copy()

        self.weights = (

            weights

            if weights is not None

            else self.DEFAULT_WEIGHTS

        )

    # --------------------------------------------------

    def validate(self):

        missing = [

            c

            for c in self.weights

            if c not in self.df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

    # --------------------------------------------------

    def generate(self):

        logger.info(

            "Generating Edge Score..."

        )

        self.validate()

        score = np.zeros(

            len(self.df)

        )

        for feature, weight in self.weights.items():

            score += (

                self.df[feature]

                *

                weight

            )

        self.df["Edge Score"] = (

            score

            .clip(0, 100)

            .round(2)

        )

        logger.info(

            "Edge Score completed."

        )

        return self.df[
            ["Edge Score"]
        ]


if __name__ == "__main__":

    print(

        "Import inside scoring_engine.py"

    )