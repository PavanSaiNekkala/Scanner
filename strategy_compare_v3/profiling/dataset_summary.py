"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/dataset_summary.py
Author : Pavan Sai

Dataset Summary Engine
============================================================
"""

from __future__ import annotations

import platform
from datetime import datetime

import numpy as np
import pandas as pd

from core.logger import get_logger
from core.utils import (
    dataframe_memory_mb,
    numeric_columns,
    categorical_columns,
    datetime_columns,
)

logger = get_logger(__name__)


class DatasetSummary:
    """
    Generates high-level dataset information.
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # ======================================================
    # SUMMARY
    # ======================================================

    def generate(self) -> pd.DataFrame:
        logger.info("Generating dataset summary...")

        rows, cols = self.df.shape

        summary = {
            "Generated On": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Platform": platform.system(),
            "Python Version": platform.python_version(),
            "Rows": rows,
            "Columns": cols,
            "Cells": rows * cols,
            "Numeric Columns": len(numeric_columns(self.df)),
            "Categorical Columns": len(categorical_columns(self.df)),
            "Datetime Columns": len(datetime_columns(self.df)),
            "Duplicate Rows": int(self.df.duplicated().sum()),
            "Duplicate Columns": int(self.df.columns.duplicated().sum()),
            "Missing Values": int(self.df.isna().sum().sum()),
            "Missing Percentage": round(
                (self.df.isna().sum().sum() / (rows * cols)) * 100, 2
            ),
            "Memory Usage (MB)": dataframe_memory_mb(self.df),
            "Numeric Cells": int(
                self.df.select_dtypes(include=np.number).count().sum()
            ),
            "Categorical Cells": int(
                self.df.select_dtypes(exclude=np.number).count().sum()
            ),
        }

        logger.info("Dataset summary completed.")

        return pd.DataFrame(summary.items(), columns=["Metric", "Value"])


if __name__ == "__main__":
    print("Import DatasetSummary inside profiler.py")
