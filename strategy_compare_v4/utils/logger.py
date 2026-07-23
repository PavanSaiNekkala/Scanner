"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
utils/logger.py

Purpose
-------
Centralized logging utilities.

=============================================================
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from datetime import datetime
import pytz

class ISTFormatter(logging.Formatter):

    def converter(
        self,
        timestamp,
    ):
        return datetime.fromtimestamp(
            timestamp,
            tz=pytz.timezone(
                "Asia/Kolkata"
            ),
        ).timetuple()

# ============================================================
# Logger Configuration
# ============================================================

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_LEVEL = logging.INFO

MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB

BACKUP_COUNT = 5


# ============================================================
# Logger Factory
# ============================================================


def get_logger(
    name: str,
    log_file: str | Path | None = None,
    level: int = DEFAULT_LEVEL,
) -> logging.Logger:
    """
    Create or retrieve a configured logger.
    """

    logger = logging.getLogger(
        name,
    )

    if logger.handlers:
        return logger

    logger.setLevel(
        level,
    )

    logger.propagate = False

    formatter = ISTFormatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    # --------------------------------------------------------
    # Console Handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        level,
    )

    console_handler.setFormatter(
        formatter,
    )

    logger.addHandler(
        console_handler,
    )

    # --------------------------------------------------------
    # Rotating File Handler
    # --------------------------------------------------------

    if log_file is not None:
        log_file = Path(
            log_file,
        )

        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )

        file_handler.setLevel(
            level,
        )

        file_handler.setFormatter(
            formatter,
        )

        logger.addHandler(
            file_handler,
        )

    return logger


# ============================================================
# Banner
# ============================================================


def banner(
    logger: logging.Logger,
    title: str,
    width: int = 70,
) -> None:
    """
    Print a section banner.
    """

    line = "=" * width

    logger.info(line)

    logger.info(
        title.center(width),
    )

    logger.info(line)


# ============================================================
# Divider
# ============================================================


def divider(
    logger: logging.Logger,
    width: int = 70,
    character: str = "-",
) -> None:
    """
    Log a divider line.
    """

    logger.info(
        character * width,
    )


# ============================================================
# Execution Timer
# ============================================================


def log_execution_time(
    logger: logging.Logger,
    seconds: float,
    task: str | None = None,
) -> None:
    """
    Log execution time.
    """

    if task:
        logger.info(
            "%s completed in %.3f seconds.",
            task,
            seconds,
        )

    else:
        logger.info(
            "Execution completed in %.3f seconds.",
            seconds,
        )


# ============================================================
# DataFrame Summary
# ============================================================


def log_dataframe_summary(
    logger: logging.Logger,
    dataframe,
    name: str = "DataFrame",
) -> None:
    """
    Log a concise DataFrame summary.
    """

    try:
        import pandas as pd

        if dataframe is None:
            logger.warning(
                "%s is None.",
                name,
            )

            return

        if not isinstance(
            dataframe,
            pd.DataFrame,
        ):
            logger.warning(
                "%s is not a pandas DataFrame.",
                name,
            )

            return

        logger.info(
            "%s Summary",
            name,
        )

        logger.info(
            "Rows             : %d",
            len(dataframe),
        )

        logger.info(
            "Columns          : %d",
            len(dataframe.columns),
        )

        logger.info(
            "Missing Values   : %d",
            int(dataframe.isna().sum().sum()),
        )

        logger.info(
            "Duplicate Rows   : %d",
            int(dataframe.duplicated().sum()),
        )

    except Exception:
        logger.exception("Unable to log DataFrame summary.")


# ============================================================
# Stage Logger
# ============================================================


def log_stage(
    logger: logging.Logger,
    stage: str,
) -> None:
    """
    Log a pipeline stage banner.
    """

    banner(
        logger,
        stage,
    )


# ============================================================
# Exception Logger
# ============================================================


def log_exception(
    logger: logging.Logger,
    message: str,
) -> None:
    """
    Log an exception with traceback.
    """

    logger.exception(
        message,
    )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "get_logger",
    "banner",
    "divider",
    "log_execution_time",
    "log_dataframe_summary",
    "log_stage",
    "log_exception",
]
