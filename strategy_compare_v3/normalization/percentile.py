"""
============================================================
Institutional Strategy Comparison Engine V3
File : normalization/percentile.py

Production Grade Percentile Normalization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from scipy.stats import rankdata

from core.logger import get_logger

logger = get_logger(__name__)


class PercentileNormalization:
    """
    Percentile Rank Normalization.

    Formula
    -------
    Percentile Rank =
        Rank(X) / (N - 1) × 100

    Advantages
    ----------
    • Distribution independent
    • Resistant to outliers
    • Excellent for institutional scoring
    • Stable across different datasets
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

        self.numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()

        self.summary_df = pd.DataFrame()

    # ==================================================
    # NORMALIZATION
    # ==================================================

    def generate(self) -> pd.DataFrame:
        logger.info("Running Percentile Normalization...")

        normalized = self.df.copy()

        if self.numeric_columns:
            normalized[self.numeric_columns] = (
                normalized[self.numeric_columns]
                .replace([np.inf, -np.inf], np.nan)
                .astype(np.float64)
            )

        summary = []

        for column in self.numeric_columns:
            series = normalized[column]

            valid = series.notna()

            values = series.loc[valid]

            # ------------------------------------------
            # Skip empty column
            # ------------------------------------------

            if values.empty:
                logger.warning("Skipping '%s' (all values are NaN).", column)

                continue

            # ------------------------------------------
            # Constant column
            # ------------------------------------------

            if values.nunique(dropna=True) <= 1:
                normalized.loc[valid, column] = 100.0

                summary.append(
                    {
                        "Feature": column,
                        "Minimum Percentile": 100.0,
                        "Maximum Percentile": 100.0,
                        "Average Percentile": 100.0,
                    }
                )

                continue

            # ------------------------------------------
            # Rank
            # ------------------------------------------

            ranks = rankdata(values, method="average")

            percentiles = (ranks - 1) / (len(values) - 1) * 100.0

            normalized.loc[valid, column] = percentiles.astype(np.float64)

            summary.append(
                {
                    "Feature": column,
                    "Minimum Percentile": round(float(np.nanmin(percentiles)), 2),
                    "Maximum Percentile": round(float(np.nanmax(percentiles)), 2),
                    "Average Percentile": round(float(np.nanmean(percentiles)), 2),
                }
            )

        self.summary_df = pd.DataFrame(summary)

        logger.info("Percentile normalization completed.")

        return normalized

    # ==================================================
    # STATISTICS
    # ==================================================

    def statistics(self) -> pd.DataFrame:
        return self.summary_df.copy()

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):
        return {
            "Method": "Percentile",
            "Numeric Features": len(self.numeric_columns),
            "Normalized Features": len(self.summary_df),
        }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":
    print("Import this module inside normalization_engine.py")
