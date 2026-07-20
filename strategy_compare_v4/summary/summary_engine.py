"""
==============================================================
Institutional Strategy Comparison Platform V4
Summary Engine
==============================================================

Pipeline

Trade CSVs
    ↓
Summary Builder
    ↓
strategy_summary.csv
    ↓
Derived Metrics Engine

==============================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .aggregations import (
    build_strategy_summary,
    save_strategy_summary,
)

logger = logging.getLogger(__name__)


class SummaryEngine:
    """
    Institutional Summary Engine.

    Generates one-row-per-stock summary from a
    strategy folder containing trade CSVs.
    """

    def __init__(
        self,
        strategy_directory: str | Path,
        output_directory: str | Path | None = None,
    ) -> None:
        self.strategy_directory = Path(strategy_directory)

        if not self.strategy_directory.exists():
            raise FileNotFoundError(self.strategy_directory)

        self.strategy_name = self.strategy_directory.name

        if output_directory is None:
            self.output_directory = self.strategy_directory

        else:
            self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.summary_df: pd.DataFrame = pd.DataFrame()

    # --------------------------------------------------

    @property
    def summary_file(self) -> Path:
        return self.output_directory / f"{self.strategy_name}_summary.csv"

    # --------------------------------------------------

    def build(self) -> pd.DataFrame:
        """
        Build institutional summary.
        """

        logger.info("=" * 70)

        logger.info(
            "Building summary : %s",
            self.strategy_name,
        )

        logger.info("=" * 70)

        self.summary_df = build_strategy_summary(
            strategy_directory=self.strategy_directory,
            strategy_name=self.strategy_name,
        )

        return self.summary_df

    # --------------------------------------------------

    def save(self) -> Path:
        """
        Save summary CSV.
        """

        if self.summary_df.empty:
            raise RuntimeError("Summary has not been built.")

        save_strategy_summary(
            self.summary_df,
            str(self.summary_file),
        )

        return self.summary_file

    # --------------------------------------------------

    def run(self) -> pd.DataFrame:
        """
        Execute complete summary pipeline.
        """

        self.build()

        self.save()

        logger.info("Summary Engine completed.")

        logger.info(
            "Rows : %d",
            len(self.summary_df),
        )

        logger.info(
            "Output : %s",
            self.summary_file,
        )

        return self.summary_df


# ==========================================================
# Functional API
# ==========================================================


def generate_strategy_summary(
    strategy_directory: str | Path,
    output_directory: str | Path | None = None,
) -> pd.DataFrame:
    """
    Functional wrapper.

    Used by the main pipeline.
    """

    return SummaryEngine(
        strategy_directory,
        output_directory,
    ).run()


__all__ = [
    "SummaryEngine",
    "generate_strategy_summary",
]
