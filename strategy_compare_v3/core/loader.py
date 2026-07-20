"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/loader.py

Production-grade Data Loader

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, BinaryIO

import numpy as np
import pandas as pd

from core.constants import MISSING_STRINGS

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
    ✓ CSV / Excel Loading
    ✓ Streamlit UploadedFile Support
    ✓ Missing Value Cleaning
    ✓ Column Standardization
    ✓ Numeric Conversion
    ✓ Empty Column Removal
    ✓ Constant Column Removal
    ✓ Validation
    ✓ Metadata Generation
    """

    def __init__(
        self,
        source: str | Path | BinaryIO,
    ):
        self.source = source

        self.file_path: Optional[Path] = None

        self.filename = "uploaded_file"

        if isinstance(source, (str, Path)):
            self.file_path = Path(source)

            self.filename = self.file_path.name

        else:
            self.filename = getattr(source, "name", "uploaded_file")

        self.df: Optional[pd.DataFrame] = None

        self.original_columns = []

        self.removed_columns = []

        self.metadata = {}

    # ======================================================
    # LOADERS
    # ======================================================

    def _load_csv(self):
        return pd.read_csv(self.source, low_memory=False)

    def _load_excel(self):
        return pd.read_excel(self.source)

    # ======================================================
    # LOAD
    # ======================================================

    def load(self):
        logger.info("Loading dataset...")

        extension = Path(self.filename).suffix.lower()

        if extension == ".csv":
            self.df = self._load_csv()

        elif extension in (".xlsx", ".xls"):
            self.df = self._load_excel()

        else:
            raise ValueError(f"Unsupported file format: {extension}")

        self.original_columns = self.df.columns.tolist()

        logger.info("Dataset loaded successfully.")

        return self.df

    # ======================================================
    # CLEANING
    # ======================================================

    def clean(self):
        logger.info("Cleaning dataset...")

        # Replace missing strings

        self.df.replace(MISSING_STRINGS, np.nan, inplace=True)

        # Standardize columns

        self.df = clean_column_names(self.df)

        # Convert numeric values

        self.df = convert_numeric(self.df)

        logger.info("FINAL CLEANED COLUMNS: %s", self.df.columns.tolist())

        # Remove empty columns

        self.remove_empty_columns()

        # Remove constant columns

        self.remove_constant_columns()

        logger.info("Cleaning completed.")

        return self.df

    # ======================================================
    # REMOVE EMPTY COLUMNS
    # ======================================================

    def remove_empty_columns(self):
        empty_columns = [
            column for column in self.df.columns if self.df[column].isna().all()
        ]

        if empty_columns:
            self.df.drop(columns=empty_columns, inplace=True)

            self.removed_columns.extend(empty_columns)

            logger.warning("Removed empty columns: %s", empty_columns)

    # ======================================================
    # REMOVE CONSTANT COLUMNS
    # ======================================================

    def remove_constant_columns(self):
        constant_columns = [
            column
            for column in self.df.columns
            if self.df[column].nunique(dropna=False) <= 1
        ]

        if constant_columns:
            self.df.drop(columns=constant_columns, inplace=True)

            self.removed_columns.extend(constant_columns)

            logger.warning("Removed constant columns: %s", constant_columns)

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(self):
        logger.info("Running validation...")

        validator = DataValidator(self.file_path, self.df)

        validator.run()

    # ======================================================
    # METADATA
    # ======================================================

    def generate_metadata(self):
        numeric_columns = self.df.select_dtypes(include=np.number).columns

        categorical_columns = self.df.select_dtypes(exclude=np.number).columns

        self.metadata = {
            "Filename": self.filename,
            "Rows": int(self.df.shape[0]),
            "Columns": int(self.df.shape[1]),
            "Numeric Columns": len(numeric_columns),
            "Categorical Columns": len(categorical_columns),
            "Duplicate Rows": int(self.df.duplicated().sum()),
            "Memory MB": round(dataframe_memory_mb(self.df), 2),
            "Removed Columns": self.removed_columns,
        }

        logger.info("Metadata generated.")

    # ======================================================
    # COMPLETE PIPELINE
    # ======================================================

    def run(self):
        self.load()

        self.clean()

        self.validate()

        self.generate_metadata()

        logger.info("Loader pipeline completed.")

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
    loader = DataLoader("data/input/sample.csv")

    df = loader.run()

    print(df.head())

    print()

    print(loader.get_metadata())
