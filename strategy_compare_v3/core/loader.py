"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/loader.py
Author : Pavan Sai

Production-grade Data Loader
============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from core.constants import (
    MISSING_STRINGS,
)

from core.logger import get_logger

from core.utils import (
    clean_column_names,
    convert_numeric,
    dataframe_memory_mb,
)

from core.validator import DataValidator

logger = get_logger(__name__)


class DataLoader:
    """
    Institutional Data Loader.

    Responsibilities
    ----------------
    1. Load CSV / Excel
    2. Clean columns
    3. Convert datatypes
    4. Replace missing strings
    5. Validate dataset
    6. Generate metadata
    """

    def __init__(
        self,
        file_path: str | Path
    ):

        self.file_path = Path(file_path)

        self.df: Optional[pd.DataFrame] = None

        self.metadata = {}

    # ======================================================
    # PRIVATE LOADERS
    # ======================================================

    def _load_csv(self) -> pd.DataFrame:

        return pd.read_csv(
            self.file_path,
            low_memory=False
        )

    def _load_excel(self) -> pd.DataFrame:

        return pd.read_excel(
            self.file_path
        )

    # ======================================================
    # LOAD
    # ======================================================

    def load(self) -> pd.DataFrame:

        logger.info(
            "Loading dataset..."
        )

        extension = self.file_path.suffix.lower()

        if extension == ".csv":

            self.df = self._load_csv()

        elif extension in [".xlsx", ".xls"]:

            self.df = self._load_excel()

        else:

            raise ValueError(
                f"Unsupported format : {extension}"
            )

        logger.info(
            "Dataset loaded successfully."
        )

        return self.df

    # ======================================================
    # CLEANING
    # ======================================================

    def clean(self) -> pd.DataFrame:

        logger.info(
            "Cleaning dataset..."
        )

        self.df.replace(
            MISSING_STRINGS,
            np.nan,
            inplace=True
        )

        self.df = clean_column_names(
            self.df
        )

        self.df = convert_numeric(
            self.df
        )

        logger.info(
            "Cleaning completed."
        )

        return self.df

    # ======================================================
    # METADATA
    # ======================================================

    def generate_metadata(self):

        self.metadata = {

            "Rows":

                self.df.shape[0],

            "Columns":

                self.df.shape[1],

            "Numeric Columns":

                len(

                    self.df.select_dtypes(

                        include=np.number

                    ).columns

                ),

            "Categorical Columns":

                len(

                    self.df.select_dtypes(

                        exclude=np.number

                    ).columns

                ),

            "Memory (MB)":

                dataframe_memory_mb(

                    self.df

                ),

            "Duplicate Rows":

                int(

                    self.df.duplicated().sum()

                )

        }

        logger.info(
            "Metadata generated."
        )

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(self):

        validator = DataValidator(

            self.file_path,

            self.df

        )

        validator.run()

    # ======================================================
    # COMPLETE PIPELINE
    # ======================================================

    def run(self) -> pd.DataFrame:

        self.load()

        self.clean()

        self.validate()

        self.generate_metadata()

        logger.info(
            "Loader pipeline completed."
        )

        return self.df

    # ======================================================
    # ACCESSORS
    # ======================================================

    def get_dataframe(self):

        return self.df

    def get_metadata(self):

        return self.metadata


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    FILE = "data/input/sample.csv"

    loader = DataLoader(FILE)

    df = loader.run()

    print(df.head())

    print()

    print(loader.get_metadata())