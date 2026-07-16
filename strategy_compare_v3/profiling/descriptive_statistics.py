"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/descriptive_statistics.py

Descriptive Statistics Engine

Consumes the output of ColumnProfiler.
============================================================
"""

from __future__ import annotations

import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class DescriptiveStatistics:

    """
    Creates descriptive statistics report from the
    master column profile.
    """

    COLUMNS = [

        "Column",

        "Rows",

        "Missing",

        "Missing %",

        "Unique",

        "Duplicate",

        "Data Type",

        "Sum",

        "Mean",

        "Median",

        "Minimum",

        "Maximum",

        "Variance",

        "Std Dev",

        "CV %",

        "Q1",

        "Q3",

        "IQR",

        "5%",

        "95%"

    ]

    def __init__(
        self,
        column_profile: pd.DataFrame
    ):

        self.column_profile = column_profile.copy()

    # ------------------------------------------------------

    def generate(self) -> pd.DataFrame:

        logger.info(
            "Generating descriptive statistics..."
        )

        missing = [

            c for c in self.COLUMNS

            if c not in self.column_profile.columns

        ]

        if missing:

            raise ValueError(

                "Missing required columns: "

                + ", ".join(missing)

            )

        report = (

            self.column_profile

            [self.COLUMNS]

            .copy()

        )

        logger.info(

            "Descriptive statistics generated."

        )

        return report


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(

        "Import inside profiler.py"

    )