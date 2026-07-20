"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/validator.py

Production-grade Dataset Validator

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from core.constants import SUPPORTED_FILE_TYPES
from core.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """
    Performs complete dataset validation.

    Supports

    ✓ Local files
    ✓ Streamlit UploadedFile
    ✓ DataFrame validation
    """

    def __init__(
        self,
        file_path: str | Path | None = None,
        dataframe: Optional[pd.DataFrame] = None,
    ):
        if file_path is None:
            self.file_path = None

        else:
            self.file_path = Path(file_path)

        self.df = dataframe

    # ======================================================
    # FILE VALIDATION
    # ======================================================

    def validate_file_exists(self) -> None:
        """
        Skip this check when dataframe comes
        from Streamlit UploadedFile.
        """

        if self.file_path is None:
            logger.info("Skipping file existence validation.")

            return

        if not self.file_path.exists():
            raise FileNotFoundError(f"{self.file_path} does not exist.")

        logger.info("File exists.")

    # ------------------------------------------------------

    def validate_extension(self) -> None:
        if self.file_path is None:
            logger.info("Skipping extension validation.")

            return

        extension = self.file_path.suffix.lower()

        if extension not in SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type: {extension}")

        logger.info("Supported file format.")

    # ------------------------------------------------------

    def validate_file_size(self) -> None:
        if self.file_path is None:
            logger.info("Skipping file size validation.")

            return

        if self.file_path.stat().st_size == 0:
            raise ValueError("Input file is empty.")

        logger.info("File size validation passed.")

    # ======================================================
    # DATAFRAME VALIDATION
    # ======================================================

    def validate_dataframe(self) -> None:
        if self.df is None:
            raise ValueError("DataFrame is None.")

        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        logger.info("DataFrame validation passed.")

    # ------------------------------------------------------

    def validate_duplicate_columns(self) -> None:
        duplicated = self.df.columns[self.df.columns.duplicated()]

        if len(duplicated):
            raise ValueError(f"Duplicate columns found: {duplicated.tolist()}")

        logger.info("Duplicate column validation passed.")

    # ------------------------------------------------------

    def validate_column_names(self) -> None:
        invalid = []

        for column in self.df.columns:
            if str(column).strip() == "":
                invalid.append(column)

        if invalid:
            raise ValueError("Unnamed columns detected.")

        logger.info("Column names validated.")

    # ------------------------------------------------------

    def validate_numeric_columns(self) -> None:
        numeric = self.df.select_dtypes(include="number")

        if numeric.empty:
            raise ValueError("No numeric columns detected.")

        logger.info("%d numeric columns detected.", numeric.shape[1])

    # ------------------------------------------------------

    def validate_required_columns(self, required_columns: Iterable[str]) -> None:
        missing = set(required_columns) - set(self.df.columns)

        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        logger.info("Required columns validated.")

    # ======================================================
    # QUALITY CHECKS
    # ======================================================

    def validate_null_columns(self) -> None:
        null_columns = [
            column for column in self.df.columns if self.df[column].isna().all()
        ]

        if null_columns:
            logger.warning("Entirely NULL columns: %s", null_columns)

    # ------------------------------------------------------

    def validate_constant_columns(self) -> None:
        constant = [
            column
            for column in self.df.columns
            if self.df[column].nunique(dropna=False) <= 1
        ]

        if constant:
            logger.warning("Constant columns: %s", constant)

    # ------------------------------------------------------

    def validate_duplicate_rows(self) -> None:
        duplicates = int(self.df.duplicated().sum())

        if duplicates:
            logger.warning("%d duplicate rows found.", duplicates)

        else:
            logger.info("No duplicate rows.")

    # ======================================================
    # COMPLETE VALIDATION
    # ======================================================

    def run(self, required_columns: Iterable[str] | None = None) -> None:
        logger.info("=" * 80)

        logger.info("Starting dataset validation...")

        self.validate_file_exists()

        self.validate_extension()

        self.validate_file_size()

        self.validate_dataframe()

        self.validate_column_names()

        self.validate_duplicate_columns()

        self.validate_duplicate_rows()

        self.validate_numeric_columns()

        self.validate_null_columns()

        self.validate_constant_columns()

        if required_columns:
            self.validate_required_columns(required_columns)

        logger.info("Validation completed successfully.")

        logger.info("=" * 80)


if __name__ == "__main__":
    print("Import DataValidator from loader.py")
