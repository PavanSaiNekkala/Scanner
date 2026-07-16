"""
============================================================
Institutional Strategy Comparison Engine V3
File : scoring/composite_score.py

Composite Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class CompositeScoreEngine:
    """
    Computes the final Composite Score.

    Composite Score is calculated from
    the previously generated score engines.
    """

    DEFAULT_WEIGHTS = {

        "Institutional Score": 0.40,

        "Edge Score": 0.15,

        "Risk Score": 0.10,

        "Efficiency Score": 0.10,

        "Stability Score": 0.10,

        "Reliability Score": 0.05,

        "Opportunity Score": 0.05,

        "Execution Score": 0.05

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

    # -----------------------------------------------------

    def validate(self):

        missing = [

            column

            for column in self.weights

            if column not in self.df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

    # -----------------------------------------------------

    def generate(self):

        logger.info(

            "Generating Composite Score..."

        )

        self.validate()

        score = np.zeros(

            len(self.df)

        )

        for feature, weight in self.weights.items():

            score += (

                self.df[feature]

                * weight

            )

        self.df["Composite Score"] = (

            score

            .clip(0, 100)

            .round(2)

        )

        logger.info(

            "Composite Score completed."

        )

        return self.df[

            ["Composite Score"]

        ]


if __name__ == "__main__":

    print(

        "Import inside scoring_engine.py"

    )