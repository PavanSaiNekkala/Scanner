"""
============================================================
Institutional Strategy Comparison Engine V3
File : scoring/reliability_score.py

Reliability Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class ReliabilityScoreEngine:
    """
    Computes Reliability Score using normalized
    reliability-related strategy metrics.
    """

    DEFAULT_WEIGHTS = {
        "Win %": 0.25,
        "Trades": 0.20,
        "Profit Consistency": 0.20,
        "Stability Index": 0.15,
        "Signal Quality": 0.10,
        "Trade Density": 0.10,
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
        logger.info("Generating Reliability Score...")

        self.validate()

        score = np.zeros(len(self.df))

        for feature, weight in self.weights.items():
            score += self.df[feature] * weight

        self.df["Reliability Score"] = score.clip(0, 100).round(2)

        logger.info("Reliability Score completed.")

        return self.df[["Reliability Score"]]


if __name__ == "__main__":
    print("Import inside scoring_engine.py")
