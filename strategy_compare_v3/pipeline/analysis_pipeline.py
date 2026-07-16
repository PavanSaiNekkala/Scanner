"""
============================================================
Institutional Strategy Comparison Engine V3

Master Analysis Pipeline

Author : Pavan Sai

============================================================
"""

from __future__ import annotations


import time

from typing import Dict, Any


import pandas as pd


from core.logger import get_logger


from profiling.profiler import DataProfiler


from relationships.relationship_engine import RelationshipEngine


from derived_metrics.derived_metrics_engine import (
    DerivedMetricsEngine
)


from feature_engineering.feature_engine import FeatureEngine


from normalization.normalization_engine import (
    NormalizationEngine
)


from scoring.scoring_engine import (
    ScoringEngine
)


from recommendation.recommendation_engine import (
    RecommendationEngine
)


from optimization.optimization_engine import (
    OptimizationEngine
)


from visualization.dashboards import (
    DashboardEngine
)


from reports.report_engine import (
    ReportEngine
)



logger = get_logger(__name__)




class AnalysisPipeline:
    """
    Master Institutional Pipeline.

    Execution Flow

    Raw Backtest Data

            |

    Profiling

            |

    Relationships

            |

    Derived Metrics

            |

    Feature Engineering

            |

    Normalization

            |

    Scoring

            |

    Recommendation

            |

    Optimization

            |

    Reports

    """



    def __init__(

        self,

        dataframe: pd.DataFrame,

        config: dict | None = None

    ):


        self.raw_df = dataframe.copy()


        self.df = dataframe.copy()


        self.config = config or {}


        self.results: Dict[str, Any] = {}


        self.execution_time = 0.0



    # ==================================================
    # PROFILING
    # ==================================================

    def profile(self):


        logger.info(

            "Profiling..."

        )


        return DataProfiler(

            self.df

        ).generate()



    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    def relationships(self):


        logger.info(

            "Relationship Analysis..."

        )


        return RelationshipEngine(

            self.df

        ).generate()



    # ==================================================
    # DERIVED METRICS
    # ==================================================

    def derived_metrics(self):


        logger.info(

            "Derived Metrics..."

        )


        derived_df = DerivedMetricsEngine(

            self.df

        ).run()



        return derived_df



    # ==================================================
    # FEATURE ENGINEERING
    # ==================================================

    def features(

        self,

        dataframe

    ):


        logger.info(

            "Feature Engineering..."

        )


        return FeatureEngine(

            dataframe

        ).run()



    # ==================================================
    # NORMALIZATION
    # ==================================================

    def normalize(

        self,

        dataframe

    ):


        logger.info(

            "Normalization..."

        )


        return NormalizationEngine(

            dataframe

        ).run()



    # ==================================================
    # SCORING
    # ==================================================

    def scoring(

        self,

        dataframe

    ):


        logger.info(

            "Scoring..."

        )


        return ScoringEngine(

            dataframe

        ).run()



    # ==================================================
    # RECOMMENDATION
    # ==================================================

    def recommendation(

        self,

        dataframe

    ):


        logger.info(

            "Recommendations..."

        )


        return RecommendationEngine(

            dataframe

        ).generate()



    # ==================================================
    # OPTIMIZATION
    # ==================================================

    def optimization(

        self,

        dataframe

    ):


        logger.info(

            "Optimization..."

        )


        def objective(df):


            return df[

                "Composite Score"

            ].mean()



        parameter_space = {


            "Edge Weight":

                [

                    0.10,

                    0.15,

                    0.20

                ],


            "Risk Weight":

                [

                    0.10,

                    0.20

                ]

        }



        scenarios = {


            "Baseline":

                lambda x: x

        }



        return OptimizationEngine(

            dataframe,

            objective

        ).run(

            parameter_space,

            scenarios

        )



    # ==================================================
    # VISUALIZATION
    # ==================================================

    def visualization(

        self,

        dataframe

    ):


        logger.info(

            "Visualization..."

        )


        return DashboardEngine(

            dataframe

        ).run()



    # ==================================================
    # REPORTS
    # ==================================================

    def reports(

        self,

        dataframe

    ):


        logger.info(

            "Reports..."

        )


        return ReportEngine(

            dataframe

        ).run()



    # ==================================================
    # MASTER RUNNER
    # ==================================================

    def run(self):


        logger.info("=" * 80)


        logger.info(

            "Starting Analysis Pipeline..."

        )


        start = time.perf_counter()



        # ----------------------------------------------
        # Profiling
        # ----------------------------------------------

        self.results["Profiling"] = (

            self.profile()

        )



        # ----------------------------------------------
        # Relationships
        # ----------------------------------------------

        self.results["Relationships"] = (

            self.relationships()

        )



        # ----------------------------------------------
        # Derived Metrics
        # ----------------------------------------------

        derived = self.derived_metrics()


        self.results["Derived Metrics"] = derived



        # ----------------------------------------------
        # Feature Engineering
        # ----------------------------------------------

        features = self.features(

            derived

        )


        self.results["Features"] = features



        # ----------------------------------------------
        # Normalization
        # ----------------------------------------------

        normalized = self.normalize(

            features

        )


        self.results["Normalization"] = normalized



        analysis_df = normalized[

            "Percentile"

        ]



        # ----------------------------------------------
        # Scoring
        # ----------------------------------------------

        scored = self.scoring(

            analysis_df

        )


        self.results["Scoring"] = scored



        # ----------------------------------------------
        # Recommendation
        # ----------------------------------------------

        recommended = self.recommendation(

            scored

        )


        self.results["Recommendation"] = recommended



        # ----------------------------------------------
        # Optimization
        # ----------------------------------------------

        self.results["Optimization"] = (

            self.optimization(

                recommended

            )

        )



        # ----------------------------------------------
        # Visualization
        # ----------------------------------------------

        self.results["Visualization"] = (

            self.visualization(

                recommended

            )

        )



        # ----------------------------------------------
        # Reports
        # ----------------------------------------------

        self.results["Reports"] = (

            self.reports(

                recommended

            )

        )



        self.execution_time = round(

            time.perf_counter()

            -

            start,

            3

        )



        self.results["Execution Time"] = (

            self.execution_time

        )



        logger.info(

            "Pipeline completed in %.3f seconds.",

            self.execution_time

        )


        logger.info("=" * 80)



        return self.results




    def summary(self):


        return {


            "Pipeline":

                "Completed",


            "Execution Time":

                self.execution_time,


            "Modules":

                list(

                    self.results.keys()

                )

        }




if __name__ == "__main__":


    print(

        "Import inside main.py"

    )