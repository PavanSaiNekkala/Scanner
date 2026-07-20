"""
============================================================
Institutional Strategy Comparison Engine V3
File : scoring/stability_score.py

Stability Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class StabilityScoreEngine:
    """
    Computes Stability Score using normalized
    stability-related strategy metrics.
    """

    DEFAULT_WEIGHTS = {
        "Trade Density": 0.15,
        "Profit Consistency": 0.25,
        "Expectancy Stability": 0.20,
        "Reward Consistency": 0.15,
        "Holding Stability": 0.10,
        "Stability Index": 0.15,
    }

    def __init__(self, dataframe: pd.DataFrame, weights: dict | None = None):
        self.df = dataframe.copy()

        self.weights = weights if weights is not None else self.DEFAULT_WEIGHTS

    # -----------------------------------------------------

    def validate(self):
        missing = [column for column in self.weights if column not in self.df.columns]

        if missing:
            raise ValueError(f"Missing columns: {missing}")

    # -----------------------------------------------------

    def generate(self):
        logger.info("Generating Stability Score...")

        self.validate()

        score = np.zeros(len(self.df))

        for feature, weight in self.weights.items():
            score += self.df[feature] * weight

        self.df["Stability Score"] = score.clip(0, 100).round(2)

        logger.info("Stability Score completed.")

        return self.df[["Stability Score"]]


if __name__ == "__main__":
    print("Import inside scoring_engine.py")
