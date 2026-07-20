"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/distribution_statistics.py

Distribution Statistics Engine

Evaluates the statistical distribution of each
numeric feature.

============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from scipy.stats import (
    skew,
    kurtosis,
    shapiro,
    normaltest,
)

from core.logger import get_logger

logger = get_logger(__name__)


class DistributionStatistics:
    """
    Statistical Distribution Analysis
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # --------------------------------------------------

    @staticmethod
    def coefficient_of_variation(series):
        mean = series.mean()

        if mean == 0:
            return np.nan

        return (series.std() / mean) * 100

    # --------------------------------------------------

    @staticmethod
    def mad(series):
        """
        Mean Absolute Deviation
        """

        return np.mean(np.abs(series - series.mean()))

    # --------------------------------------------------

    @staticmethod
    def median_absolute_deviation(series):
        median = series.median()

        return np.median(np.abs(series - median))

    # --------------------------------------------------

    def generate(self):
        logger.info("Generating distribution statistics...")

        report = []

        numeric = self.df.select_dtypes(include=np.number)

        for column in numeric.columns:
            s = numeric[column].dropna()

            if len(s) == 0:
                continue

            row = {
                "Column": column,
                "Observations": len(s),
                "Variance": s.var(),
                "Std Dev": s.std(),
                "CV %": self.coefficient_of_variation(s),
                "MAD": self.mad(s),
                "Median MAD": self.median_absolute_deviation(s),
                "Skewness": skew(s, bias=False),
                "Kurtosis": kurtosis(s, fisher=True, bias=False),
                "Minimum": s.min(),
                "Q1": s.quantile(0.25),
                "Median": s.median(),
                "Q3": s.quantile(0.75),
                "Maximum": s.max(),
                "Range": s.max() - s.min(),
                "IQR": s.quantile(0.75) - s.quantile(0.25),
            }

            # ------------------------------------------
            # Normality Tests
            # ------------------------------------------

            try:
                if len(s) <= 5000:
                    p = shapiro(s)[1]

                    row["Shapiro p-value"] = p

                    row["Normally Distributed"] = p > 0.05

                else:
                    p = normaltest(s)[1]

                    row["Normal Test p-value"] = p

                    row["Normally Distributed"] = p > 0.05

            except Exception:
                row["Normally Distributed"] = np.nan

            report.append(row)

        logger.info("Distribution statistics completed.")

        return pd.DataFrame(report)


if __name__ == "__main__":
    print("Import in profiler.py")
