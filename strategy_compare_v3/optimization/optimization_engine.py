"""
============================================================
Institutional Strategy Comparison Engine V3
File : optimization/optimization_engine.py

Master Optimization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time
from typing import Callable, Dict, Any

import pandas as pd

from core.logger import get_logger

from optimization.parameter_optimizer import (
    ParameterOptimizer,
)

from optimization.sensitivity_analysis import (
    SensitivityAnalysis,
)

from optimization.monte_carlo import (
    MonteCarloSimulation,
)

from optimization.robustness import (
    RobustnessAnalysis,
)

logger = get_logger(__name__)


class OptimizationEngine:
    """
    Master Optimization Engine.

    Executes every optimization module
    and returns a unified report.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        objective_function: Callable,
    ):

        self.df = dataframe.copy()

        self.objective_function = objective_function

        self.execution_time = 0.0

        self.results: Dict[str, Any] = {}

    # --------------------------------------------------

    def parameter_optimization(
        self,
        parameter_space: dict
    ):

        optimizer = ParameterOptimizer(

            self.df,

            target_column="Composite Score"

        )

        return optimizer.optimize(

            parameter_space

        )

    # --------------------------------------------------

    def sensitivity_analysis(
        self,
        parameter_space: dict
    ):

        analyser = SensitivityAnalysis(

            self.df,

            self.objective_function

        )

        return analyser.analyse_multiple(

            parameter_space

        )

    # --------------------------------------------------

    def monte_carlo(
        self,
        simulations: int = 1000,
        noise_level: float = 0.05
    ):

        simulator = MonteCarloSimulation(

            dataframe=self.df,

            objective_function=self.objective_function,

            simulations=simulations,

            noise_level=noise_level,

        )

        return simulator.run()

    # --------------------------------------------------

    def robustness(
        self,
        scenarios: dict
    ):

        robustness = RobustnessAnalysis(

            self.df,

            self.objective_function

        )

        return robustness.run(

            scenarios

        )

    # --------------------------------------------------

    def run(

        self,

        parameter_space: dict,

        scenarios: dict,

        simulations: int = 1000,

        noise_level: float = 0.05,

    ):

        logger.info("=" * 80)

        logger.info(

            "Starting Optimization Engine..."

        )

        start = time.perf_counter()

        self.results["Parameter Optimization"] = (

            self.parameter_optimization(

                parameter_space

            )

        )

        self.results["Sensitivity Analysis"] = (

            self.sensitivity_analysis(

                parameter_space

            )

        )

        self.results["Monte Carlo"] = (

            self.monte_carlo(

                simulations,

                noise_level

            )

        )

        self.results["Robustness"] = (

            self.robustness(

                scenarios

            )

        )

        self.execution_time = round(

            time.perf_counter()

            - start,

            3

        )

        self.results["Execution Time"] = (

            self.execution_time

        )

        logger.info(

            "Optimization completed in %.3f seconds.",

            self.execution_time

        )

        logger.info("=" * 80)

        return self.results

    # --------------------------------------------------

    def summary(self):

        return {

            "Modules": [

                "Parameter Optimization",

                "Sensitivity Analysis",

                "Monte Carlo",

                "Robustness"

            ],

            "Execution Time":

                self.execution_time

        }


if __name__ == "__main__":

    print(

        "Import inside main.py"

    )