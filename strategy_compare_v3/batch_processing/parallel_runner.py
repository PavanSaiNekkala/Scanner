"""
============================================================
Institutional Strategy Comparison Engine V3

File : batch_processing/parallel_runner.py

Parallel Batch Processor

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import time

from pathlib import Path

from concurrent.futures import ProcessPoolExecutor, as_completed


import pandas as pd


from core.logger import get_logger


from batch_processing.batch_runner import BatchRunner

logger = get_logger(__name__)


class ParallelBatchRunner:
    """
    Parallel processing engine.


    Responsibilities
    ----------------

    ✓ Discover CSV files

    ✓ Process multiple files simultaneously

    ✓ Handle failures independently

    ✓ Collect final dataframe



    """

    def __init__(self, root_directory: str | Path, workers: int = 4):
        self.root_directory = Path(root_directory)

        self.workers = workers

        self.execution_time = 0.0

    # ==================================================
    # SINGLE FILE WORKER
    # ==================================================

    @staticmethod
    def process_single_file(file_path):
        runner = BatchRunner(file_path.parent.parent)

        return runner.process_file(file_path)

    # ==================================================
    # DISCOVER FILES
    # ==================================================

    def discover_files(self):
        return list(self.root_directory.rglob("*.csv"))

    # ==================================================
    # RUN PARALLEL
    # ==================================================

    def run(self):
        logger.info("=" * 80)

        logger.info("Starting Parallel Batch Processing...")

        start = time.perf_counter()

        files = self.discover_files()

        logger.info("Total CSV files found: %d", len(files))

        results = []

        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self.process_single_file, file): file for file in files
            }

            for future in as_completed(futures):
                file = futures[future]

                try:
                    result = future.result()

                    results.append(result)

                    logger.info("Completed: %s", file)

                except Exception as error:
                    logger.exception("Failed: %s : %s", file, error)

        if results:
            final = pd.concat(results, ignore_index=True)

        else:
            final = pd.DataFrame()

        self.execution_time = round(time.perf_counter() - start, 3)

        logger.info(
            "Parallel processing completed in %.3f seconds", self.execution_time
        )

        logger.info("=" * 80)

        return final


if __name__ == "__main__":
    runner = ParallelBatchRunner("data/input/backtest", workers=8)

    result = runner.run()

    print(result.head())
