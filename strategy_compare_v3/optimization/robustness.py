"""
============================================================
Institutional Strategy Comparison Engine V3
File : optimization/robustness.py

Robustness Analysis Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from typing import Callable, Dict

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class RobustnessAnalysis:
    """
    Institutional Robustness Analysis.

    Evaluates how stable a strategy remains
    under different stress scenarios.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        objective_function: Callable,
    ):
        self.df = dataframe.copy()

        self.objective_function = objective_function

    # --------------------------------------------------

    def run_scenario(
        self,
        scenario_name: str,
        transformation: Callable[[pd.DataFrame], pd.DataFrame],
    ) -> Dict:
        logger.info("Running scenario: %s", scenario_name)

        modified = transformation(self.df.copy())

        score = self.objective_function(modified)

        return {"Scenario": scenario_name, "Score": score}

    # --------------------------------------------------

    def run(self, scenarios: Dict[str, Callable]) -> pd.DataFrame:
        logger.info("Running Robustness Analysis...")

        results = []

        for name, transform in scenarios.items():
            results.append(self.run_scenario(name, transform))

        results = pd.DataFrame(results)

        baseline = results.iloc[0]["Score"]

        results["Deviation"] = results["Score"] - baseline

        results["Deviation %"] = results["Deviation"] / baseline * 100

        robustness = 100 - results["Deviation %"].abs().mean()

        results.attrs["Robustness Score"] = round(robustness, 2)

        logger.info("Robustness Score = %.2f", robustness)

        return results

    # --------------------------------------------------

    @staticmethod
    def summary(results: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Metric": ["Mean", "Std", "Minimum", "Maximum", "Robustness Score"],
                "Value": [
                    results["Score"].mean(),
                    results["Score"].std(),
                    results["Score"].min(),
                    results["Score"].max(),
                    results.attrs.get("Robustness Score", np.nan),
                ],
            }
        )


if __name__ == "__main__":
    print("Import inside optimization_engine.py")
