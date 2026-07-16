"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/derived_engine.py

Master Derived Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import time

from typing import Dict, Any


import pandas as pd


from core.logger import get_logger



from derived_metrics.derived_metrics_engine import (
    TradeMetricsEngine
)


from derived_metrics.performance_metrics import (
    PerformanceMetricsEngine
)


from derived_metrics.reliability_metrics import (
    ReliabilityMetricsEngine
)


from derived_metrics.risk_metrics import (
    RiskMetricsEngine
)


from derived_metrics.exit_metrics import (
    ExitMetricsEngine
)


from derived_metrics.efficiency_metrics import (
    EfficiencyMetricsEngine
)


from derived_metrics.opportunity_metrics import (
    OpportunityMetricsEngine
)


from derived_metrics.statistical_metrics import (
    StatisticalMetricsEngine
)




logger = get_logger(__name__)





class DerivedMetricsEngine:
    """
    Master Derived Metrics Pipeline.


    Flow
    ----

    Trade Level CSV

            |

            v

    TradeMetricsEngine

            |

            v

    Strategy Level Data

            |

            v

    Performance Metrics

    Reliability Metrics

    Risk Metrics

    Exit Metrics

    Efficiency Metrics

    Opportunity Metrics

    Statistical Metrics

            |

            v

    Feature Engineering


    """



    def __init__(

        self,

        dataframe: pd.DataFrame

    ):


        self.df = dataframe.copy()


        self.execution_time = 0.0


        self.generated_metrics = []


        self.module_summary = []





    # ==================================================
    # MODULE PIPELINE
    # ==================================================

    def _modules(self):


        return [

            PerformanceMetricsEngine,

            ReliabilityMetricsEngine,

            RiskMetricsEngine,

            ExitMetricsEngine,

            EfficiencyMetricsEngine,

            OpportunityMetricsEngine

        ]





    # ==================================================
    # TRACK GENERATED COLUMNS
    # ==================================================

    def _track_columns(

        self,

        before,

        after

    ):


        generated = sorted(

            list(

                set(after)

                -

                set(before)

            )

        )


        self.generated_metrics.extend(

            generated

        )


        return generated





    # ==================================================
    # RUN ENGINE
    # ==================================================

    def run(self):


        logger.info("=" * 80)


        logger.info(

            "Starting Derived Metrics Engine..."

        )


        start = time.perf_counter()



        # ==================================================
        # STEP 1
        # TRADE LEVEL -> STRATEGY LEVEL
        # ==================================================


        logger.info(

            "Running Trade Metrics Engine..."

        )


        self.df = TradeMetricsEngine(

            self.df

        ).generate()



        logger.info(

            "Trade level aggregation completed."

        )




        # ==================================================
        # STEP 2
        # DERIVED METRIC MODULES
        # ==================================================


        for engine_class in self._modules():


            module_start = time.perf_counter()


            name = engine_class.__name__



            logger.info(

                "Running %s",

                name

            )



            before = (

                self.df.columns.tolist()

            )



            try:


                engine = engine_class(

                    self.df

                )



                self.df = engine.generate()



                after = (

                    self.df.columns.tolist()

                )



                generated = self._track_columns(

                    before,

                    after

                )



                self.module_summary.append({

                    "Module":

                        name,


                    "Status":

                        "Completed",


                    "Generated":

                        generated,


                    "Count":

                        len(generated),


                    "Execution Time":

                        round(

                            time.perf_counter()

                            -

                            module_start,

                            4

                        )

                })



                logger.info(

                    "%s generated %s",

                    name,

                    generated

                )



            except Exception as error:



                logger.exception(

                    "%s failed",

                    name

                )



                self.module_summary.append({

                    "Module":

                        name,


                    "Status":

                        "Failed",


                    "Error":

                        str(error)

                })



                raise






        # ==================================================
        # FINAL STATISTICAL ANALYSIS
        # ==================================================


        logger.info(

            "Generating Statistical Summary..."

        )



        statistics = StatisticalMetricsEngine(

            self.df

        ).generate()



        self.df.attrs["statistics"] = statistics




        # ==================================================
        # FINALIZE
        # ==================================================


        self.generated_metrics = sorted(

            set(

                self.generated_metrics

            )

        )



        self.execution_time = round(

            time.perf_counter()

            -

            start,

            3

        )



        logger.info(

            "Generated %d derived metrics",

            len(

                self.generated_metrics

            )

        )



        logger.info(

            "Derived Metrics completed in %.3f seconds",

            self.execution_time

        )


        logger.info("=" * 80)



        return self.df





    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self) -> Dict[str, Any]:


        return {


            "Execution Time":

                self.execution_time,


            "Generated Metrics":

                self.generated_metrics,


            "Total Metrics":

                len(

                    self.generated_metrics

                ),


            "Modules":

                self.module_summary

        }





    # ==================================================
    # ACCESSOR
    # ==================================================

    def get_dataframe(self):

        return self.df





if __name__ == "__main__":


    print(

        "Import DerivedMetricsEngine inside pipeline"

    )