"""
============================================================
Institutional Strategy Comparison Engine V3
File : optimization/monte_carlo.py

Monte Carlo Simulation Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class MonteCarloSimulation:
    """
    Institutional Monte Carlo Simulation.

    Simulates uncertainty in the scoring model
    by repeatedly perturbing numeric inputs.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        objective_function: Callable,
        simulations: int = 1000,
        noise_level: float = 0.05,
        random_state: int = 42,
    ):

        self.df = dataframe.copy()

        self.objective_function = objective_function

        self.simulations = simulations

        self.noise_level = noise_level

        self.random_state = random_state

        np.random.seed(random_state)

    # -----------------------------------------------------

    def perturb_data(self):

        """
        Apply Gaussian noise to numeric columns.
        """

        simulated = self.df.copy()

        numeric = simulated.select_dtypes(

            include=np.number

        ).columns

        for column in numeric:

            std = simulated[column].std()

            noise = np.random.normal(

                0,

                std * self.noise_level,

                len(simulated)

            )

            simulated[column] += noise

        return simulated

    # -----------------------------------------------------

    def run(self):

        logger.info(

            "Running Monte Carlo Simulation..."

        )

        results = []

        for simulation in range(

            self.simulations

        ):

            simulated = self.perturb_data()

            score = self.objective_function(

                simulated

            )

            results.append(

                score

            )

        results = np.asarray(results)

        summary = pd.DataFrame({

            "Metric": [

                "Mean",

                "Median",

                "Std",

                "Minimum",

                "Maximum",

                "5th Percentile",

                "95th Percentile"

            ],

            "Value": [

                results.mean(),

                np.median(results),

                results.std(),

                results.min(),

                results.max(),

                np.percentile(results, 5),

                np.percentile(results, 95)

            ]

        })

        logger.info(

            "Monte Carlo completed."

        )

        return {

            "Simulation Results":

                results,

            "Summary":

                summary

        }

    # -----------------------------------------------------

    def confidence_interval(

        self,

        results: np.ndarray,

        confidence: float = 95

    ):

        alpha = (

            100 - confidence

        ) / 2

        return (

            np.percentile(

                results,

                alpha

            ),

            np.percentile(

                results,

                100 - alpha

            )

        )


if __name__ == "__main__":

    print(

        "Import inside optimization_engine.py"

    )