"""
============================================================
Institutional Strategy Comparison Engine V3
File : normalization/minmax.py

Min-Max Normalization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler

from core.logger import get_logger

logger = get_logger(__name__)


class MinMaxNormalization:
    """
    Normalize numeric features to [0, 1].

    Formula
    -------
    X' = (X - Min) / (Max - Min)
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

        self.numeric = self.df.select_dtypes(include=np.number).columns

        self.scaler = MinMaxScaler()

    # --------------------------------------------------

    def generate(self):
        logger.info("Running Min-Max Normalization...")

        normalized = self.df.copy()

        if len(self.numeric) == 0:
            logger.warning("No numeric columns found.")

            return normalized

        normalized[self.numeric] = self.scaler.fit_transform(normalized[self.numeric])

        logger.info("Min-Max normalization completed.")

        return normalized

    # --------------------------------------------------

    def scaler_parameters(self):
        if not hasattr(self.scaler, "data_min_"):
            raise RuntimeError("Run generate() before requesting parameters.")

        return pd.DataFrame(
            {
                "Feature": self.numeric,
                "Minimum": self.scaler.data_min_,
                "Maximum": self.scaler.data_max_,
            }
        )


if __name__ == "__main__":
    print("Import inside normalization_engine.py")
