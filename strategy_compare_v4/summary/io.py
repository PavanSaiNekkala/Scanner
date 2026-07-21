"""
==============================================================
Institutional Strategy Comparison Platform V4
Summary IO Module
==============================================================

Responsible for

• Discovering strategy trade files
• Reading trade CSVs
• Validating input
• Returning DataFrames
• Never computing metrics

==============================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from strategy_compare_v4.utils.helpers import (
    require_columns,
    validate_dataframe,
)
from strategy_compare_v4.utils.io_utils import (
    read_csv,
)

logger = logging.getLogger(__name__)

# ==========================================================
# Constants
# ==========================================================

TRADE_FILE_PATTERN = "_backtest_"

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
# Stock Name Helper
# ==========================================================


def extract_stock_name(
    file: Path,
) -> str:
    """
    Extract stock name from a trade filename.
    """

    return file.stem.split(
        TRADE_FILE_PATTERN,
    )[0]


# ==========================================================
# CSV Reader
# ==========================================================


def load_trade_file(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Load and validate a trade CSV.
    """

    file_path = Path(
        file_path,
    )

    logger.info(
        "Loading %s",
        file_path.name,
    )

    df = read_csv(
        file_path,
    )

    validate_dataframe(
        df,
    )

    require_columns(
        df,
        REQUIRED_COLUMNS,
    )

    logger.info(
        "Trades : %d",
        len(df),
    )

    return df


# ==========================================================
# Trade File Discovery
# ==========================================================


def discover_trade_files(
    strategy_directory: str | Path,
) -> list[Path]:
    """
    Discover all trade CSV files.
    """

    strategy_directory = Path(
        strategy_directory,
    )

    if not strategy_directory.exists():
        raise FileNotFoundError(
            strategy_directory,
        )

    trade_files = sorted(
        file
        for file in strategy_directory.glob("*.csv")
        if TRADE_FILE_PATTERN in file.name
    )

    if not trade_files:
        raise FileNotFoundError(f"No trade files found in {strategy_directory}")

    logger.info(
        "Trade files discovered : %d",
        len(trade_files),
    )

    return trade_files


# ==========================================================
# Load Entire Strategy
# ==========================================================


def load_strategy_directory(
    strategy_directory: str | Path,
) -> dict[str, pd.DataFrame]:
    """
    Load every trade file within a strategy directory.

    Returns
    -------
    dict[str, pd.DataFrame]
        Key   : Stock symbol
        Value : Trade DataFrame
    """

    trade_files = discover_trade_files(
        strategy_directory,
    )

    strategy: dict[str, pd.DataFrame] = {}

    processed = 0
    skipped = 0

    for file in trade_files:
        try:
            stock = extract_stock_name(
                file,
            )

            strategy[stock] = load_trade_file(
                file,
            )

            processed += 1

        except Exception:
            logger.exception(
                "Failed to load %s",
                file.name,
            )

            skipped += 1

    logger.info("Strategy loaded successfully.")

    logger.info(
        "Processed : %d",
        processed,
    )

    logger.info(
        "Skipped : %d",
        skipped,
    )

    return strategy


# ==========================================================
# Strategy File Summary
# ==========================================================


def strategy_file_summary(
    strategy_directory: str | Path,
) -> pd.DataFrame:
    """
    Build a simple inventory of all trade files
    within a strategy directory.
    """

    trade_files = discover_trade_files(
        strategy_directory,
    )

    rows: list[dict] = []

    for file in trade_files:
        try:
            df = load_trade_file(
                file,
            )

            validate_dataframe(
                df,
            )

            rows.append(
                {
                    "Stock": extract_stock_name(file),
                    "Trades": len(df),
                    "Columns": len(df.columns),
                    "Missing Values": int(df.isna().sum().sum()),
                    "Duplicate Rows": int(df.duplicated().sum()),
                    "File": file.name,
                }
            )

        except Exception:
            logger.exception(
                "Unable to summarize %s",
                file.name,
            )

    summary = pd.DataFrame(
        rows,
    )

    if not summary.empty:
        summary = summary.sort_values(
            by="Stock",
            kind="stable",
            ignore_index=True,
        )

    logger.info(
        "Strategy inventory created (%d files).",
        len(summary),
    )

    return summary


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "REQUIRED_COLUMNS",
    "TRADE_FILE_PATTERN",
    "extract_stock_name",
    "discover_trade_files",
    "load_trade_file",
    "load_strategy_directory",
    "strategy_file_summary",
]
