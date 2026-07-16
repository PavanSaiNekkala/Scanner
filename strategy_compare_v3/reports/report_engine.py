"""
============================================================
Institutional Strategy Comparison Engine V3
File : reports/report_engine.py

Master Report Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from core.logger import get_logger

from reports.summary_report import SummaryReport
from reports.institutional_report import InstitutionalReport
from reports.excel_report import ExcelReport

logger = get_logger(__name__)


class ReportEngine:
    """
    Master Report Engine.

    Coordinates all report generation modules.

    Responsibilities
    ----------------
    • Executive Summary
    • Institutional Report
    • Excel Export
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        output_directory: str = "outputs/excel",
    ):

        self.df = dataframe.copy()

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.execution_time = 0.0

        self.results: Dict[str, Any] = {}

    # -----------------------------------------------------

    def summary_report(self):

        logger.info(
            "Generating Summary Report..."
        )

        return SummaryReport(
            self.df
        ).generate()

    # -----------------------------------------------------

    def institutional_report(self):

        logger.info(
            "Generating Institutional Report..."
        )

        return InstitutionalReport(
            self.df
        ).generate()

    # -----------------------------------------------------

    def excel_report(
        self,
        report_dictionary: Dict[str, pd.DataFrame]
    ):

        logger.info(
            "Generating Excel Workbook..."
        )

        exporter = ExcelReport(
            output_directory=self.output_directory
        )

        return exporter.generate(
            report_dictionary
        )

    # -----------------------------------------------------

    def run(self):

        logger.info("=" * 80)

        logger.info(
            "Starting Report Engine..."
        )

        start = time.perf_counter()

        # ---------------------------------------------
        # Summary Report
        # ---------------------------------------------

        summary = self.summary_report()

        # ---------------------------------------------
        # Institutional Report
        # ---------------------------------------------

        institutional = self.institutional_report()

        # ---------------------------------------------
        # Merge Reports
        # ---------------------------------------------

        workbook = {}

        workbook.update(summary)

        workbook.update(institutional)

        # ---------------------------------------------
        # Excel Export
        # ---------------------------------------------

        excel_file = self.excel_report(
            workbook
        )

        # ---------------------------------------------

        self.execution_time = round(

            time.perf_counter() - start,

            3

        )

        self.results = {

            "Summary Report":

                summary,

            "Institutional Report":

                institutional,

            "Excel File":

                excel_file,

            "Execution Time":

                self.execution_time

        }

        logger.info(

            "Report Engine completed in %.3f sec.",

            self.execution_time

        )

        logger.info("=" * 80)

        return self.results

    # -----------------------------------------------------

    def summary(self):

        return {

            "Reports Generated": [

                "Summary Report",

                "Institutional Report",

                "Excel Workbook"

            ],

            "Execution Time":

                self.execution_time

        }

    # -----------------------------------------------------

    def get_excel_file(self):

        return self.results.get(

            "Excel File"

        )


if __name__ == "__main__":

    print(

        "Import inside main.py"

    )