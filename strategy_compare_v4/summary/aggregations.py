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

from .io import load_strategy_directory
from .metrics import compute_trade_metrics

logger = logging.getLogger(__name__)


# ==========================================================
# Summary Builder
# =========================================================


def build_strategy_summary(
    strategy_directory: str | Path,
    strategy_name: str,
) -> pd.DataFrame:
    strategy_directory = Path(strategy_directory)

    """
    Build one institutional summary table.

    Parameters
    ----------
    strategy_directory
        Folder containing trade CSVs.

    strategy_name
        Optional strategy name.

    Returns
    -------
    DataFrame
    """

    trade_logs = load_strategy_directory(strategy_directory)

    rows = []

    for stock, df in trade_logs.items():
        metrics = compute_trade_metrics(
            stock,
            df,
        )

        if strategy_name is not None:
            metrics["Strategy"] = strategy_name

        rows.append(metrics)

    summary = pd.DataFrame(rows)

    if summary.empty:
        logger.warning("No summary rows generated.")

        return summary

    # ------------------------------------------------------
    # Column Ordering
    # ------------------------------------------------------

    preferred = [
        "Stock",
        "Strategy",
        "Trades",
        "Wins",
        "Losses",
        "Win%",
        "Avg Win %",
        "Avg Loss %",
        "Profit Factor",
        "Reward Risk",
        "Expectancy",
        "Avg days",
        "Years",
        "Annual Return %",
        "CAGR",
        "Max Drawdown %",
        "Sharpe",
        "Sortino",
        "Recovery Factor",
    ]

    existing = [c for c in preferred if c in summary.columns]

    remaining = [c for c in summary.columns if c not in existing]

    summary = summary[existing + remaining]

    summary = summary.sort_values(
        by="Expectancy",
        ascending=False,
        ignore_index=True,
    )

    logger.info("Institutional summary built.")

    logger.info(
        "Stocks : %d",
        len(summary),
    )

    return summary


# ==========================================================
# Save Summary
# ==========================================================


def save_strategy_summary(
    summary: pd.DataFrame,
    output_file: str,
) -> None:
    """
    Save institutional summary.
    """

    summary.to_csv(
        output_file,
        index=False,
    )

    logger.info(
        "Summary saved: %s",
        output_file,
    )


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "build_strategy_summary",
    "save_strategy_summary",
]
