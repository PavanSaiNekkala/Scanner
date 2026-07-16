"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/institutional_metrics.py

Production Institutional Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class InstitutionalMetricsEngine:
    """
    Institutional Feature Aggregation Engine.

    Uses previously generated features to create
    high-level institutional quality metrics.


    Input Features
    --------------
    Profitability Index
    Capital Efficiency
    Edge Ratio
    Trade Density
    Signal Quality
    Profit Consistency
    Stability Index
    Opportunity Density
    Execution Quality


    Generated Features
    ------------------
    Capital Productivity
    Edge Density
    Signal Robustness
    Strategy Robustness
    Execution Productivity
    Institutional Readiness
    Institutional Grade
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()

    # ==================================================
    # SAFE DIVIDE
    # ==================================================

    @staticmethod
    def safe_divide(a, b):

        return np.where(

            b == 0,

            np.nan,

            a / b

        )

    # ==================================================
    # CAPITAL PRODUCTIVITY
    # ==================================================

    def capital_productivity(self):

        required = {

            "Profitability Index",

            "Capital Efficiency"

        }


        if not required.issubset(
            self.df.columns
        ):

            logger.warning(
                "Capital Productivity skipped."
            )

            return


        self.df["Capital Productivity"] = (

            self.df["Profitability Index"]

            *

            self.df["Capital Efficiency"]

        )

    # ==================================================
    # EDGE DENSITY
    # ==================================================

    def edge_density(self):

        required = {

            "Edge Ratio",

            "Trade Density"

        }


        if not required.issubset(
            self.df.columns
        ):

            logger.warning(
                "Edge Density skipped."
            )

            return


        self.df["Edge Density"] = (

            self.df["Edge Ratio"]

            *

            self.df["Trade Density"]

        )

    # ==================================================
    # SIGNAL ROBUSTNESS
    # ==================================================

    def signal_robustness(self):

        required = {

            "Signal Quality",

            "Profit Consistency"

        }


        if not required.issubset(
            self.df.columns
        ):

            return


        self.df["Signal Robustness"] = (

            self.df["Signal Quality"]

            *

            self.df["Profit Consistency"]

        )

    # ==================================================
    # STRATEGY ROBUSTNESS
    # ==================================================

    def strategy_robustness(self):

        required = {

            "Stability Index",

            "Profitability Index"

        }


        if not required.issubset(
            self.df.columns
        ):

            return


        self.df["Strategy Robustness"] = (

            self.df["Stability Index"]

            *

            self.df["Profitability Index"]

        )

    # ==================================================
    # EXECUTION PRODUCTIVITY
    # ==================================================

    def execution_productivity(self):

        required = {

            "Execution Quality",

            "Opportunity Density"

        }


        if not required.issubset(
            self.df.columns
        ):

            return


        self.df["Execution Productivity"] = (

            self.df["Execution Quality"]

            *

            self.df["Opportunity Density"]

        )

    # ==================================================
    # INSTITUTIONAL READINESS
    # ==================================================

    def institutional_readiness(self):

        required = {

            "Capital Productivity",

            "Edge Density",

            "Strategy Robustness",

            "Execution Productivity"

        }


        if not required.issubset(
            self.df.columns
        ):

            logger.warning(
                "Institutional Readiness skipped."
            )

            return


        self.df["Institutional Readiness"] = (

            self.df["Capital Productivity"]

            +

            self.df["Edge Density"]

            +

            self.df["Strategy Robustness"]

            +

            self.df["Execution Productivity"]

        ) / 4


    # ==================================================
    # INSTITUTIONAL GRADE
    # ==================================================

    def institutional_grade(self):

        if (
            "Institutional Readiness"
            not in
            self.df.columns
        ):

            return


        score = self.df[
            "Institutional Readiness"
        ]


        conditions = [

            score >= 90,

            score >= 75,

            score >= 60,

            score >= 40

        ]


        choices = [

            "Institutional",

            "Professional",

            "Advanced",

            "Intermediate"

        ]


        self.df["Institutional Grade"] = np.select(

            conditions,

            choices,

            default="Basic"

        )

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):

        logger.info(

            "Generating Institutional Metrics..."

        )


        self.capital_productivity()

        self.edge_density()

        self.signal_robustness()

        self.strategy_robustness()

        self.execution_productivity()

        self.institutional_readiness()

        self.institutional_grade()


        logger.info(

            "Institutional metrics completed."

        )


        return self.df


if __name__ == "__main__":

    print(
        "Import InstitutionalMetricsEngine inside feature_engine.py"
    )