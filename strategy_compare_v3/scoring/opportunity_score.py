"""
============================================================
Institutional Strategy Comparison Engine V3
File : scoring/opportunity_score.py

Opportunity Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class OpportunityScoreEngine:
    """
    Computes Opportunity Score using normalized
    opportunity-related strategy metrics.
    """

    DEFAULT_WEIGHTS = {
        "Trades / Year": 0.20,
        "Signal Frequency": 0.15,
        "Opportunity Density": 0.20,
        "Opportunity Velocity": 0.15,
        "Opportunity Capture": 0.10,
        "Opportunity Efficiency": 0.10,
        "Opportunity Strength": 0.05,
        "Opportunity Potential": 0.05,
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
        logger.info("Generating Opportunity Score...")

        self.validate()

        score = np.zeros(len(self.df))

        for feature, weight in self.weights.items():
            score += self.df[feature] * weight

        self.df["Opportunity Score"] = score.clip(0, 100).round(2)

        logger.info("Opportunity Score completed.")

        return self.df[["Opportunity Score"]]


if __name__ == "__main__":
    print("Import inside scoring_engine.py")
