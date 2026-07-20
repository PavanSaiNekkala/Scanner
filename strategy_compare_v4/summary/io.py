"""
==============================================================
Institutional Strategy Comparison Platform V4
Summary IO Module
==============================================================

Responsible for:

• Discovering strategy trade files
• Reading trade CSVs
• Validating input
• Returning DataFrames
• Never computing metrics

Author : Pavan Sai Nekkala
==============================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


# ==========================================================
# Required Trade Columns
# ==========================================================

REQUIRED_COLUMNS = {
    "signal_date",
    "entry_date",
    "exit_date",
    "days_held",
    "outcome",
    "trade_type",
    "entry_price",
    "exit_price",
    "gross_return_%",
    "net_return_%",
}


# ==========================================================
# CSV Reader
# ==========================================================


def load_trade_file(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Read a single trade CSV.

    Parameters
    ----------
    file_path
        CSV file.

    Returns
    -------
    DataFrame
    """

    file_path = Path(file_path)

    logger.info(
        "Loading trade file: %s",
        file_path.name,
    )

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    df = pd.read_csv(file_path)

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"{file_path.name} missing columns:\n" + "\n".join(sorted(missing))
        )

    logger.info(
        "Loaded %s (%d trades)",
        file_path.name,
        len(df),
    )

    return df


# ==========================================================
# Discover Trade Files
# ==========================================================


def discover_trade_files(
    strategy_directory: str | Path,
) -> list[Path]:
    """
    Discover all trade CSVs inside a strategy folder.

    Ignores statistics workbooks and generated reports.
    """

    strategy_directory = Path(strategy_directory)

    if not strategy_directory.exists():
        raise FileNotFoundError(strategy_directory)

    csv_files = sorted(
        file for file in strategy_directory.glob("*.csv") if "_backtest_" in file.name
    )

    if not csv_files:
        raise FileNotFoundError(f"No trade CSV files found in {strategy_directory}")

    logger.info(
        "Discovered %d trade files.",
        len(csv_files),
    )

    return csv_files


# ==========================================================
# Load Entire Strategy
# ==========================================================


def load_strategy_directory(
    strategy_directory: str | Path,
) -> dict[str, pd.DataFrame]:
    """
    Load every stock trade file.

    Returns
    -------
    dict

        key   = Stock

        value = Trade DataFrame
    """

    trade_files = discover_trade_files(strategy_directory)

    strategy = {}

    for file in trade_files:
        stock = file.stem.split("_backtest_")[0]

        strategy[stock] = load_trade_file(file)

    logger.info(
        "Loaded %d stocks.",
        len(strategy),
    )

    return strategy


# ==========================================================
# Strategy Summary
# ==========================================================


def strategy_file_summary(
    strategy_directory: str | Path,
) -> pd.DataFrame:
    """
    Return simple inventory of all trade files.

    Useful for diagnostics.
    """

    trade_files = discover_trade_files(strategy_directory)

    rows = []

    for file in trade_files:
        df = load_trade_file(file)

        rows.append(
            {
                "Stock": file.stem.split("_backtest_")[0],
                "Trades": len(df),
                "Columns": len(df.columns),
                "File": file.name,
            }
        )

    return pd.DataFrame(rows)


# ==========================================================
# Exported Symbols
# ==========================================================

__all__ = [
    "discover_trade_files",
    "load_trade_file",
    "load_strategy_directory",
    "strategy_file_summary",
]
