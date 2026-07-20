"""
============================================================
Institutional Strategy Comparison Engine V3
File : normalization/quantile.py

Quantile Normalization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.preprocessing import QuantileTransformer

from core.logger import get_logger

logger = get_logger(__name__)


class QuantileNormalization:
    """
    Quantile Normalization.

    Transforms features to either:

    1. Uniform Distribution
    2. Normal (Gaussian) Distribution

    Advantages
    ----------
    • Handles skewed distributions
    • Robust against outliers
    • Produces comparable feature scales
    • Excellent for machine learning
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        output_distribution: str = "uniform",
        random_state: int = 42,
    ):
        self.df = dataframe.copy()

        self.output_distribution = output_distribution

        self.random_state = random_state

        self.numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()

        self.transformer = QuantileTransformer(
            output_distribution=output_distribution,
            random_state=random_state,
        )

        self.statistics_df = pd.DataFrame()

    # --------------------------------------------------

    def generate(self) -> pd.DataFrame:
        logger.info("Running Quantile Normalization...")

        normalized = self.df.copy()

        if not self.numeric_columns:
            logger.warning("No numeric columns found.")

            return normalized

        transformed = self.transformer.fit_transform(normalized[self.numeric_columns])

        normalized[self.numeric_columns] = transformed

        stats = []

        for column in self.numeric_columns:
            series = normalized[column]

            stats.append(
                {
                    "Feature": column,
                    "Minimum": round(series.min(), 6),
                    "Maximum": round(series.max(), 6),
                    "Mean": round(series.mean(), 6),
                    "Std": round(series.std(), 6),
                    "Distribution": self.output_distribution,
                }
            )

        self.statistics_df = pd.DataFrame(stats)

        logger.info("Quantile normalization completed.")

        return normalized

    # --------------------------------------------------

    def statistics(self) -> pd.DataFrame:
        return self.statistics_df.copy()

    # --------------------------------------------------

    def summary(self):
        return {
            "Method": "Quantile",
            "Distribution": self.output_distribution,
            "Numeric Features": len(self.numeric_columns),
            "Normalized Features": len(self.statistics_df),
        }


if __name__ == "__main__":
    print("Import inside normalization_engine.py")
