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

from feature_engineering.feature_engine import FeatureEngine

from derived_metrics.derived_engine import DerivedMetricsEngine


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

    Coordinates every engine.

    No calculations are performed here.

    Every calculation belongs to the
    respective module.
    """

    def __init__(

        self,

        dataframe: pd.DataFrame,

        config: dict | None = None

    ):

        self.df = dataframe.copy()

        self.config = config or {}

        self.results: Dict[str, Any] = {}

        self.execution_time = 0.0

    # --------------------------------------------------

    def profile(self):

        logger.info(

            "Profiling..."

        )

        return DataProfiler(

            self.df

        ).generate()

    # --------------------------------------------------

    def relationships(self):

        logger.info(

            "Relationship Analysis..."

        )

        return RelationshipEngine(

            self.df

        ).generate()


    # --------------------------------------------------
    # DERIVED METRICS
    # --------------------------------------------------

    def derived_metrics(self):

        logger.info(

            "Derived Metrics..."

        )

        self.df = DerivedMetricsEngine(

            self.df

        ).run()


        return self.df


    # --------------------------------------------------

    def features(self):

        logger.info(

            "Feature Engineering..."

        )

        return FeatureEngine(

            self.df

        ).run()
    
    # --------------------------------------------------

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

    # --------------------------------------------------

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

    # --------------------------------------------------

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

    # --------------------------------------------------

    def optimization(

        self,

        dataframe

    ):

        logger.info(

            "Optimization..."

        )

        def objective(

            df

        ):

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

    # --------------------------------------------------

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

    # --------------------------------------------------

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

    # --------------------------------------------------

    def run(self):

        logger.info("=" * 80)

        logger.info(

            "Starting Analysis Pipeline..."

        )

        start = time.perf_counter()


        # ----------------------------------------------
        # Optional Research Modules
        # ----------------------------------------------

        if self.config.get(

            "research_mode",

            False

        ):

            self.results["Profiling"] = (

                self.profile()

            )


            self.results["Relationships"] = (

                self.relationships()

            )

        # ----------------------------------------------
        # Derived Metrics

        derived = self.derived_metrics()

        self.results["Derived Metrics"] = derived


        # ----------------------------------------------
        # Feature Engineering

        features = self.features()

        self.results["Features"] = features

        # ----------------------------------------------
        normalized = self.normalize(

            features

        )

        self.results["Normalization"] = normalized



        # ==================================================
        # SCORING DATAFRAME
        # MERGE NORMALIZED FEATURES + ORIGINAL METRICS
        # ==================================================

        analysis_df = normalized["Percentile"].copy()



        scoring_columns = [

            "Expectancy%",

            "Profit Factor",

            "Reward Risk Ratio",

            "Win %",

            "Avg win%",

            "Avg loss%",

            "Trades",

            "Years",

        ]



        for column in scoring_columns:


            if column in self.df.columns:


                analysis_df[column] = self.df[column]

            else:


                logger.warning(

                    "Missing scoring column: %s",

                    column

                )


        logger.info(

            "Scoring dataframe columns: %s",

            analysis_df.columns.tolist()

        )

        required_scoring_columns = [

            "Expectancy%",

            "Profit Factor",

            "Reward Risk Ratio",

            "Win %",

            "Edge Ratio"

        ]


        missing = [

            col

            for col in required_scoring_columns

            if col not in analysis_df.columns

        ]


        if missing:

            raise ValueError(

                f"Missing scoring metrics: {missing}"

            )
        
        scored = self.scoring(

            analysis_df

        )

        self.results["Scoring"] = scored

        # ----------------------------------------------

        recommended = self.recommendation(

            scored

        )

        self.results["Recommendation"] = recommended

        # ----------------------------------------------

        self.results["Optimization"] = (

            self.optimization(

                recommended

            )

        )

        self.results["Visualization"] = (

            self.visualization(

                recommended

            )

        )

        self.results["Reports"] = (

            self.reports(

                recommended

            )

        )

        # ----------------------------------------------

        self.execution_time = round(

            time.perf_counter()

            - start,

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

    # --------------------------------------------------

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