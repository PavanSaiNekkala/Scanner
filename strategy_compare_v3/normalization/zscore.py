"""
============================================================
Institutional Strategy Comparison Engine V3
File : normalization/zscore.py

Z-Score Normalization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

from core.logger import get_logger

logger = get_logger(__name__)


class ZScoreNormalization:
    """
    Standard Z-Score Normalization.

    Formula
    -------
    Z = (X - Mean) / Standard Deviation
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()

        self.numeric_columns = self.df.select_dtypes(
            include=np.number
        ).columns

        self.scaler = StandardScaler()

    # --------------------------------------------------

    def generate(self):

        logger.info(
            "Running Z-Score Normalization..."
        )

        normalized = self.df.copy()

        if len(self.numeric_columns) == 0:

            logger.warning(
                "No numeric columns found."
            )

            return normalized

        normalized[self.numeric_columns] = (

            self.scaler.fit_transform(

                normalized[self.numeric_columns]

            )

        )

        logger.info(
            "Z-Score normalization completed."
        )

        return normalized

    # --------------------------------------------------

    def statistics(self):

        if not hasattr(

            self.scaler,

            "mean_"

        ):

            raise RuntimeError(

                "Run generate() first."

            )

        return pd.DataFrame({

            "Feature":

                self.numeric_columns,

            "Mean":

                self.scaler.mean_,

            "Standard Deviation":

                np.sqrt(

                    self.scaler.var_

                )

        })

    # --------------------------------------------------

    def summary(self):

        return {

            "Method":

                "Z-Score",

            "Features":

                len(

                    self.numeric_columns

                )

        }


if __name__ == "__main__":

    print(

        "Import inside normalization_engine.py"

    )