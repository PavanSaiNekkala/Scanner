"""
============================================================
Institutional Strategy Comparison Engine V3
File : normalization/normalization_engine.py

Master Normalization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time
from typing import Dict, Any

import pandas as pd

from core.logger import get_logger
from core.cache import CacheManager

from normalization.minmax import MinMaxNormalization
from normalization.zscore import ZScoreNormalization
from normalization.robust_zscore import RobustZScoreNormalization
from normalization.percentile import PercentileNormalization
from normalization.quantile import QuantileNormalization

logger = get_logger(__name__)


class NormalizationEngine:
    """
    Master Normalization Engine.

    Executes all normalization techniques.

    Methods
    -------
    - Min-Max
    - Z-Score
    - Robust Z-Score
    - Percentile
    - Quantile

    Returns
    -------
    Dictionary of normalized DataFrames.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        use_cache: bool = False
    ):

        self.df = dataframe.copy()

        self.use_cache = use_cache

        self.cache = CacheManager()

        self.results: Dict[str, Any] = {}

    # -----------------------------------------------------

    def validate(self):

        if self.df.empty:

            raise ValueError(
                "Input dataframe is empty."
            )

        numeric = self.df.select_dtypes(
            include="number"
        )

        if numeric.empty:

            raise ValueError(
                "No numeric columns found."
            )

    # -----------------------------------------------------

    def run(self):

        logger.info("=" * 80)

        logger.info(
            "Starting Normalization Engine..."
        )

        self.validate()

        start = time.perf_counter()

        # -------------------------------------------------
        # Min-Max
        # -------------------------------------------------

        minmax = MinMaxNormalization(
            self.df
        ).generate()

        # -------------------------------------------------
        # Z-Score
        # -------------------------------------------------

        zscore = ZScoreNormalization(
            self.df
        ).generate()

        # -------------------------------------------------
        # Robust Z-Score
        # -------------------------------------------------

        robust = RobustZScoreNormalization(
            self.df
        ).generate()

        # -------------------------------------------------
        # Percentile
        # -------------------------------------------------

        percentile = PercentileNormalization(
            self.df
        ).generate()

        # -------------------------------------------------
        # Quantile
        # -------------------------------------------------

        quantile_uniform = QuantileNormalization(
            self.df,
            output_distribution="uniform"
        ).generate()

        quantile_normal = QuantileNormalization(
            self.df,
            output_distribution="normal"
        ).generate()

        # -------------------------------------------------

        elapsed = round(

            time.perf_counter() - start,

            3

        )

        self.results = {

            "Min-Max":

                minmax,

            "Z-Score":

                zscore,

            "Robust Z-Score":

                robust,

            "Percentile":

                percentile,

            "Quantile (Uniform)":

                quantile_uniform,

            "Quantile (Normal)":

                quantile_normal,

            "Execution Time (sec)":

                elapsed

        }

        logger.info(

            "Normalization completed in %.3f seconds.",

            elapsed

        )

        logger.info("=" * 80)

        return self.results

    # -----------------------------------------------------

    def get_result(
        self,
        method: str
    ):

        return self.results.get(method)

    # -----------------------------------------------------

    def methods(self):

        return [

            key

            for key in self.results.keys()

            if key != "Execution Time (sec)"

        ]

    # -----------------------------------------------------

    def summary(self):

        return {

            "Methods":

                self.methods(),

            "Execution Time":

                self.results.get(

                    "Execution Time (sec)"

                ),

            "Total Methods":

                len(

                    self.methods()

                )

        }


if __name__ == "__main__":

    print(

        "Import inside main.py"

    )