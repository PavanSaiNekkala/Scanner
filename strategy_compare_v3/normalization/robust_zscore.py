"""
============================================================
Institutional Strategy Comparison Engine V3
File : normalization/robust_zscore.py

Robust Z-Score Normalization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from scipy.stats import median_abs_deviation

from core.logger import get_logger

logger = get_logger(__name__)


class RobustZScoreNormalization:
    """
    Robust Z-Score Normalization.

    Formula
    -------
    Robust Z = (X - Median) / (1.4826 × MAD)

    where

    MAD = Median Absolute Deviation

    Advantages
    ----------
    • Resistant to outliers
    • Suitable for financial datasets
    • Suitable for skewed distributions
    """

    CONSISTENCY_CONSTANT = 1.4826

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

        self.numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()

        self.statistics_df = pd.DataFrame()

    # -----------------------------------------------------

    def generate(self) -> pd.DataFrame:
        logger.info("Running Robust Z-Score Normalization...")

        normalized = self.df.copy()

        statistics = []

        for column in self.numeric_columns:
            series = normalized[column].astype(float)

            median = series.median()

            mad = median_abs_deviation(series, nan_policy="omit", scale=1)

            if np.isnan(mad) or mad == 0:
                logger.warning("Skipping %s (MAD = %.6f)", column, mad)

                normalized[column] = np.nan

                statistics.append(
                    {"Feature": column, "Median": median, "MAD": mad, "Scale": np.nan}
                )

                continue

            scale = self.CONSISTENCY_CONSTANT * mad

            normalized[column] = (series - median) / scale

            statistics.append(
                {"Feature": column, "Median": median, "MAD": mad, "Scale": scale}
            )

        self.statistics_df = pd.DataFrame(statistics)

        logger.info("Robust Z-Score normalization completed.")

        return normalized

    # -----------------------------------------------------

    def statistics(self) -> pd.DataFrame:
        """
        Returns normalization statistics.
        """

        return self.statistics_df.copy()

    # -----------------------------------------------------

    def summary(self) -> dict:
        return {
            "Method": "Robust Z-Score",
            "Numeric Features": len(self.numeric_columns),
            "Normalized Features": len(self.statistics_df),
        }


if __name__ == "__main__":
    print("Import inside normalization_engine.py")
