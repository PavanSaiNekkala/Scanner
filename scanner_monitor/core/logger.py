"""
scanner_monitor.core.logger
===========================

Central logging utilities for the Institutional Scanner Monitor.

This module provides a consistent logging configuration across the
application using both console and rotating file handlers.

Features
--------
- Rotating file logging
- Console logging
- Singleton logger instances
- Thread-safe logger creation
- Convenience logging functions
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

from core.config import (
    LOG_FILE,
    LOG_LEVEL,
)

__all__ = [
    "get_logger",
    "logger",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
]

# =============================================================================
# Logging Configuration
# =============================================================================

LOG_FORMAT: Final[str] = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)

DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

MAX_LOG_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MB

BACKUP_COUNT: Final[int] = 5

# =============================================================================
# Formatter
# =============================================================================

_FORMATTER = logging.Formatter(
    fmt=LOG_FORMAT,
    datefmt=DATE_FORMAT,
)

# =============================================================================
# Handler Factory
# =============================================================================


def _create_console_handler() -> logging.StreamHandler:
    """
    Create a configured console handler.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(_FORMATTER)

    return handler


def _create_file_handler() -> RotatingFileHandler:
    """
    Create a configured rotating file handler.
    """

    Path(LOG_FILE).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )

    handler.setFormatter(_FORMATTER)

    return handler


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
    name
        Logger name.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL.upper())
    logger.propagate = False

    logger.addHandler(
        _create_console_handler(),
    )

    logger.addHandler(
        _create_file_handler(),
    )

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
    *args: object,
    **kwargs: object,
) -> None:
    """
    Log a DEBUG message.
    """

    logger.debug(
        message,
        *args,
        **kwargs,
    )


def info(
    message: str,
    *args: object,
    **kwargs: object,
) -> None:
    """
    Log an INFO message.
    """

    logger.info(
        message,
        *args,
        **kwargs,
    )


def warning(
    message: str,
    *args: object,
    **kwargs: object,
) -> None:
    """
    Log a WARNING message.
    """

    logger.warning(
        message,
        *args,
        **kwargs,
    )


def error(
    message: str,
    *args: object,
    **kwargs: object,
) -> None:
    """
    Log an ERROR message.
    """

    logger.error(
        message,
        *args,
        **kwargs,
    )


def critical(
    message: str,
    *args: object,
    **kwargs: object,
) -> None:
    """
    Log a CRITICAL message.
    """

    logger.critical(
        message,
        *args,
        **kwargs,
    )


def exception(
    message: str,
    *args: object,
    **kwargs: object,
) -> None:
    """
    Log an exception together with its traceback.
    """

    logger.exception(
        message,
        *args,
        **kwargs,
    )