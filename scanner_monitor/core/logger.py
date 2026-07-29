"""
core/logger.py
==============

Central logging utilities for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.config import (
    LOG_FILE,
    LOG_LEVEL,
)

# =============================================================================
# Log Format
# =============================================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# Formatter
# =============================================================================

formatter = logging.Formatter(

    fmt=LOG_FORMAT,

    datefmt=DATE_FORMAT,

)

# =============================================================================
# Console Handler
# =============================================================================

console_handler = logging.StreamHandler()

console_handler.setFormatter(

    formatter,

)

# =============================================================================
# File Handler
# =============================================================================

Path(LOG_FILE).parent.mkdir(

    parents=True,

    exist_ok=True,

)

file_handler = RotatingFileHandler(

    LOG_FILE,

    maxBytes=10 * 1024 * 1024,

    backupCount=5,

    encoding="utf-8",

)

file_handler.setFormatter(

    formatter,

)

# =============================================================================
# Logger Factory
# =============================================================================


def get_logger(

    name: str,

) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name:
        Logger name.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(

        name,

    )

    if logger.handlers:

        return logger

    logger.setLevel(

        LOG_LEVEL.upper(),

    )

    logger.addHandler(

        console_handler,

    )

    logger.addHandler(

        file_handler,

    )

    logger.propagate = False

    return logger

# =============================================================================
# Default Logger
# =============================================================================

logger = get_logger(

    "scanner_monitor",

)

# =============================================================================
# Convenience Functions
# =============================================================================


def debug(

    message: str,

) -> None:

    logger.debug(

        message,

    )


def info(

    message: str,

) -> None:

    logger.info(

        message,

    )


def warning(

    message: str,

) -> None:

    logger.warning(

        message,

    )


def error(

    message: str,

) -> None:

    logger.error(

        message,

    )


def critical(

    message: str,

) -> None:

    logger.critical(

        message,

    )


def exception(

    message: str,

) -> None:
    """
    Log an exception with traceback.
    """

    logger.exception(

        message,

    )