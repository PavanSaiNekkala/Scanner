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

from utils.io_utils import (
    find_backtest_files,
    write_excel,
)
from utils.logger import (
    banner,
    get_logger,
    log_execution_time,
)
from utils.math_utils import round_dataframe

logger = get_logger(__name__)

# ============================================================
# Statistics Engine
# ============================================================

def build_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate descriptive statistics for all
    numeric columns.
    """

    numeric = df.select_dtypes(include=np.number)

    if numeric.empty:
        return pd.DataFrame()

    stats = pd.DataFrame(index=numeric.columns)

    stats["Count"] = numeric.count()

    stats["Missing"] = numeric.isna().sum()

    stats["Sum"] = numeric.sum()

    stats["Mean"] = numeric.mean()

    stats["Median"] = numeric.median()

    stats["Mode"] = numeric.mode().iloc[0]

    stats["Variance"] = numeric.var()

    stats["Std Dev"] = numeric.std()

    stats["Min"] = numeric.min()

    stats["25%"] = numeric.quantile(0.25)

    stats["50%"] = numeric.quantile(0.50)

    stats["75%"] = numeric.quantile(0.75)

    stats["Max"] = numeric.max()

    stats["Range"] = stats["Max"] - stats["Min"]

    stats["IQR"] = stats["75%"] - stats["25%"]

    stats["Skewness"] = numeric.skew()

    stats["Kurtosis"] = numeric.kurt()

    stats["CV %"] = np.where(
        stats["Mean"] != 0,
        stats["Std Dev"] / stats["Mean"] * 100,
        np.nan,
    )

    stats["Std Error"] = (
        stats["Std Dev"] /
        np.sqrt(stats["Count"])
    )

    stats["5%"] = numeric.quantile(0.05)

    stats["10%"] = numeric.quantile(0.10)

    stats["90%"] = numeric.quantile(0.90)

    stats["95%"] = numeric.quantile(0.95)

    stats["99%"] = numeric.quantile(0.99)

    return round_dataframe(stats, 4)

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

    logger.info("Processing %s", folder.name)

    csv_files = sorted(folder.glob("*.csv"))

    if not csv_files:

        logger.warning(
            "No CSV files found."
        )

        return

    output_excel = (
        folder /
        f"{folder.name}_Statistics.xlsx"
    )

    with pd.ExcelWriter(
        output_excel,
        engine="openpyxl",
    ) as writer:

        for csv in csv_files:

            logger.info(
                "Reading %s",
                csv.name,
            )

            df = pd.read_csv(csv)

            stats = build_statistics(df)

            if stats.empty:

                continue

            sheet = (
                csv.stem
                .replace("_backtest_", "_")
            )[:31]

            stats.to_excel(
                writer,
                sheet_name=sheet,
            )

    logger.info(
        "Saved %s",
        output_excel.name,
    )

# ============================================================
# Main
# ============================================================

def main() -> None:

    banner(
        logger,
        "BACKTEST STATISTICS",
    )

    start = time.perf_counter()

    root = Path.cwd()

    backtest_dirs = sorted(
        root.glob("backtest_*")
    )

    logger.info(
        "Found %d strategy folders.",
        len(backtest_dirs),
    )

    for folder in backtest_dirs:

        process_folder(folder)

    log_execution_time(
        logger,
        time.perf_counter() - start,
        "Statistics Generation",
    )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        logger.warning(
            "Execution cancelled."
        )

    except Exception:

        logger.exception(
            "Statistics generation failed."
        )

        raise