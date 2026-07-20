"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/correlation.py

Production Grade Correlation Analysis Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class CorrelationEngine:
    """
    Production-grade correlation analysis.

    Generates

    ✓ Pearson Correlation
    ✓ Spearman Correlation
    ✓ Kendall Correlation
    ✓ Strong Relationship Report
    """

    def __init__(self, dataframe: pd.DataFrame):
        df = dataframe.select_dtypes(include=np.number).copy()

        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        df.dropna(axis=1, how="all", inplace=True)

        if not df.empty:
            df = df.fillna(df.median(numeric_only=True))

            # Remove constant columns

            df = df.loc[:, df.nunique(dropna=False) > 1]

        self.df = df

    # =====================================================
    # INTERNAL
    # =====================================================

    def _empty_check(self):
        return self.df.shape[1] >= 2

    # =====================================================
    # PEARSON
    # =====================================================

    def pearson(self):
        logger.info("Computing Pearson correlation...")

        if not self._empty_check():
            return pd.DataFrame()

        return self.df.corr(method="pearson")

    # =====================================================
    # SPEARMAN
    # =====================================================

    def spearman(self):
        logger.info("Computing Spearman correlation...")

        if not self._empty_check():
            return pd.DataFrame()

        return self.df.corr(method="spearman")

    # =====================================================
    # KENDALL
    # =====================================================

    def kendall(self):
        logger.info("Computing Kendall correlation...")

        if not self._empty_check():
            return pd.DataFrame()

        return self.df.corr(method="kendall")

    # =====================================================
    # STRONG RELATIONSHIPS
    # =====================================================

    def strongest_relationships(self, method="pearson", threshold=0.70):
        logger.info("Finding strong relationships...")

        if not self._empty_check():
            return pd.DataFrame()

        corr = self.df.corr(method=method)

        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

        rows = []

        for column in upper.columns:
            values = upper[column].dropna()

            for feature, value in values.items():
                absolute = abs(value)

                if absolute < threshold:
                    continue

                if absolute >= 0.90:
                    strength = "Very Strong"

                elif absolute >= 0.70:
                    strength = "Strong"

                elif absolute >= 0.50:
                    strength = "Moderate"

                else:
                    strength = "Weak"

                rows.append(
                    {
                        "Feature A": feature,
                        "Feature B": column,
                        "Correlation": round(value, 4),
                        "Absolute": round(absolute, 4),
                        "Strength": strength,
                        "Direction": ("Positive" if value >= 0 else "Negative"),
                    }
                )

        if not rows:
            return pd.DataFrame()

        report = (
            pd.DataFrame(rows)
            .sort_values("Absolute", ascending=False)
            .reset_index(drop=True)
        )

        logger.info("%d strong relationships found.", len(report))

        return report

    # =====================================================
    # GENERATE
    # =====================================================

    def generate(self):
        logger.info("Generating correlation report...")

        return {
            "Pearson": self.pearson(),
            "Spearman": self.spearman(),
            "Kendall": self.kendall(),
            "Strong Relationships": self.strongest_relationships(),
        }


if __name__ == "__main__":
    print("Import CorrelationEngine from relationship_engine.py")
