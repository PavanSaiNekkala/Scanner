"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
stock_backtest_stats.py

Purpose
-------
Generate descriptive statistics workbooks for every
backtest strategy directory.

Each strategy folder receives one Statistics.xlsx
containing one worksheet per stock.

=============================================================
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from utils.logger import (
    banner,
    get_logger,
    log_execution_time,
)
from utils.math_utils import (
    round_dataframe,
)

logger = get_logger(__name__)


# ============================================================
# Configuration
# ============================================================

BACKTEST_PATTERN = "backtest_*"

CSV_PATTERN = "*.csv"

MAX_SHEET_NAME = 31

ROUND_DECIMALS = 4

EPSILON = 1e-12

QUANTILES = (
    0.05,
    0.10,
    0.25,
    0.50,
    0.75,
    0.90,
    0.95,
    0.99,
)


# ============================================================
# Helpers
# ============================================================


def numeric_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return numeric columns only.
    """

    numeric = df.select_dtypes(
        include=np.number,
    )

    if numeric.empty:
        logger.warning("No numeric columns found.")

    return numeric


def safe_mode(
    numeric: pd.DataFrame,
) -> pd.Series:
    """
    Safely compute mode.
    """

    mode = numeric.mode(
        dropna=True,
    )

    if mode.empty:
        return pd.Series(
            np.nan,
            index=numeric.columns,
        )

    return mode.iloc[0]


# ============================================================
# Statistics Engine
# ============================================================


def build_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate institutional
    descriptive statistics.
    """

    numeric = numeric_dataframe(
        df,
    )

    if numeric.empty:
        return pd.DataFrame()

    stats = pd.DataFrame(
        index=numeric.columns,
    )

    stats["Count"] = numeric.count()

    stats["Missing"] = numeric.isna().sum()

    stats["Unique"] = numeric.nunique()

    stats["Sum"] = numeric.sum()

    stats["Mean"] = numeric.mean()

    stats["Median"] = numeric.median()

    stats["Mode"] = safe_mode(
        numeric,
    )

    stats["Variance"] = numeric.var()

    stats["Std Dev"] = numeric.std()

    stats["Std Error"] = stats["Std Dev"] / np.sqrt(
        stats["Count"],
    )

    stats["Min"] = numeric.min()

    stats["Max"] = numeric.max()

    stats["Range"] = stats["Max"] - stats["Min"]

    stats["25%"] = numeric.quantile(
        0.25,
    )

    stats["50%"] = numeric.quantile(
        0.50,
    )

    stats["75%"] = numeric.quantile(
        0.75,
    )

    stats["IQR"] = stats["75%"] - stats["25%"]

    stats["Skewness"] = numeric.skew()

    stats["Kurtosis"] = numeric.kurt()

    stats["CV %"] = np.where(
        np.abs(
            stats["Mean"],
        )
        > EPSILON,
        (stats["Std Dev"] / stats["Mean"]) * 100,
        np.nan,
    )

    # --------------------------------------------------------
    # Additional Quantiles
    # --------------------------------------------------------

    for quantile in QUANTILES:
        label = f"{int(quantile * 100)}%"

        stats[label] = numeric.quantile(
            quantile,
        )

    # --------------------------------------------------------
    # Distribution Statistics
    # --------------------------------------------------------

    stats["Positive"] = (numeric > 0).sum()

    stats["Negative"] = (numeric < 0).sum()

    stats["Zero"] = (numeric == 0).sum()

    stats["MAD"] = (
        numeric.sub(
            numeric.median(),
        )
        .abs()
        .median()
    )

    # --------------------------------------------------------
    # IQR Outliers
    # --------------------------------------------------------

    q1 = numeric.quantile(
        0.25,
    )

    q3 = numeric.quantile(
        0.75,
    )

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr

    upper = q3 + 1.5 * iqr

    stats["Outliers"] = (
        (
            numeric.lt(
                lower,
            )
        )
        | (
            numeric.gt(
                upper,
            )
        )
    ).sum()

    return round_dataframe(
        stats,
        ROUND_DECIMALS,
    )


# ============================================================
# Folder Processing
# ============================================================


def process_folder(
    folder: Path,
) -> None:
    """
    Generate statistics workbook
    for one strategy folder.
    """

    logger.info(
        "Processing %s",
        folder.name,
    )

    csv_files = sorted(
        folder.glob(
            CSV_PATTERN,
        )
    )

    if not csv_files:
        logger.warning("No CSV files found.")

        return

    output_excel = folder / f"{folder.name}_Statistics.xlsx"

    processed = 0

    skipped = 0

    with pd.ExcelWriter(
        output_excel,
        engine="openpyxl",
    ) as writer:
        for csv in csv_files:
            logger.info(
                "Reading %s",
                csv.name,
            )

            try:
                df = pd.read_csv(
                    csv,
                )

                if df.empty:
                    logger.warning(
                        "%s is empty.",
                        csv.name,
                    )

                    skipped += 1

                    continue

                stats = build_statistics(
                    df,
                )

                if stats.empty:
                    skipped += 1

                    continue

                sheet = (
                    csv.stem.replace(
                        "_backtest_",
                        "_",
                    )
                )[:MAX_SHEET_NAME]

                stats.to_excel(
                    writer,
                    sheet_name=sheet,
                )

                processed += 1

            except Exception:
                logger.exception(
                    "Failed processing %s",
                    csv.name,
                )

                skipped += 1

        logger.info(
            "Processed : %d",
            processed,
        )

        logger.info(
            "Skipped   : %d",
            skipped,
        )

    logger.info(
        "Saved %s",
        output_excel.name,
    )


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Application entry point.
    """

    banner(
        logger,
        "BACKTEST STATISTICS",
    )

    start = time.perf_counter()

    root = Path.cwd()

    backtest_dirs = sorted(
        root.glob(
            BACKTEST_PATTERN,
        )
    )

    if not backtest_dirs:
        logger.warning("No strategy folders found.")

        return

    logger.info(
        "Found %d strategy folders.",
        len(backtest_dirs),
    )

    processed = 0

    for folder in backtest_dirs:
        try:
            process_folder(
                folder,
            )

            processed += 1

        except Exception:
            logger.exception(
                "Failed processing folder %s",
                folder.name,
            )

    banner(
        logger,
        "Execution Summary",
    )

    logger.info(
        "Strategy Folders : %d",
        len(backtest_dirs),
    )

    logger.info(
        "Processed        : %d",
        processed,
    )

    logger.info(
        "Skipped          : %d",
        len(backtest_dirs) - processed,
    )

    log_execution_time(
        logger,
        time.perf_counter() - start,
        "Statistics Generation",
    )


# ============================================================
# CLI Entry
# ============================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        logger.warning("Execution cancelled by user.")

    except Exception:
        logger.exception("Statistics generation failed.")

        raise
