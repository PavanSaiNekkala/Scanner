"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
utils/logger.py

Purpose
-------
Centralized logging utilities used throughout the
Institutional Strategy Comparison Platform.

Provides
--------
• Configured application logger
• Console logging
• Optional file logging
• Section banners

=============================================================
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

# ============================================================
# Logger Configuration
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_LEVEL = logging.INFO


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

    Parameters
    ----------
    name : str
        Logger name.

    log_file : str | Path | None
        Optional log file.

    level : int
        Logging level.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    # --------------------------------------------------------
    # Console Handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setLevel(level)

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # --------------------------------------------------------
    # File Handler (Optional)
    # --------------------------------------------------------

    if log_file is not None:

        log_file = Path(log_file)

        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )

        file_handler.setLevel(level)

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

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
    Log a section banner.

    Example
    -------
    ======================================================
                    DERIVED METRICS
    ======================================================
    """

    line = "=" * width

    logger.info(line)

    logger.info(title.center(width))

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

    logger.info(character * width)


# ============================================================
# Execution Timer
# ============================================================

def log_execution_time(
    logger: logging.Logger,
    seconds: float,
    task: Optional[str] = None,
) -> None:
    """
    Log execution time.
    """

    if task:

        logger.info(
            "%s completed in %.2f seconds",
            task,
            seconds,
        )

    else:

        logger.info(
            "Execution completed in %.2f seconds",
            seconds,
        )