"""
============================================================
Institutional Strategy Comparison Engine V3
File : optimization/sensitivity_analysis.py

Sensitivity Analysis Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class SensitivityAnalysis:
    """
    Institutional Sensitivity Analysis.

    Measures how sensitive the objective
    function is to parameter changes.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        objective_function: Callable,
    ):

        self.df = dataframe.copy()

        self.objective_function = objective_function

    # -----------------------------------------------------

    def analyse_parameter(
        self,
        parameter_name: str,
        values: list,
    ) -> pd.DataFrame:

        logger.info(

            "Analysing parameter: %s",

            parameter_name

        )

        results = []

        for value in values:

            score = self.objective_function(

                self.df,

                {

                    parameter_name: value

                }

            )

            results.append({

                "Parameter":

                    parameter_name,

                "Value":

                    value,

                "Objective":

                    score

            })

        return pd.DataFrame(results)

    # -----------------------------------------------------

    def analyse_multiple(
        self,
        parameter_space: dict
    ) -> pd.DataFrame:

        logger.info(

            "Running sensitivity analysis..."

        )

        frames = []

        for parameter, values in parameter_space.items():

            frames.append(

                self.analyse_parameter(

                    parameter,

                    values

                )

            )

        results = pd.concat(

            frames,

            ignore_index=True

        )

        logger.info(

            "Sensitivity analysis completed."

        )

        return results

    # -----------------------------------------------------

    def ranking(
        self,
        sensitivity_df: pd.DataFrame
    ) -> pd.DataFrame:

        grouped = (

            sensitivity_df

            .groupby("Parameter")["Objective"]

            .agg(

                Mean="mean",

                Std="std",

                Min="min",

                Max="max"

            )

            .reset_index()

        )

        grouped["Sensitivity"] = (

            grouped["Max"]

            -

            grouped["Min"]

        )

        grouped = grouped.sort_values(

            "Sensitivity",

            ascending=False

        )

        return grouped.reset_index(

            drop=True

        )


if __name__ == "__main__":

    print(

        "Import inside optimization_engine.py"

    )