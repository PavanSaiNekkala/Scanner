"""
============================================================
Institutional Strategy Comparison Engine V3

File : batch_processing/result_collector.py

Result Collector Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import pandas as pd

from typing import List


from core.logger import get_logger

logger = get_logger(__name__)


class ResultCollector:
    """
    Collects processed strategy results.


    Responsibilities
    ----------------

    ✓ Combine strategy outputs

    ✓ Remove duplicate records

    ✓ Validate final dataset

    ✓ Generate comparison dataframe


    """

    def __init__(self):
        self.results: List[pd.DataFrame] = []

    # ==================================================
    # ADD RESULT
    # ==================================================

    def add(self, dataframe: pd.DataFrame):
        if dataframe is None:
            return

        if dataframe.empty:
            return

        self.results.append(dataframe.copy())

        logger.info("Result added. Rows: %d", len(dataframe))

    # ==================================================
    # COMBINE
    # ==================================================

    def combine(self):
        logger.info("Combining strategy results...")

        if not self.results:
            return pd.DataFrame()

        combined = pd.concat(self.results, ignore_index=True)

        logger.info("Combined rows: %d", len(combined))

        return combined

    # ==================================================
    # REMOVE DUPLICATES
    # ==================================================

    def remove_duplicates(self, dataframe):
        required = ["Strategy", "Stock"]

        available = [c for c in required if c in dataframe.columns]

        if available:
            dataframe = dataframe.drop_duplicates(subset=available, keep="last")

        return dataframe

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate(self, dataframe):
        required = ["Strategy", "Stock", "Composite Score"]

        missing = [c for c in required if c not in dataframe.columns]

        if missing:
            raise ValueError(f"Missing result fields: {missing}")

        return True

    # ==================================================
    # FINAL DATASET
    # ==================================================

    def generate(self):
        dataframe = self.combine()

        dataframe = self.remove_duplicates(dataframe)

        self.validate(dataframe)

        logger.info("Final comparison dataset generated.")

        return dataframe


if __name__ == "__main__":
    print("Import ResultCollector")
