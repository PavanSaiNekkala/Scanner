"""
============================================================
Institutional Strategy Comparison Engine V3
File : profiling/profiler.py

Master Profiling Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


from typing import Dict


import pandas as pd


from core.logger import get_logger


from profiling.dataset_summary import DatasetSummary
from profiling.column_profiler import ColumnProfiler
from profiling.descriptive_statistics import DescriptiveStatistics
from profiling.distribution_statistics import DistributionStatistics
from profiling.missing_value_profiler import MissingValueProfiler
from profiling.data_quality import DataQuality



logger = get_logger(__name__)




class DataProfiler:
    """
    Master profiling engine.


    Executes all profiling modules.


    Pipeline Contract
    -----------------

    AnalysisPipeline expects:

        DataProfiler.generate()


    Internal execution:

        run()


    Returns
    -------

    Dictionary of profiling outputs.

    """



    def __init__(

        self,

        dataframe: pd.DataFrame

    ):


        self.df = dataframe.copy()


        self.results: Dict[str, pd.DataFrame] = {}



    # ==================================================
    # MAIN PROFILING ENGINE
    # ==================================================

    def run(self):


        logger.info("=" * 80)


        logger.info(

            "Starting Profiling Engine..."

        )



        # ----------------------------------------------
        # Dataset Summary
        # ----------------------------------------------

        dataset_summary = DatasetSummary(

            self.df

        ).generate()



        # ----------------------------------------------
        # Column Profiling
        # ----------------------------------------------

        column_profile = ColumnProfiler(

            self.df

        ).profile()



        # ----------------------------------------------
        # Descriptive Statistics
        # ----------------------------------------------

        descriptive = DescriptiveStatistics(

            column_profile

        ).generate()



        # ----------------------------------------------
        # Distribution Statistics
        # ----------------------------------------------

        distribution = DistributionStatistics(

            self.df

        ).generate()



        # ----------------------------------------------
        # Missing Values
        # ----------------------------------------------

        missing = MissingValueProfiler(

            self.df

        ).generate()



        # ----------------------------------------------
        # Data Quality
        # ----------------------------------------------

        quality = DataQuality(

            self.df

        ).generate()



        # ----------------------------------------------
        # Store Results
        # ----------------------------------------------

        self.results = {


            "Dataset Summary":

                dataset_summary,


            "Column Profile":

                column_profile,


            "Descriptive Statistics":

                descriptive,


            "Distribution Statistics":

                distribution,


            "Missing Values":

                missing,


            "Data Quality":

                quality

        }



        logger.info(

            "Profiling completed successfully."

        )


        logger.info("=" * 80)



        return self.results




    # ==================================================
    # PIPELINE COMPATIBILITY METHOD
    # ==================================================

    def generate(self):

        """
        Standard pipeline entry point.


        AnalysisPipeline uses generate()
        across all engines.

        This wrapper maintains
        architectural consistency.

        """


        return self.run()




    # ==================================================
    # REPORT ACCESS
    # ==================================================

    def get_report(

        self,

        name: str

    ) -> pd.DataFrame:


        return self.results.get(

            name

        )




    # ==================================================
    # AVAILABLE REPORTS
    # ==================================================

    def report_names(self):


        return list(

            self.results.keys()

        )




# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":


    print(

        "Use this module from main.py"

    )