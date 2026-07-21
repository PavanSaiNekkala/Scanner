"""
===============================================================
Institutional Strategy Comparison Engine V4

Master Derived Metrics Engine

Author
------
OpenAI

===============================================================
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    INSTITUTION_RANK,
    RECOMMENDATION,
    VALIDATION_STATUS,
)
from strategy_compare_v4.derived_metrics.efficiency_metrics import (
    derive_efficiency_metrics,
)
from strategy_compare_v4.derived_metrics.exit_metrics import (
    derive_exit_metrics,
)
from strategy_compare_v4.derived_metrics.opportunity_metrics import (
    derive_opportunity_metrics,
)
from strategy_compare_v4.derived_metrics.performance_metrics import (
    derive_performance_metrics,
)
from strategy_compare_v4.derived_metrics.risk_metrics import (
    derive_risk_metrics,
)
from strategy_compare_v4.derived_metrics.scoring_metrics import (
    derive_scoring_metrics,
)
from strategy_compare_v4.derived_metrics.validation_metrics import (
    derive_validation_metrics,
)
from strategy_compare_v4.utils.helpers import (
    require_columns,
)
from strategy_compare_v4.utils.io_utils import (
    read_csv,
    read_excel,
    write_excel,
)
from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)

logger = get_logger(__name__)


class DerivedMetricsEngine:
    """
    Master Institutional Derived Metrics Engine

    Pipeline
    --------
    Validation
          ↓
    Performance
          ↓
    Risk
          ↓
    Exit
          ↓
    Opportunity
          ↓
    Efficiency
          ↓
    Institutional Scoring
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

        from typing import Any

        self.summary: dict[str, Any] = {}

        self.diagnostics_report: dict[str, Any] = {}

    # ---------------------------------------------------------
    # Validation Stage
    # ---------------------------------------------------------

    def validation_stage(self):
        logger.info("Running Validation Metrics...")

        self.df = derive_validation_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Performance Stage
    # ---------------------------------------------------------

    def performance_stage(self):
        logger.info("Running Performance Metrics...")

        self.df = derive_performance_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Risk Stage
    # ---------------------------------------------------------

    def risk_stage(self):
        logger.info("Running Risk Metrics...")

        self.df = derive_risk_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Exit Stage
    # ---------------------------------------------------------

    def exit_stage(self):
        logger.info("Running Exit Metrics...")

        self.df = derive_exit_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Opportunity Stage
    # ---------------------------------------------------------

    def opportunity_stage(self):
        logger.info("Running Opportunity Metrics...")

        self.df = derive_opportunity_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Efficiency Stage
    # ---------------------------------------------------------

    def efficiency_stage(self):
        logger.info("Running Efficiency Metrics...")

        self.df = derive_efficiency_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Dependency Validation
    # ---------------------------------------------------------

    def validate_dependencies(self):
        """
        Verify all required derived metrics
        exist before institutional scoring.
        """

        require_columns(
            self.df,
            [
                "Expectancy",
                "Profit Factor",
                "Reward Risk",
                "Institutional Exit Score",
                "Institutional Opportunity Score",
                "Institutional Efficiency Score",
            ],
        )

        return self

    # ---------------------------------------------------------
    # Institutional Scoring Stage
    # ---------------------------------------------------------

    def scoring_stage(self):
        logger.info("Running Institutional Scoring...")

        self.df = derive_scoring_metrics(self.df)

        return self

    # ---------------------------------------------------------
    # Pipeline Summary
    # ---------------------------------------------------------

    def pipeline_summary(self):
        """
        Build pipeline execution summary.
        """

        self.summary = {
            "Rows Processed": len(self.df),
            "Columns Produced": len(self.df.columns),
            "Passed Validation": (
                int((self.df[VALIDATION_STATUS] == "PASSED").sum())
                if VALIDATION_STATUS in self.df.columns
                else None
            ),
            "Warning Rows": (
                int((self.df[VALIDATION_STATUS] == "WARNING").sum())
                if VALIDATION_STATUS in self.df.columns
                else None
            ),
            "Failed Validation": (
                int((self.df[VALIDATION_STATUS] == "FAILED").sum())
                if VALIDATION_STATUS in self.df.columns
                else None
            ),
        }

        return self

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    def diagnostics(self):
        """
        Generate institutional diagnostics.
        """

        diagnostics = {}

        if COMPOSITE_SCORE in self.df.columns:
            diagnostics["Average Composite"] = round(self.df[COMPOSITE_SCORE].mean(), 2)

            diagnostics["Maximum Composite"] = round(self.df[COMPOSITE_SCORE].max(), 2)

            diagnostics["Minimum Composite"] = round(self.df[COMPOSITE_SCORE].min(), 2)

        if RECOMMENDATION in self.df.columns:
            diagnostics["Recommendations"] = (
                self.df[RECOMMENDATION].value_counts().to_dict()
            )

        self.diagnostics_report = diagnostics

        return self

    # ---------------------------------------------------------
    # Execution Report
    # ---------------------------------------------------------

    def execution_report(self):
        """
        Log pipeline execution summary.
        """

        banner(logger, "Institutional Metrics Engine Completed")

        for key, value in self.summary.items():
            logger.info("%-30s : %s", key, value)

        if self.diagnostics_report:
            logger.info("")

            for key, value in self.diagnostics_report.items():
                logger.info("%-30s : %s", key, value)

        logger.info("")

        logger.info("Derived Metrics Pipeline Completed Successfully.")

        return self

    # ---------------------------------------------------------
    # Sort Results
    # ---------------------------------------------------------

    def sort_results(self):
        """
        Sort final institutional output.
        """

        if INSTITUTION_RANK in self.df.columns:
            self.df = self.df.sort_values(INSTITUTION_RANK, ascending=True).reset_index(
                drop=True
            )

        elif COMPOSITE_SCORE in self.df.columns:
            self.df = self.df.sort_values(COMPOSITE_SCORE, ascending=False).reset_index(
                drop=True
            )

        return self

    # ---------------------------------------------------------
    # DataFrame
    # ---------------------------------------------------------

    def get_dataframe(self):
        """
        Return processed dataframe.
        """

        return self.df

    # ---------------------------------------------------------
    # Run Pipeline
    # ---------------------------------------------------------

    def run(self):
        """
        Execute complete institutional
        derived metrics pipeline.
        """

        start = time.perf_counter()

        try:
            (
                self.validation_stage()
                .performance_stage()
                .risk_stage()
                .exit_stage()
                .opportunity_stage()
                .efficiency_stage()
                .validate_dependencies()
                .scoring_stage()
                .pipeline_summary()
                .diagnostics()
                .sort_results()
            )

        except Exception as exc:
            logger.exception("Derived Metrics Engine failed.")

            raise RuntimeError(f"Derived Metrics Engine failed:\n{exc}") from exc

        finally:
            self.execution_time = round(time.perf_counter() - start, 3)

        self.summary["Execution Time (s)"] = self.execution_time

        self.execution_report()

        return self.df


