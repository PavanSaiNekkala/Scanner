"""
============================================================
Institutional Strategy Comparison Engine V3
File : optimization/parameter_optimizer.py

Parameter Optimization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import itertools
from typing import Dict, List

import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class ParameterOptimizer:
    """
    Parameter Optimization Engine.

    Performs grid-search style optimization
    over configurable parameter ranges.

    Intended for optimizing:

    • Score weights
    • Recommendation thresholds
    • Strategy parameters
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
    ):
        self.df = dataframe.copy()

        self.target_column = target_column

    # -----------------------------------------------------

    def validate(self):
        if self.target_column not in self.df.columns:
            raise ValueError(f"'{self.target_column}' not found.")

    # -----------------------------------------------------

    @staticmethod
    def parameter_grid(parameter_space: Dict[str, List]):
        keys = parameter_space.keys()

        values = parameter_space.values()

        for combination in itertools.product(*values):
            yield dict(zip(keys, combination))

    # -----------------------------------------------------

    def evaluate(self, parameters: Dict) -> float:
        """
        Override this method for
        custom optimization logic.

        Current implementation
        simply returns the mean
        of the target column.
        """

        return float(self.df[self.target_column].mean())

    # -----------------------------------------------------

    def optimize(self, parameter_space: Dict[str, List]) -> pd.DataFrame:
        logger.info("Starting parameter optimization...")

        self.validate()

        results = []

        for params in self.parameter_grid(parameter_space):
            score = self.evaluate(params)

            results.append({**params, "Objective": score})

        results = pd.DataFrame(results)

        results = results.sort_values("Objective", ascending=False).reset_index(
            drop=True
        )

        logger.info("Parameter optimization completed.")

        return results


if __name__ == "__main__":
    print("Import inside optimization_engine.py")
