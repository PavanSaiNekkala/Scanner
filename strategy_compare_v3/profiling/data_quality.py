"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/data_quality.py

Institutional Data Quality Engine

============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class DataQuality:

    """
    Comprehensive data quality assessment.
    """

    def __init__(self,
                 dataframe: pd.DataFrame):

        self.df = dataframe.copy()

    # -----------------------------------------------------

    def missing_analysis(self):

        total_cells = self.df.size

        missing_cells = int(
            self.df.isna().sum().sum()
        )

        missing_pct = (
            missing_cells /
            total_cells
        ) * 100

        return {

            "Missing Cells":
                missing_cells,

            "Missing %":
                round(
                    missing_pct,
                    2
                )

        }

    # -----------------------------------------------------

    def duplicate_analysis(self):

        return {

            "Duplicate Rows":

                int(
                    self.df.duplicated().sum()
                ),

            "Duplicate Columns":

                int(
                    self.df.columns.duplicated().sum()
                )

        }

    # -----------------------------------------------------

    def constant_columns(self):

        constant = []

        for c in self.df.columns:

            if self.df[c].nunique(
                dropna=False
            ) <= 1:

                constant.append(c)

        return constant

    # -----------------------------------------------------

    def infinite_values(self):

        numeric = self.df.select_dtypes(
            include=np.number
        )

        return int(

            np.isinf(
                numeric
            ).sum().sum()

        )

    # -----------------------------------------------------

    def outliers(self):

        report = {}

        numeric = self.df.select_dtypes(
            include=np.number
        )

        for col in numeric.columns:

            s = numeric[col].dropna()

            if len(s) == 0:

                report[col] = 0

                continue

            q1 = s.quantile(.25)

            q3 = s.quantile(.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr

            upper = q3 + 1.5 * iqr

            report[col] = int(

                ((s < lower) |
                 (s > upper)).sum()

            )

        return report

    # -----------------------------------------------------

    def quality_score(self):

        score = 100.0

        missing = self.missing_analysis()

        duplicates = self.duplicate_analysis()

        constants = len(
            self.constant_columns()
        )

        infs = self.infinite_values()

        outliers = sum(

            self.outliers().values()

        )

        score -= min(

            missing["Missing %"] * 0.5,

            30

        )

        score -= min(

            duplicates["Duplicate Rows"] * 0.05,

            20

        )

        score -= min(

            constants * 2,

            15

        )

        score -= min(

            infs,

            15

        )

        score -= min(

            outliers * 0.01,

            20

        )

        return round(

            max(score, 0),

            2

        )

    # -----------------------------------------------------

    def generate(self):

        logger.info(

            "Generating data quality report..."

        )

        report = {

            **self.missing_analysis(),

            **self.duplicate_analysis(),

            "Constant Columns":

                len(

                    self.constant_columns()

                ),

            "Infinite Values":

                self.infinite_values(),

            "Total Outliers":

                sum(

                    self.outliers().values()

                ),

            "Quality Score":

                self.quality_score()

        }

        logger.info(

            "Data quality completed."

        )

        return pd.DataFrame(

            report.items(),

            columns=[

                "Metric",

                "Value"

            ]

        )


if __name__ == "__main__":

    print(

        "Import inside profiler.py"

    )