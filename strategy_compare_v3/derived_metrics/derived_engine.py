"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/derived_engine.py

Master Derived Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import pandas as pd


from core.logger import get_logger


from derived_metrics.performance_metrics import (
    PerformanceMetricsEngine
)


from derived_metrics.risk_metrics import (
    RiskMetricsEngine
)


from derived_metrics.reliability_metrics import (
    ReliabilityMetricsEngine
)


from derived_metrics.efficiency_metrics import (
    EfficiencyMetricsEngine
)


from derived_metrics.exit_metrics import (
    ExitMetricsEngine
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
    Master Derived Metrics Orchestrator.

    Converts raw backtest trade data into
    strategy-level derived metrics.

    Pipeline:

    Raw Trades

        |

    Performance Metrics

        |

    Risk Metrics

        |

    Reliability Metrics

        |

    Efficiency Metrics

        |

    Exit Metrics

        |

    Opportunity Metrics

        |

    Statistical Metrics

        |

    Strategy Summary DataFrame

    """



    def __init__(

        self,

        dataframe: pd.DataFrame

    ):


        self.df = dataframe.copy()


        self.results = {}



    # ==================================================
    # RUN ALL DERIVED MODULES
    # ==================================================

    def run(self):


        logger.info(

            "Starting Derived Metrics Engine..."

        )



        modules = [


            PerformanceMetricsEngine,


            RiskMetricsEngine,


            ReliabilityMetricsEngine,


            EfficiencyMetricsEngine,


            ExitMetricsEngine,


            OpportunityMetricsEngine,


            StatisticalMetricsEngine

        ]



        for module in modules:


            logger.info(

                "Running %s",

                module.__name__

            )



            output = module(

                self.df

            ).generate()



            if isinstance(

                output,

                dict

            ):


                self.results.update(

                    output

                )


            elif isinstance(

                output,

                pd.DataFrame

            ):


                self.results.update(

                    output.iloc[0].to_dict()

                )



            else:


                logger.warning(

                    "%s returned unsupported type: %s",

                    module.__name__,

                    type(output)

                )



        summary = pd.DataFrame(

            [

                self.results

            ]

        )



        logger.info(

            "Derived Metrics completed."

        )


        logger.info(

            "Generated %d derived metrics.",

            len(summary.columns)

        )



        return summary



    # ==================================================
    # SUMMARY
    # ==================================================

    def get_summary(self):


        return self.results





if __name__ == "__main__":


    print(

        "Import DerivedMetricsEngine inside analysis_pipeline.py"

    )