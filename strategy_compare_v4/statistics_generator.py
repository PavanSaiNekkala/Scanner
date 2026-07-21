"""
=============================================================
Institutional Strategy Statistics Engine

Purpose
-------
Generate comprehensive descriptive statistics for every
backtest CSV and export them into Excel workbooks.

Features
--------
• Automatic folder discovery
• Automatic CSV discovery
• Institutional descriptive statistics
• Safe validation
• Logging
• Excel export

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# Configuration
# ============================================================

ROOT_DIRECTORY = Path(
    "/workspaces/Scanner/strategy_compare_v3",
)

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
# Statistics Engine
# ============================================================


class StatisticsEngine:
    """
    Institutional Statistics Engine.
    """

    def __init__(
        self,
        root_directory: str | Path = ROOT_DIRECTORY,
    ):
        self.root_directory = Path(
            root_directory,
        )

        self.processed_folders = 0

        self.processed_files = 0

    # ========================================================
    # Helpers
    # ========================================================

    def discover_folders(
        self,
    ):
        """
        Locate every backtest folder.
        """

        return sorted(
            self.root_directory.glob(
                BACKTEST_PATTERN,
            )
        )

    def discover_csv_files(
        self,
        folder: Path,
    ):
        """
        Locate CSV files.
        """

        return sorted(
            folder.glob(
                CSV_PATTERN,
            )
        )

    def load_dataframe(
        self,
        csv_file: Path,
    ) -> pd.DataFrame:
        """
        Load CSV safely.
        """

        dataframe = pd.read_csv(
            csv_file,
        )

        if dataframe.empty:
            raise ValueError(f"{csv_file.name} is empty.")

        return dataframe

    def numeric_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Return numeric columns.
        """

        numeric = dataframe.select_dtypes(
            include=np.number,
        )

        if numeric.empty:
            raise ValueError("No numeric columns found.")

        return numeric

    # ========================================================
    # Statistics
    # ========================================================

    def compute_statistics(
        self,
        numeric: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute institutional statistics.
        """

        statistics = pd.DataFrame(
            index=numeric.columns,
        )

        statistics["Count"] = numeric.count()

        statistics["Missing"] = numeric.isna().sum()

        statistics["Unique"] = numeric.nunique()

        statistics["Sum"] = numeric.sum()

        statistics["Mean"] = numeric.mean()

        statistics["Median"] = numeric.median()

        mode = numeric.mode(
            dropna=True,
        )

        statistics["Mode"] = mode.iloc[0] if not mode.empty else np.nan

        statistics["Variance"] = numeric.var()

        statistics["Std Dev"] = numeric.std()

        statistics["Std Error"] = statistics["Std Dev"] / np.sqrt(
            statistics["Count"],
        )

        statistics["Min"] = numeric.min()

        statistics["Max"] = numeric.max()

        statistics["Range"] = statistics["Max"] - statistics["Min"]

        statistics["Skewness"] = numeric.skew()

        statistics["Kurtosis"] = numeric.kurt()

        statistics["CV %"] = np.where(
            np.abs(
                statistics["Mean"],
            )
            > EPSILON,
            (statistics["Std Dev"] / statistics["Mean"]) * 100,
            np.nan,
        )

        for quantile in QUANTILES:
            label = f"{int(quantile * 100)}%"

            statistics[label] = numeric.quantile(
                quantile,
            )

        statistics["IQR"] = statistics["75%"] - statistics["25%"]

        statistics["Positive"] = (numeric > 0).sum()

        statistics["Negative"] = (numeric < 0).sum()

        statistics["Zero"] = (numeric == 0).sum()

        return statistics.round(
            ROUND_DECIMALS,
        )

    # ========================================================
    # Excel Export
    # ========================================================

    def export_folder(
        self,
        folder: Path,
    ):
        """
        Export statistics for one
        backtest folder.
        """

        print(f"\nProcessing {folder.name}")

        csv_files = self.discover_csv_files(
            folder,
        )

        if not csv_files:
            print("   No CSV files found.")
            return

        output_excel = folder / f"{folder.name}_Statistics.xlsx"

        with pd.ExcelWriter(
            output_excel,
            engine="openpyxl",
        ) as writer:
            for csv_file in csv_files:
                print(f"   {csv_file.name}")

                try:
                    dataframe = self.load_dataframe(
                        csv_file,
                    )

                    numeric = self.numeric_dataframe(
                        dataframe,
                    )

                    statistics = self.compute_statistics(
                        numeric,
                    )

                    sheet_name = (
                        csv_file.stem.replace(
                            "_backtest_",
                            "_",
                        )
                    )[:MAX_SHEET_NAME]

                    statistics.to_excel(
                        writer,
                        sheet_name=sheet_name,
                    )

                    self.processed_files += 1

                except Exception as exc:
                    print(f"      Skipped: {exc}")

                    continue

        self.processed_folders += 1

        print(f"Saved -> {output_excel}")

    # ========================================================
    # Run Engine
    # ========================================================

    def run(
        self,
    ):
        """
        Execute the complete
        statistics generation
        pipeline.
        """

        print("\n========================================")
        print("Institutional Statistics Engine")
        print("========================================")

        folders = self.discover_folders()

        if not folders:
            print("No backtest folders found.")
            return

        for folder in folders:
            self.export_folder(
                folder,
            )

        print("\n========================================")
        print("Execution Summary")
        print("========================================")

        print(f"Folders Processed : {self.processed_folders}")

        print(f"CSV Files Processed : {self.processed_files}")

        print("\nAll folders completed.")


# ============================================================
# Main
# ============================================================


def main():
    """
    Application entry point.
    """

    engine = StatisticsEngine()

    engine.run()


if __name__ == "__main__":
    main()
