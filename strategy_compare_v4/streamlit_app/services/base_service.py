"""
base_service.py
===============

Base service class shared by all services.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from utils.exceptions import (
    EmptyDataFrameError,
)
from utils.logging import get_logger
from utils.validators import (
    validate_columns,
    validate_dataframe,
)


class BaseService:
    """
    Base class for all services.
    """

    def __init__(self, name: str):
        self.logger = get_logger(name)

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def check_dataframe(
        self,
        df: pd.DataFrame,
    ):
        try:
            validate_dataframe(df)

        except ValueError as e:
            raise EmptyDataFrameError(str(e)) from e

    def check_columns(
        self,
        df: pd.DataFrame,
        required: list[str],
    ):
        try:
            validate_columns(
                df,
                required,
            )

        except ValueError as e:
            raise EmptyDataFrameError(str(e)) from e

    # --------------------------------------------------
    # File
    # --------------------------------------------------

    def exists(
        self,
        path,
    ) -> bool:
        return Path(path).exists()

    def ensure_directory(
        self,
        path,
    ):
        Path(path).mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    def dataframe_info(
        self,
        df: pd.DataFrame,
    ) -> dict:
        return {
            "Rows": len(df),
            "Columns": len(df.columns),
            "Memory (KB)": round(
                df.memory_usage(deep=True).sum() / 1024,
                2,
            ),
        }
