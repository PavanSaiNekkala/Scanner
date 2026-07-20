"""
============================================================
Institutional Strategy Comparison Engine V3

File : batch_processing/batch_runner.py

Batch Strategy Processor

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import time

from pathlib import Path


import pandas as pd


from core.logger import get_logger

from core.loader import DataLoader


from pipeline.analysis_pipeline import AnalysisPipeline


from batch_processing.strategy_detector import StrategyDetector


from batch_processing.result_collector import ResultCollector

logger = get_logger(__name__)


class BatchRunner:
    """
    Processes multiple backtest folders.


    Folder Structure Expected
    -------------------------


    backtest_data/

        Strategy_A/

            RELIANCE.csv
            TCS.csv


        Strategy_B/

            RELIANCE.csv
            TCS.csv


    Output
    ------

    Combined strategy comparison dataframe

    """

    def __init__(self, root_directory: str | Path):
        self.root_directory = Path(root_directory)

        self.collector = ResultCollector()

        self.execution_time = 0.0

    # ==================================================
    # PROCESS SINGLE FILE
    # ==================================================

    def process_file(self, file_path: Path):
        logger.info("Processing %s", file_path)

        # ----------------------------------------------
        # DATA LOADING
        # ----------------------------------------------

        loader = DataLoader(file_path)

        dataframe = loader.run()

        logger.info("Loaded dataframe shape: %s", dataframe.shape)

        # ----------------------------------------------
        # ANALYSIS PIPELINE
        # ----------------------------------------------

        pipeline = AnalysisPipeline(dataframe)

        output = pipeline.run()

        scored_df = output.get("Recommendation")

        if scored_df is None:
            raise ValueError("Recommendation output missing from AnalysisPipeline")

        # ----------------------------------------------
        # STRATEGY METADATA
        # ----------------------------------------------

        metadata = StrategyDetector(file_path).metadata()

        for key, value in metadata.items():
            scored_df[key] = value

        return scored_df

    # ==================================================
    # DISCOVER CSV FILES
    # ==================================================

    def discover_files(self):
        files = list(self.root_directory.rglob("*.csv"))

        logger.info("Found %d CSV files", len(files))

        return files

    # ==================================================
    # RUN BATCH
    # ==================================================

    def run(self):
        logger.info("=" * 80)

        logger.info("Starting Batch Processing...")

        start = time.perf_counter()

        files = self.discover_files()

        for file in files:
            try:
                result = self.process_file(file)

                self.collector.add(result)

            except Exception as error:
                logger.exception("Failed processing %s : %s", file, error)

        # ----------------------------------------------
        # FINAL COLLECTION
        # ----------------------------------------------

        try:
            final_dataframe = self.collector.generate()

        except Exception as error:
            logger.exception("Result collection failed : %s", error)

            final_dataframe = pd.DataFrame()

        self.execution_time = round(time.perf_counter() - start, 3)

        logger.info("Batch completed in %.3f seconds", self.execution_time)

        logger.info("=" * 80)

        return final_dataframe

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):
        return {
            "Root Directory": str(self.root_directory),
            "Execution Time": self.execution_time,
        }


if __name__ == "__main__":
    runner = BatchRunner("data/input/backtest")

    output = runner.run()

    print(output.head())
