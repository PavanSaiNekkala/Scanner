"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/logger.py
Author : Pavan Sai

Centralized logging configuration.
============================================================
"""

from __future__ import annotations

import logging
import sys

from core.constants import (
    LOG_DIR,
    LOG_FORMAT,
    LOG_LEVEL,
)

# ----------------------------------------------------------
# Create log directory
# ----------------------------------------------------------

LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "strategy_compare.log"


# ----------------------------------------------------------
# Configure Logger
# ----------------------------------------------------------


def get_logger(name: str = "StrategyCompare") -> logging.Logger:
    """
    Returns a configured logger.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    formatter = logging.Formatter(LOG_FORMAT)

    # ------------------------------------------------------
    # Console Logger
    # ------------------------------------------------------

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(formatter)

    # ------------------------------------------------------
    # File Logger
    # ------------------------------------------------------

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")

    file_handler.setFormatter(formatter)

    # ------------------------------------------------------

    logger.addHandler(console_handler)

    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


# ----------------------------------------------------------
# Default Logger
# ----------------------------------------------------------

logger = get_logger()


# ----------------------------------------------------------
# Test
# ----------------------------------------------------------

if __name__ == "__main__":
    logger.info("Logger initialized successfully.")

    logger.warning("Warning message.")

    logger.error("Error message.")

    logger.debug("Debug message.")
