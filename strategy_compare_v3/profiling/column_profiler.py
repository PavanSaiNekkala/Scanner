"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/column_profiler.py

Master Column Profiling Engine

Every other profiling module uses this output.

============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class ColumnProfiler:

    """
    Creates one complete profile for every column.
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

    # -----------------------------------------------------

    @staticmethod
    def _iqr_outliers(series: pd.Series):

        series = series.dropna()

        if series.empty:
            return 0

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr

        upper = q3 + 1.5 * iqr

        return int(
            ((series < lower) |
             (series > upper)).sum()
        )

    # -----------------------------------------------------

    def profile(self):

        logger.info(
            "Generating column profiles..."
        )

        rows = []

        total_rows = len(self.df)

        for column in self.df.columns:

            s = self.df[column]

            numeric = pd.api.types.is_numeric_dtype(s)

            profile = {

                "Column":

                    column,

                "Data Type":

                    str(s.dtype),

                "Rows":

                    total_rows,

                "Missing":

                    int(s.isna().sum()),

                "Missing %":

                    round(
                        s.isna().mean()*100,
                        2
                    ),

                "Unique":

                    int(s.nunique()),

                "Duplicate":

                    int(
                        total_rows -
                        s.nunique()
                    ),

                "Mode":

                    (
                        s.mode().iloc[0]
                        if not s.mode().empty
                        else np.nan
                    ),

            }

            if numeric:

                profile.update({

                    "Sum":

                        s.sum(),

                    "Mean":

                        s.mean(),

                    "Median":

                        s.median(),

                    "Minimum":

                        s.min(),

                    "Maximum":

                        s.max(),

                    "Variance":

                        s.var(),

                    "Std Dev":

                        s.std(),

                    "CV %":

                        (
                            s.std()/s.mean()*100
                            if s.mean()!=0
                            else np.nan
                        ),

                    "Q1":

                        s.quantile(.25),

                    "Q3":

                        s.quantile(.75),

                    "IQR":

                        s.quantile(.75)
                        -
                        s.quantile(.25),

                    "5%":

                        s.quantile(.05),

                    "95%":

                        s.quantile(.95),

                    "Skewness":

                        s.skew(),

                    "Kurtosis":

                        s.kurt(),

                    "Positive":

                        int((s>0).sum()),

                    "Negative":

                        int((s<0).sum()),

                    "Zero":

                        int((s==0).sum()),

                    "Outliers":

                        self._iqr_outliers(s)

                })

            else:

                profile.update({

                    "Sum": np.nan,

                    "Mean": np.nan,

                    "Median": np.nan,

                    "Minimum": np.nan,

                    "Maximum": np.nan,

                    "Variance": np.nan,

                    "Std Dev": np.nan,

                    "CV %": np.nan,

                    "Q1": np.nan,

                    "Q3": np.nan,

                    "IQR": np.nan,

                    "5%": np.nan,

                    "95%": np.nan,

                    "Skewness": np.nan,

                    "Kurtosis": np.nan,

                    "Positive": np.nan,

                    "Negative": np.nan,

                    "Zero": np.nan,

                    "Outliers": np.nan

                })

            rows.append(profile)

        logger.info(
            "Column profiling completed."
        )

        return pd.DataFrame(rows)


if __name__ == "__main__":

    print(
        "Import this class in profiler.py"
    )