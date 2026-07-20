"""
============================================================
Institutional Strategy Comparison Engine V3

File : feature_engineering/feature_engine.py

Production Grade Master Feature Engineering Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time

from typing import Dict, Any

import pandas as pd


from core.cache import CacheManager
from core.logger import get_logger
from core.feature_contract import FeatureContract


from feature_engineering.reward_risk import RewardRiskEngine

from feature_engineering.expectancy import ExpectancyEngine

from feature_engineering.profitability import ProfitabilityEngine

from feature_engineering.efficiency import EfficiencyEngine

from feature_engineering.stability import StabilityEngine

from feature_engineering.quality import QualityEngine

from feature_engineering.opportunity import OpportunityEngine

from feature_engineering.institutional_metrics import InstitutionalMetricsEngine

logger = get_logger(__name__)


class FeatureEngine:
    """
    Master Feature Engineering Pipeline.

    Responsibilities
    ----------------
    ✓ Apply feature contract
    ✓ Execute feature modules
    ✓ Track generated features
    ✓ Capture execution metrics
    ✓ Preserve dataframe integrity
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

        self.feature_count = 0

        self.generated_features = []

        self.module_summary = []

    # ==================================================
    # MODULE LIST
    # ==================================================

    def _modules(self):
        return [
            RewardRiskEngine,
            ExpectancyEngine,
            ProfitabilityEngine,
            EfficiencyEngine,
            StabilityEngine,
            QualityEngine,
            OpportunityEngine,
            InstitutionalMetricsEngine,
        ]

    # ==================================================
    # TRACK GENERATED FEATURES
    # ==================================================

    def _track_features(self, before, after):
        generated = sorted(list(set(after) - set(before)))

        self.generated_features.extend(generated)

        return generated

    # ==================================================
    # VALIDATION
    # ==================================================

    def _validate_input(self):
        if self.df.empty:
            raise ValueError("Feature Engine received empty dataframe.")

        logger.info("Feature Engine input shape: %s", self.df.shape)

    # ==================================================
    # RUN
    # ==================================================

    def run(self):
        logger.info("=" * 80)

        logger.info("Starting Feature Engineering...")

        start = time.perf_counter()

        # ------------------------------------------------
        # Apply centralized contract
        # ------------------------------------------------

        self.df = FeatureContract.normalize(self.df)

        self._validate_input()

        # ------------------------------------------------
        # Execute modules
        # ------------------------------------------------

        for module in self._modules():
            module_start = time.perf_counter()

            name = module.__name__

            before = self.df.columns.tolist()

            logger.info("Running %s", name)

            try:
                engine = module(self.df)

                self.df = engine.generate()

                after = self.df.columns.tolist()

                generated = self._track_features(before, after)

                elapsed = round(time.perf_counter() - module_start, 4)

                self.module_summary.append(
                    {
                        "Module": name,
                        "Status": "Completed",
                        "Generated": generated,
                        "Count": len(generated),
                        "Time": elapsed,
                    }
                )

                logger.info("%s generated %d features", name, len(generated))

            except Exception as error:
                logger.exception("%s failed: %s", name, error)

                self.module_summary.append(
                    {"Module": name, "Status": "Failed", "Error": str(error)}
                )

        # ------------------------------------------------
        # Finalize
        # ------------------------------------------------

        self.generated_features = sorted(set(self.generated_features))

        self.feature_count = len(self.generated_features)

        self.execution_time = round(time.perf_counter() - start, 3)

        logger.info("Generated %d engineered features", self.feature_count)

        logger.info(
            "Feature Engineering completed in %.3f seconds", self.execution_time
        )

        logger.info("=" * 80)

        return self.df

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self) -> Dict[str, Any]:
        return {
            "Execution Time": self.execution_time,
            "Generated Features": self.feature_count,
            "Feature Names": self.generated_features,
            "Module Summary": self.module_summary,
        }

    # ==================================================
    # ACCESSOR
    # ==================================================

    def get_dataframe(self):
        return self.df


if __name__ == "__main__":
    print("Import FeatureEngine into main.py")
