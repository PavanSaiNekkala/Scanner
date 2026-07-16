"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/column_profiler.py

Production Grade Column Profiler

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from core.logger import get_logger

logger = get_logger(__name__)


class ColumnProfiler:
    """
    Creates a complete statistical profile
    for every column.
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

    # =====================================================
    # OUTLIERS
    # =====================================================

    @staticmethod
    def _iqr_outliers(series: pd.Series) -> int:

        series = series.dropna()

        if series.empty:

            return 0

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr

        upper = q3 + 1.5 * iqr

        return int(

            ((series < lower) | (series > upper)).sum()

        )

    # =====================================================
    # PROFILE
    # =====================================================

    def profile(self) -> pd.DataFrame:

        logger.info(

            "Generating column profiles..."

        )

        rows = []

        total_rows = len(self.df)

        for column in self.df.columns:

            s = self.df[column]

            is_numeric = (

                is_numeric_dtype(s)

                and

                not is_bool_dtype(s)

            )

            is_boolean = is_bool_dtype(s)

            is_datetime = is_datetime64_any_dtype(s)

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

                        s.isna().mean() * 100,

                        2

                    ),

                "Unique":

                    int(s.nunique(dropna=True)),

                "Duplicate":

                    int(

                        total_rows

                        -

                        s.nunique(dropna=True)

                    ),

                "Mode":

                    (

                        s.mode().iloc[0]

                        if not s.mode().empty

                        else np.nan

                    )

            }

            # ==============================================
            # NUMERIC
            # ==============================================

            if is_numeric:

                mean = s.mean()

                std = s.std()

                q1 = s.quantile(0.25)

                q3 = s.quantile(0.75)

                profile.update({

                    "Sum":

                        s.sum(),

                    "Mean":

                        mean,

                    "Median":

                        s.median(),

                    "Minimum":

                        s.min(),

                    "Maximum":

                        s.max(),

                    "Variance":

                        s.var(),

                    "Std Dev":

                        std,

                    "CV %":

                        (

                            std / mean * 100

                            if pd.notna(mean)

                            and mean != 0

                            else np.nan

                        ),

                    "Q1":

                        q1,

                    "Q3":

                        q3,

                    "IQR":

                        q3 - q1,

                    "5%":

                        s.quantile(0.05),

                    "95%":

                        s.quantile(0.95),

                    "Skewness":

                        s.skew(),

                    "Kurtosis":

                        s.kurt(),

                    "Positive":

                        int((s > 0).sum()),

                    "Negative":

                        int((s < 0).sum()),

                    "Zero":

                        int((s == 0).sum()),

                    "Outliers":

                        self._iqr_outliers(s)

                })

            # ==============================================
            # BOOLEAN
            # ==============================================

            elif is_boolean:

                profile.update({

                    "Sum":

                        int(s.sum()),

                    "Mean":

                        float(s.mean()),

                    "Median":

                        np.nan,

                    "Minimum":

                        bool(s.min()),

                    "Maximum":

                        bool(s.max()),

                    "Variance":

                        np.nan,

                    "Std Dev":

                        np.nan,

                    "CV %":

                        np.nan,

                    "Q1":

                        np.nan,

                    "Q3":

                        np.nan,

                    "IQR":

                        np.nan,

                    "5%":

                        np.nan,

                    "95%":

                        np.nan,

                    "Skewness":

                        np.nan,

                    "Kurtosis":

                        np.nan,

                    "Positive":

                        int(s.sum()),

                    "Negative":

                        0,

                    "Zero":

                        int((~s).sum()),

                    "Outliers":

                        0

                })

            # ==============================================
            # DATETIME
            # ==============================================

            elif is_datetime:

                profile.update({

                    "Sum": np.nan,

                    "Mean": np.nan,

                    "Median": np.nan,

                    "Minimum": s.min(),

                    "Maximum": s.max(),

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

            # ==============================================
            # OBJECT / TEXT
            # ==============================================

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

        "Import ColumnProfiler into profiler.py"

    )