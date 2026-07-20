"""
============================================================
Institutional Strategy Comparison Engine V3

File : batch_processing/strategy_detector.py

Strategy Metadata Detector

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


from pathlib import Path

from typing import Dict, Any


from core.logger import get_logger

logger = get_logger(__name__)


class StrategyDetector:
    """
    Detects strategy metadata from
    backtest file structure.


    Responsibilities
    ----------------

    ✓ Identify strategy name
    ✓ Identify stock name
    ✓ Detect strategy version
    ✓ Detect timeframe
    ✓ Capture folder metadata

    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    # ==================================================
    # STRATEGY NAME
    # ==================================================

    def strategy_name(self) -> str:
        """
        Expected:

        backtest/
            Strategy_A/
                RELIANCE.csv


        returns:

        Strategy_A

        """

        return self.file_path.parent.name

    # ==================================================
    # STOCK NAME
    # ==================================================

    def stock_name(self) -> str:
        return self.file_path.stem

    # ==================================================
    # STRATEGY VERSION
    # ==================================================

    def strategy_version(self):
        name = self.strategy_name()

        for keyword in ["v1", "v2", "v3", "v4", "v5"]:
            if keyword.lower() in name.lower():
                return keyword.upper()

        return "DEFAULT"

    # ==================================================
    # TIMEFRAME DETECTION
    # ==================================================

    def timeframe(self):
        name = self.file_path.name.lower()

        if "daily" in name:
            return "Daily"

        if "weekly" in name:
            return "Weekly"

        if "monthly" in name:
            return "Monthly"

        return "Unknown"

    # ==================================================
    # METADATA
    # ==================================================

    def metadata(self) -> Dict[str, Any]:
        return {
            "Strategy": self.strategy_name(),
            "Stock": self.stock_name(),
            "Strategy Version": self.strategy_version(),
            "Timeframe": self.timeframe(),
            "File": self.file_path.name,
        }


if __name__ == "__main__":
    detector = StrategyDetector("data/input/backtest/Strategy_A/RELIANCE.csv")

    print(detector.metadata())
