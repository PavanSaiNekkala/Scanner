"""
logging.py
==========

Application logger.
"""

from __future__ import annotations

import logging
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
    

def get_logger(
    name: str,
    logfile: str = "streamlit_app.log",
) -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = ISTFormatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler = logging.FileHandler(
        Path("logs") / logfile,
        encoding="utf-8",
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
