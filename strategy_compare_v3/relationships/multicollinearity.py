"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/multicollinearity.py

Production Grade Multicollinearity Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from numpy.linalg import eigvals
from statsmodels.stats.outliers_influence import (
    variance_inflation_factor,
)

from core.logger import get_logger

logger = get_logger(__name__)


class Multicollinearity:
    """
    Production-grade multicollinearity analysis.

    Generates

    ✓ Variance Inflation Factors
    ✓ Correlation Redundancy
    ✓ Eigenvalues
    ✓ Condition Number
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
    ):
        df = dataframe.select_dtypes(include=np.number).copy()

        # -----------------------------------------
        # Clean dataset
        # -----------------------------------------

        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True,
        )

        df.dropna(
            axis=1,
            how="all",
            inplace=True,
        )

        if not df.empty:
            df = df.fillna(df.median(numeric_only=True))

            # Remove constant columns

            df = df.loc[:, df.nunique(dropna=False) > 1]

        self.df = df

    # ==================================================
    # VIF
    # ==================================================

    def vif(self):
        logger.info("Calculating VIF...")

        if self.df.shape[1] < 2:
            logger.warning("Insufficient columns for VIF.")

            return pd.DataFrame(
                {
                    "Information": ["VIF skipped"],
                    "Reason": ["Less than two usable numeric columns."],
                }
            )

        report = []

        X = self.df.astype(float)

        for i, col in enumerate(X.columns):
            try:
                vif_value = variance_inflation_factor(
                    X.values,
                    i,
                )

            except Exception as exc:
                logger.warning(
                    "Unable to compute VIF for %s : %s",
                    col,
                    exc,
                )

                vif_value = np.nan

            report.append(
                {
                    "Feature": col,
                    "VIF": (
                        round(
                            float(vif_value),
                            4,
                        )
                        if pd.notna(vif_value)
                        else np.nan
                    ),
                }
            )

        report = pd.DataFrame(report)

        report["Severity"] = np.select(
            [
                report["VIF"] < 5,
                report["VIF"] < 10,
            ],
            [
                "Low",
                "Moderate",
            ],
            default="High",
        )

        return report.sort_values(
            "VIF",
            ascending=False,
            na_position="last",
        ).reset_index(drop=True)

    # ==================================================
    # CORRELATION REDUNDANCY
    # ==================================================

    def correlation_redundancy(
        self,
        threshold=0.95,
    ):
        if self.df.shape[1] < 2:
            return pd.DataFrame()

        corr = self.df.corr().abs()

        upper = corr.where(
            np.triu(
                np.ones(corr.shape),
                k=1,
            ).astype(bool)
        )

        redundant = []

        for column in upper.columns:
            correlated = upper.index[upper[column] >= threshold].tolist()

            if correlated:
                redundant.append(
                    {
                        "Feature": column,
                        "Highly Correlated With": ", ".join(correlated),
                    }
                )

        return pd.DataFrame(redundant)

    # ==================================================
    # EIGENVALUES
    # ==================================================

    def eigenvalues(self):
        if self.df.shape[1] < 2:
            return pd.DataFrame()

        try:
            corr = self.df.corr()

            values = eigvals(corr)

            return (
                pd.DataFrame({"Eigenvalue": values.real})
                .sort_values(
                    "Eigenvalue",
                    ascending=False,
                )
                .reset_index(drop=True)
            )

        except Exception as exc:
            logger.warning(
                "Eigenvalue computation failed: %s",
                exc,
            )

            return pd.DataFrame()

    # ==================================================
    # CONDITION NUMBER
    # ==================================================

    def condition_number(self):
        if self.df.shape[1] < 2:
            return np.nan

        try:
            corr = self.df.corr()

            eig = np.real(eigvals(corr))

            eig = eig[eig > 1e-12]

            if len(eig) == 0:
                return np.nan

            return round(
                float(np.sqrt(eig.max() / eig.min())),
                4,
            )

        except Exception as exc:
            logger.warning(
                "Condition number failed: %s",
                exc,
            )

            return np.nan

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):
        logger.info("Generating multicollinearity report...")

        return {
            "VIF": self.vif(),
            "Redundant Features": self.correlation_redundancy(),
            "Eigenvalues": self.eigenvalues(),
            "Condition Number": pd.DataFrame(
                {
                    "Metric": ["Condition Number"],
                    "Value": [self.condition_number()],
                }
            ),
        }


if __name__ == "__main__":
    print("Import Multicollinearity from relationship_engine.py")
