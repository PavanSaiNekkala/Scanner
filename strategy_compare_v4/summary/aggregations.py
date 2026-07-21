"""
==============================================================
Institutional Strategy Comparison Platform V4
Summary Aggregation Engine
==============================================================

Converts multiple trade logs into one institutional
summary DataFrame.

One Strategy Folder
        ↓
Many Trade CSVs
        ↓
One Summary DataFrame

==============================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from strategy_compare_v4.config.constants import (
    EXPECTANCY,
    STOCK,
    STRATEGY,
)
from strategy_compare_v4.utils.helpers import (
    dataframe_summary,
    sort_dataframe,
)
from strategy_compare_v4.utils.io_utils import write_csv

from .io import load_strategy_directory
from .metrics import compute_trade_metrics

logger = logging.getLogger(__name__)

# ==========================================================
# Preferred Column Order
# ==========================================================

PREFERRED_COLUMNS = [
    STOCK,
    STRATEGY,
    "Trades",
    "Wins",
    "Losses",
    "Win%",
    "Avg Win %",
    "Avg Loss %",
    "Profit Factor",
    "Reward Risk",
    EXPECTANCY,
    "Avg days",
    "Years",
    "Annual Return %",
    "CAGR",
    "Max Drawdown %",
    "Sharpe",
    "Sortino",
    "Recovery Factor",
]


# ==========================================================
# Strategy Summary
# ==========================================================


def build_strategy_summary(
    strategy_directory: str | Path,
    strategy_name: str | None = None,
) -> pd.DataFrame:
    """
    Build one institutional summary table.
    """

    strategy_directory = Path(
        strategy_directory,
    )

    logger.info(
        "Loading strategy directory: %s",
        strategy_directory,
    )

    trade_logs = load_strategy_directory(
        strategy_directory,
    )

    rows: list[dict] = []

    processed = 0

    skipped = 0

    for stock, df in trade_logs.items():
        if df.empty:
            skipped += 1

            continue

        metrics = compute_trade_metrics(
            stock,
            df,
        )

        if strategy_name is not None:
            metrics[STRATEGY] = strategy_name

        rows.append(metrics)

        processed += 1

    summary = pd.DataFrame(
        rows,
    )

    if summary.empty:
        logger.warning("No summary rows generated.")

        return summary

    # ------------------------------------------------------
    # Column Ordering
    # ------------------------------------------------------

    existing = [column for column in PREFERRED_COLUMNS if column in summary.columns]

    remaining = [column for column in summary.columns if column not in existing]

    summary = summary[existing + remaining]

    # ------------------------------------------------------
    # Sorting
    # ------------------------------------------------------

    if EXPECTANCY in summary.columns:
        summary = sort_dataframe(
            summary,
            column=EXPECTANCY,
            ascending=False,
        )

    # ------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------

    diagnostics = dataframe_summary(
        summary,
    )

    logger.info("Strategy summary completed.")

    logger.info(
        "Processed : %d",
        processed,
    )

    logger.info(
        "Skipped : %d",
        skipped,
    )

    logger.info(
        "Rows : %d",
        diagnostics["Rows"],
    )

    logger.info(
        "Columns : %d",
        diagnostics["Columns"],
    )

    logger.info(
        "Missing Values : %d",
        diagnostics["Missing Values"],
    )

    logger.info(
        "Duplicate Rows : %d",
        diagnostics["Duplicate Rows"],
    )

    return summary


# ==========================================================
# Save Summary
# ==========================================================


def save_strategy_summary(
    summary: pd.DataFrame,
    output_file: str | Path,
) -> None:
    """
    Save institutional summary CSV.
    """

    output_file = Path(
        output_file,
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        summary,
        output_file,
    )

    logger.info("Summary saved successfully.")

    logger.info(
        "Output : %s",
        output_file,
    )

    logger.info(
        "Rows : %d",
        len(summary),
    )


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "build_strategy_summary",
    "save_strategy_summary",
]
