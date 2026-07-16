"""
============================================================
Institutional Strategy Comparison Engine V3

File : main.py

Master Execution Runner

Author : Pavan Sai

============================================================
"""

from __future__ import annotations


from pathlib import Path


from core.logger import get_logger


from batch_processing.parallel_runner import (
    ParallelBatchRunner
)


from reports.strategy_comparison_report import (
    StrategyComparisonReport
)


from reports.excel_strategy_exporter import (
    ExcelStrategyExporter
)



logger = get_logger(__name__)




def main():


    logger.info("=" * 80)


    logger.info(

        "Institutional Strategy Comparison Engine Started"

    )


    # ==================================================
    # CONFIGURATION
    # ==================================================


    BACKTEST_PATH = Path(

        "."

    )


    OUTPUT_PATH = (

        "outputs/excel/"
        "Institutional_Strategy_Comparison.xlsx"

    )


    WORKERS = 8



    # ==================================================
    # STEP 1
    # PARALLEL PROCESSING
    # ==================================================


    logger.info(

        "Starting Parallel Batch Processing..."

    )


    batch_runner = ParallelBatchRunner(

        BACKTEST_PATH,

        workers=WORKERS

    )


    comparison_dataframe = batch_runner.run()



    if comparison_dataframe.empty:


        raise RuntimeError(

            "No strategy results generated."

        )



    logger.info(

        "Processed records: %d",

        len(comparison_dataframe)

    )



    # ==================================================
    # STEP 2
    # STRATEGY COMPARISON
    # ==================================================


    logger.info(

        "Generating Strategy Comparison Report..."

    )


    report_engine = StrategyComparisonReport(

        comparison_dataframe

    )


    report = report_engine.generate()



    # Add complete dataset

    report[

        "Complete Comparison"

    ] = comparison_dataframe



    # ==================================================
    # STEP 3
    # EXCEL EXPORT
    # ==================================================


    logger.info(

        "Exporting Institutional Excel Report..."

    )


    exporter = ExcelStrategyExporter(

        OUTPUT_PATH

    )


    excel_file = exporter.export(

        report

    )



    logger.info(

        "Excel Generated: %s",

        excel_file

    )



    logger.info("=" * 80)


    logger.info(

        "PROCESS COMPLETED SUCCESSFULLY"

    )


    logger.info("=" * 80)



if __name__ == "__main__":


    main()