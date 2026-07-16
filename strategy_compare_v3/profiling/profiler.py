"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/profiler.py

Master Profiling Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from core.logger import get_logger

from profiling.dataset_summary import DatasetSummary
from profiling.column_profiler import ColumnProfiler
from profiling.descriptive_statistics import DescriptiveStatistics
from profiling.distribution_statistics import DistributionStatistics
from profiling.missing_value_profiler import MissingValueProfiler
from profiling.data_quality import DataQuality

logger = get_logger(__name__)


class Profiler:
    """
    Master profiling engine.

    Executes all profiling modules.

    Returns
    -------
    Dictionary of DataFrames.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()

        self.results: Dict[str, pd.DataFrame] = {}

    # --------------------------------------------------

    def run(self):

        logger.info("=" * 80)

        logger.info(
            "Starting Profiling Engine..."
        )

        # ----------------------------------------------

        dataset_summary = DatasetSummary(
            self.df
        ).generate()

        # ----------------------------------------------

        column_profile = ColumnProfiler(
            self.df
        ).profile()

        # ----------------------------------------------

        descriptive = DescriptiveStatistics(
            column_profile
        ).generate()

        # ----------------------------------------------

        distribution = DistributionStatistics(
            self.df
        ).generate()

        # ----------------------------------------------

        missing = MissingValueProfiler(
            self.df
        ).generate()

        # ----------------------------------------------

        quality = DataQuality(
            self.df
        ).generate()

        # ----------------------------------------------

        self.results = {

            "Dataset Summary":

                dataset_summary,

            "Column Profile":

                column_profile,

            "Descriptive Statistics":

                descriptive,

            "Distribution Statistics":

                distribution,

            "Missing Values":

                missing,

            "Data Quality":

                quality

        }

        logger.info(
            "Profiling completed successfully."
        )

        logger.info("=" * 80)

        return self.results

    # --------------------------------------------------

    def get_report(
        self,
        name: str
    ) -> pd.DataFrame:

        return self.results.get(name)

    # --------------------------------------------------

    def report_names(self):

        return list(
            self.results.keys()
        )


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "Use this module from main.py"
    )