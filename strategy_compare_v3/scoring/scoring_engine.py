"""
============================================================
Institutional Strategy Comparison Engine V3

File : scoring/scoring_engine.py

Master Scoring Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time


import pandas as pd


from core.logger import get_logger
from core.cache import CacheManager


from scoring.edge_score import EdgeScoreEngine
from scoring.risk_score import RiskScoreEngine
from scoring.efficiency_score import EfficiencyScoreEngine
from scoring.stability_score import StabilityScoreEngine
from scoring.reliability_score import ReliabilityScoreEngine
from scoring.opportunity_score import OpportunityScoreEngine
from scoring.execution_score import ExecutionScoreEngine

from scoring.institutional_score import InstitutionalScoreEngine
from scoring.composite_score import CompositeScoreEngine

logger = get_logger(__name__)


class ScoringEngine:
    """
    Master Institutional Scoring Pipeline.

    Pipeline:

    Feature Engineering
            |
            |
    Edge Score
            |
    Risk Score
            |
    Efficiency Score
            |
    Stability Score
            |
    Reliability Score
            |
    Opportunity Score
            |
    Execution Score
            |
    Institutional Score
            |
    Composite Score
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        use_cache: bool = False,
    ):
        self.df = dataframe.copy()

        self.use_cache = use_cache

        self.cache = CacheManager()

        self.execution_time = 0.0

        self.generated_scores = []

        self.module_summary = []

    # ==================================================
    # NORMALIZE INPUT CONTRACT
    # ==================================================

    def _normalize_scoring_columns(self):
        mapping = {
            "ExpectancyPct": "Expectancy%",
            "Profit_Factor": "Profit Factor",
            "Reward_Risk_Ratio": "Reward Risk Ratio",
            "Win_Pct": "Win %",
            "Edge_Ratio": "Edge Ratio",
        }

        created = []

        for source, target in mapping.items():
            if source in self.df.columns and target not in self.df.columns:
                self.df[target] = self.df[source]

                created.append(target)

        logger.info("Scoring contract created: %s", created)

    # ==================================================
    # VALIDATION
    # ==================================================

    def _validate_scoring_inputs(self):
        required = [
            "Expectancy%",
            "Profit Factor",
            "Reward Risk Ratio",
            "Win %",
            "Edge Ratio",
        ]

        missing = [c for c in required if c not in self.df.columns]

        if missing:
            raise ValueError(f"Missing scoring columns: {missing}")

        logger.info("Scoring input validation successful.")

    # ==================================================
    # MERGE
    # ==================================================

    @staticmethod
    def _merge_score(dataframe, score_df):
        if score_df is None:
            return dataframe

        if score_df.empty:
            return dataframe

        duplicate = [c for c in score_df.columns if c in dataframe.columns]

        if duplicate:
            score_df = score_df.drop(columns=duplicate)

        # ==================================================
        # REMOVE PANDAS METADATA BEFORE CONCAT
        # ==================================================

        dataframe = dataframe.copy()

        score_df = score_df.copy()

        dataframe.attrs = {}

        score_df.attrs = {}

        return pd.concat([dataframe, score_df], axis=1, ignore_index=False)

    # ==================================================
    # MODULE LIST
    # ==================================================

    def _score_modules(self):
        return [
            EdgeScoreEngine,
            RiskScoreEngine,
            EfficiencyScoreEngine,
            StabilityScoreEngine,
            ReliabilityScoreEngine,
            OpportunityScoreEngine,
            ExecutionScoreEngine,
        ]

    # ==================================================
    # RUN
    # ==================================================

    def run(self):
        logger.info("=" * 80)

        logger.info("Starting Scoring Engine...")

        start = time.perf_counter()

        self._normalize_scoring_columns()

        self._validate_scoring_inputs()

        for engine_class in self._score_modules():
            module_start = time.perf_counter()

            name = engine_class.__name__

            logger.info("Running %s", name)

            before = set(self.df.columns)

            try:
                result = engine_class(self.df).generate()

                self.df = self._merge_score(self.df, result)

                after = set(self.df.columns)

                generated = sorted(after - before)

                self.generated_scores.extend(generated)

                self.module_summary.append(
                    {
                        "Module": name,
                        "Status": "Completed",
                        "Generated": generated,
                        "Time": round(time.perf_counter() - module_start, 4),
                    }
                )

                logger.info("%s generated %s", name, generated)

            except Exception as error:
                logger.exception("%s failed", name)

                self.module_summary.append(
                    {"Module": name, "Status": "Failed", "Error": str(error)}
                )

                raise

        # ==================================================
        # CHECK INSTITUTIONAL DEPENDENCIES
        # ==================================================

        institutional_required = [
            "Risk Score",
            "Efficiency Score",
            "Opportunity Score",
            "Execution Score",
        ]

        missing = [c for c in institutional_required if c not in self.df.columns]

        if missing:
            raise ValueError(f"Institutional score dependency missing: {missing}")

        institutional = InstitutionalScoreEngine(self.df).generate()

        self.df = self._merge_score(self.df, institutional)

        composite = CompositeScoreEngine(self.df).generate()

        self.df = self._merge_score(self.df, composite)

        self.execution_time = round(time.perf_counter() - start, 3)

        self.generated_scores = sorted(set(self.generated_scores))

        logger.info("Scoring completed in %.3f seconds", self.execution_time)

        logger.info("=" * 80)

        return self.df

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):
        return {
            "Execution Time": self.execution_time,
            "Generated Scores": self.generated_scores,
            "Total Scores": len(self.generated_scores),
            "Modules": self.module_summary,
        }

    def get_dataframe(self):
        return self.df


if __name__ == "__main__":
    print("Import ScoringEngine inside main.py")
