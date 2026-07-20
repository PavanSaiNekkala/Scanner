"""
============================================================
Institutional Strategy Comparison Engine V3
File : scoring/institutional_score.py

Institutional Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class InstitutionalScoreEngine:
    """
    Computes Institutional Score.

    Institutional Score is a weighted
    aggregation of all domain scores.
    """

    DEFAULT_WEIGHTS = {
        "Edge Score": 0.20,
        "Risk Score": 0.15,
        "Efficiency Score": 0.15,
        "Stability Score": 0.15,
        "Reliability Score": 0.15,
        "Opportunity Score": 0.10,
        "Execution Score": 0.10,
    }

    def __init__(self, dataframe: pd.DataFrame, weights: dict | None = None):
        self.df = dataframe.copy()

        self.weights = weights if weights is not None else self.DEFAULT_WEIGHTS

    # --------------------------------------------------

    def validate(self):
        missing = [
            feature for feature in self.weights if feature not in self.df.columns
        ]

        if missing:
            raise ValueError(f"Missing columns: {missing}")

    # --------------------------------------------------

    def generate(self):
        logger.info("Generating Institutional Score...")

        self.validate()

        score = np.zeros(len(self.df))

        for feature, weight in self.weights.items():
            score += self.df[feature] * weight

        self.df["Institutional Score"] = score.clip(0, 100).round(2)

        logger.info("Institutional Score completed.")

        return self.df[["Institutional Score"]]


if __name__ == "__main__":
    print("Import inside scoring_engine.py")
