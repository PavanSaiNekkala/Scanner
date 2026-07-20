"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/dependency_matrix.py

Production Grade Dependency Matrix Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.feature_selection import mutual_info_regression

from core.logger import get_logger

logger = get_logger(__name__)


class DependencyMatrix:
    """
    Generates dependency analytics for
    all numeric variables.

    Produces

    ✓ Covariance Matrix
    ✓ Mutual Information Matrix
    ✓ Dependency Strength Report
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.select_dtypes(include=np.number).copy()

        self.df = self._prepare_numeric()

    # ==================================================
    # DATA PREPARATION
    # ==================================================

    def _prepare_numeric(self) -> pd.DataFrame:
        df = self.df.copy()

        if df.empty:
            return df

        # Replace infinities

        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Remove empty columns

        df.dropna(axis=1, how="all", inplace=True)

        if df.empty:
            return df

        # Fill NaN using median

        medians = df.median(numeric_only=True)

        df = df.fillna(medians)

        # Remove constant columns

        df = df.loc[:, df.nunique(dropna=False) > 1]

        return df

    # ==================================================
    # COVARIANCE
    # ==================================================

    def covariance(self):
        logger.info("Computing covariance matrix...")

        if self.df.empty:
            return pd.DataFrame()

        return self.df.cov()

    # ==================================================
    # MUTUAL INFORMATION
    # ==================================================

    def mutual_information(self):
        logger.info("Computing mutual information...")

        if self.df.shape[1] < 2:
            return pd.DataFrame()

        cols = self.df.columns

        mi = pd.DataFrame(index=cols, columns=cols, dtype=float)

        for target in cols:
            X = self.df.drop(columns=target)

            y = self.df[target]

            if X.empty:
                mi.loc[target, target] = 1.0

                continue

            try:
                scores = mutual_info_regression(X, y, random_state=42)

                mi.loc[target, target] = 1.0

                mi.loc[target, X.columns] = scores

            except Exception as exc:
                logger.warning("Mutual information skipped for %s : %s", target, exc)

                mi.loc[target] = np.nan

                mi.loc[target, target] = 1.0

        return mi.fillna(0)

    # ==================================================
    # DEPENDENCY STRENGTH
    # ==================================================

    def dependency_strength(self):
        logger.info("Computing dependency strengths...")

        if self.df.shape[1] < 2:
            return pd.DataFrame()

        corr = self.df.corr()

        rows = []

        cols = corr.columns

        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                value = corr.iloc[i, j]

                if pd.isna(value):
                    continue

                absolute = abs(value)

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
                        "Feature A": cols[i],
                        "Feature B": cols[j],
                        "Correlation": round(value, 4),
                        "Absolute": round(absolute, 4),
                        "Strength": strength,
                    }
                )

        if not rows:
            return pd.DataFrame()

        return (
            pd.DataFrame(rows)
            .sort_values("Absolute", ascending=False)
            .reset_index(drop=True)
        )

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating dependency analytics...")

        return {
            "Covariance": self.covariance(),
            "Mutual Information": self.mutual_information(),
            "Dependency Strength": self.dependency_strength(),
        }


if __name__ == "__main__":
    print("Import DependencyMatrix from relationship_engine.py")