# ===========================================================
# Convenience Function
# ===========================================================


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute complete institutional
    derived metrics pipeline.
    """

    return DerivedMetricsEngine(df).run()


# ===========================================================
# File Processing
# ===========================================================


def process_file(
    input_file: str,
    output_file: str | None = None,
) -> pd.DataFrame:
    """
    Process a single CSV/Excel file.
    """

    logger.info(
        "Loading file: %s",
        input_file,
    )

    input_path = Path(input_file)

    extension = input_path.suffix.lower()

    if extension == ".csv":
        df = read_csv(input_file)

    elif extension in {
        ".xlsx",
        ".xls",
    }:
        df = read_excel(input_file)

    else:
        raise ValueError(f"Unsupported file type: {extension}")

    result = derive_metrics(df)

    if output_file is None:
        output_file = str(input_path.with_name(input_path.stem + "_Institutional.xlsx"))

    write_excel(
        result,
        output_file,
    )

    logger.info(
        "Output saved: %s",
        output_file,
    )

    return result


# ===========================================================
# Directory Processing
# ===========================================================


def process_directory(
    directory: str | Path,
) -> None:
    """
    Process every CSV and Excel file
    inside a directory.
    """

    path = Path(directory)

    files = sorted(
        list(path.glob("*.csv")) + list(path.glob("*.xlsx")) + list(path.glob("*.xls"))
    )

    if not files:
        logger.warning(
            "No input files found in %s",
            path,
        )

        return

    logger.info(
        "Found %d files.",
        len(files),
    )

    for file in files:
        try:
            process_file(str(file))

        except Exception:
            logger.exception(
                "Failed processing %s",
                file.name,
            )


# ===========================================================
# Main
# ===========================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=("Institutional Strategy Comparison Engine V4")
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Input CSV or Excel file",
    )

    parser.add_argument(
        "--dir",
        type=str,
        help="Directory containing reports",
    )

    args = parser.parse_args()

    if args.file:
        process_file(args.file)

    elif args.dir:
        process_directory(args.dir)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
