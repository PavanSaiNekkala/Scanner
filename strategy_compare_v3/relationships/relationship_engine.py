"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/relationship_engine.py

Production Grade Relationship Analysis Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time
from typing import Any, Dict

import pandas as pd

from core.cache import CacheManager
from core.logger import get_logger

from relationships.correlation import CorrelationEngine
from relationships.dependency_matrix import DependencyMatrix
from relationships.multicollinearity import Multicollinearity
from relationships.feature_selection import FeatureSelection
from relationships.dimensionality_reduction import (
    DimensionalityReduction,
)

logger = get_logger(__name__)


class RelationshipEngine:
    """
    =========================================================

    Master Relationship Analysis Engine

    Performs

        ✓ Correlation Analysis

        ✓ Dependency Matrix

        ✓ Multicollinearity Detection

        ✓ Dimensionality Reduction

        ✓ Feature Selection (Optional)

    =========================================================
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        target: str | None = None,
        use_cache: bool = False,
    ):
        self.df = dataframe.copy()

        self.target = target

        self.use_cache = use_cache

        self.cache = CacheManager()

        self.results: Dict[str, Any] = {}

    # ======================================================

    def validate(self):
        if self.df is None:
            raise ValueError("Input dataframe is None.")

        if self.df.empty:
            raise ValueError("Input dataframe is empty.")

        numeric = self.df.select_dtypes(include="number")

        if numeric.empty:
            raise ValueError("No numeric columns found.")

        if self.target is not None:
            if self.target not in self.df.columns:
                raise ValueError(f"Target column '{self.target}' not found.")

    # ======================================================

    def run(self):
        logger.info("=" * 80)

        logger.info("Starting Relationship Engine...")

        self.validate()

        start = time.perf_counter()

        # --------------------------------------------------
        # Correlation
        # --------------------------------------------------

        logger.info("Running Correlation Engine...")

        correlation = CorrelationEngine(self.df).generate()

        # --------------------------------------------------
        # Dependency Matrix
        # --------------------------------------------------

        logger.info("Running Dependency Matrix...")

        dependency = DependencyMatrix(self.df).generate()

        # --------------------------------------------------
        # Multicollinearity
        # --------------------------------------------------

        logger.info("Running Multicollinearity...")

        multicollinearity = Multicollinearity(self.df).generate()

        # --------------------------------------------------
        # Feature Selection
        # --------------------------------------------------

        if self.target is not None:
            logger.info("Running Feature Selection...")

            feature_selection = FeatureSelection(self.df, target=self.target).generate()

        else:
            logger.info("Skipping Feature Selection (No target column provided).")

            feature_selection = pd.DataFrame(
                {"Information": ["Skipped"], "Reason": ["No target column supplied."]}
            )

        # --------------------------------------------------
        # Dimensionality Reduction
        # --------------------------------------------------

        logger.info("Running PCA...")

        dimensionality = DimensionalityReduction(self.df).generate()

        # --------------------------------------------------

        elapsed = round(time.perf_counter() - start, 3)

        self.results = {
            "Correlation": correlation,
            "Dependency": dependency,
            "Multicollinearity": multicollinearity,
            "Feature Selection": feature_selection,
            "Dimensionality Reduction": dimensionality,
            "Execution Time (sec)": elapsed,
        }

        logger.info("Relationship Engine completed in %.3f seconds.", elapsed)

        logger.info("=" * 80)

        return self.results

    # ======================================================

    def get_report(self, name: str):
        return self.results.get(name)

    # ======================================================

    def report_names(self):
        return list(self.results.keys())

    # ==================================================
    # PIPELINE COMPATIBILITY WRAPPER
    # ==================================================

    def generate(self):
        """
        Standard interface wrapper.

        AnalysisPipeline expects
        RelationshipEngine.generate()

        Existing implementation uses run()
        """

        return self.run()


if __name__ == "__main__":
    print("Import RelationshipEngine from main.py")
