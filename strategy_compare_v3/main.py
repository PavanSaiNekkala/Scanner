"""
============================================================
Institutional Strategy Comparison Engine V3

Main Entry Point

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.loader import DataLoader
from core.logger import get_logger
from pipeline.analysis_pipeline import AnalysisPipeline

logger = get_logger(__name__)


def parse_arguments():

    parser = argparse.ArgumentParser(

        description="Institutional Strategy Comparison Engine V3"

    )

    parser.add_argument(

        "--input",

        required=True,

        help="CSV / Excel file"

    )

    parser.add_argument(

        "--config",

        required=False,

        default=None,

        help="Configuration file"

    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    input_file = Path(args.input)

    if not input_file.exists():

        logger.error(

            "Input file not found."

        )

        sys.exit(1)

    logger.info(

        "=" * 80

    )

    logger.info(

        "Institutional Strategy Comparison Engine"

    )

    logger.info(

        "=" * 80

    )

    # -----------------------------------------

    loader = DataLoader(

        input_file

    )

    dataframe = loader.load()

    # -----------------------------------------

    pipeline = AnalysisPipeline(

        dataframe

    )

    results = pipeline.run()

    # -----------------------------------------

    logger.info(

        "=" * 80

    )

    logger.info(

        "Execution Completed"

    )

    logger.info(

        "Execution Time : %.3f sec",

        results["Execution Time"]

    )

    logger.info(

        "=" * 80

    )

    print()

    print(

        pipeline.summary()

    )


if __name__ == "__main__":

    main()