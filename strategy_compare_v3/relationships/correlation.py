"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/correlation.py

Correlation Analysis Engine

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
    Computes multiple correlation matrices.

    Methods
    -------
    Pearson
    Spearman
    Kendall
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.select_dtypes(
            include=np.number
        ).copy()

    # -----------------------------------------------------

    def pearson(self) -> pd.DataFrame:

        logger.info(
            "Computing Pearson correlation..."
        )

        return self.df.corr(
            method="pearson"
        )

    # -----------------------------------------------------

    def spearman(self) -> pd.DataFrame:

        logger.info(
            "Computing Spearman correlation..."
        )

        return self.df.corr(
            method="spearman"
        )

    # -----------------------------------------------------

    def kendall(self) -> pd.DataFrame:

        logger.info(
            "Computing Kendall correlation..."
        )

        return self.df.corr(
            method="kendall"
        )

    # -----------------------------------------------------

    def strongest_relationships(
        self,
        method: str = "pearson",
        threshold: float = 0.70
    ) -> pd.DataFrame:
        """
        Return feature pairs whose absolute
        correlation exceeds the threshold.
        """

        corr = self.df.corr(
            method=method
        )

        upper = corr.where(
            np.triu(
                np.ones(
                    corr.shape
                ),
                k=1
            ).astype(bool)
        )

        rows = []

        for col in upper.columns:

            values = upper[col].dropna()

            for idx, value in values.items():

                if abs(value) >= threshold:

                    rows.append({

                        "Feature 1":

                            idx,

                        "Feature 2":

                            col,

                        "Correlation":

                            round(
                                value,
                                4
                            ),

                        "Strength":

                            (
                                "Strong"

                                if abs(value) >= 0.90

                                else "Moderate"

                            ),

                        "Direction":

                            (

                                "Positive"

                                if value > 0

                                else "Negative"

                            )

                    })

        report = pd.DataFrame(rows)

        if not report.empty:

            report = report.sort_values(

                "Correlation",

                key=np.abs,

                ascending=False

            ).reset_index(drop=True)

        logger.info(

            "%d strong relationships detected.",

            len(report)

        )

        return report

    # -----------------------------------------------------

    def generate(self):

        logger.info(
            "Generating correlation report..."
        )

        return {

            "Pearson":

                self.pearson(),

            "Spearman":

                self.spearman(),

            "Kendall":

                self.kendall(),

            "Strong Relationships":

                self.strongest_relationships()

        }


if __name__ == "__main__":

    print(
        "Import inside relationship_engine.py"
    )