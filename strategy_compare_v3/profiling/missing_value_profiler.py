"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/missing_value_profiler.py

Missing Value Analysis Engine

============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class MissingValueProfiler:
    """
    Analyze missing values for each column.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()

    # ------------------------------------------------------

    def generate(self) -> pd.DataFrame:

        logger.info(
            "Generating missing value profile..."
        )

        rows = []

        total_rows = len(self.df)

        for column in self.df.columns:

            series = self.df[column]

            missing = int(
                series.isna().sum()
            )

            available = total_rows - missing

            percent = round(
                (missing / total_rows) * 100,
                2
            )

            if percent == 0:

                severity = "Excellent"

            elif percent <= 5:

                severity = "Low"

            elif percent <= 15:

                severity = "Moderate"

            elif percent <= 30:

                severity = "High"

            else:

                severity = "Critical"

            rows.append({

                "Column":

                    column,

                "Rows":

                    total_rows,

                "Available":

                    available,

                "Missing":

                    missing,

                "Missing %":

                    percent,

                "Completeness %":

                    round(
                        100 - percent,
                        2
                    ),

                "Severity":

                    severity

            })

        report = pd.DataFrame(rows)

        logger.info(
            "Missing value profile completed."
        )

        return report

    # ------------------------------------------------------

    def summary(self):

        total_cells = self.df.size

        missing_cells = int(
            self.df.isna().sum().sum()
        )

        complete_cells = total_cells - missing_cells

        return {

            "Total Cells":

                total_cells,

            "Missing Cells":

                missing_cells,

            "Complete Cells":

                complete_cells,

            "Dataset Completeness %":

                round(
                    complete_cells
                    /
                    total_cells
                    * 100,
                    2
                )

        }


if __name__ == "__main__":

    print(
        "Import inside profiler.py"
    )