"""
============================================================
Institutional Strategy Comparison Engine V3

File : recommendation/recommendation_engine.py

Master Recommendation Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import numpy as np

import pandas as pd


from core.logger import get_logger

logger = get_logger(__name__)


class RecommendationEngine:
    """
    Institutional Recommendation Engine.


    Generates final strategy recommendation
    based on Composite Score.


    Output Contract
    ---------------

    Composite Score

    Recommendation


    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate(self):
        required = ["Composite Score"]

        missing = [col for col in required if col not in self.df.columns]

        if missing:
            raise ValueError(f"Missing recommendation columns: {missing}")

    # ==================================================
    # RECOMMENDATION LOGIC
    # ==================================================

    def generate_recommendation(self):
        score = self.df["Composite Score"]

        conditions = [score >= 85, score >= 70, score >= 50, score >= 30]

        choices = ["Strong Buy", "Buy", "Watch", "Avoid"]

        self.df["Recommendation"] = np.select(conditions, choices, default="Reject")

    # ==================================================
    # QUALITY LABEL
    # ==================================================

    def generate_quality_grade(self):
        if "Composite Score" not in self.df.columns:
            return

        score = self.df["Composite Score"]

        conditions = [score >= 90, score >= 75, score >= 60, score >= 40]

        choices = ["Institutional Grade", "High Quality", "Acceptable", "Low Quality"]

        self.df["Quality Grade"] = np.select(conditions, choices, default="Poor")

    # ==================================================
    # FINAL OUTPUT
    # ==================================================

    def generate(self):
        logger.info("Generating Recommendations...")

        self.validate()

        self.generate_recommendation()

        self.generate_quality_grade()

        logger.info("Recommendation generation completed.")

        return self.df


if __name__ == "__main__":
    print("Import RecommendationEngine inside pipeline")
