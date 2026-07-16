"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/quality.py

Quality Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class QualityEngine:
    """
    Quality Feature Engineering.

    Expected Columns
    ----------------
    Win %
    Profit Factor
    Expectancy%
    Reward Risk Ratio
    Trades
    Avg days
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

    # -----------------------------------------------------

    @staticmethod
    def safe_divide(a, b):

        return np.where(
            b == 0,
            np.nan,
            a / b
        )

    # -----------------------------------------------------

    def trade_quality(self):

        required = {

            "Trades",

            "Win %"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Trade Quality"] = self.safe_divide(

            self.df["Win %"],

            self.df["Trades"]

        )

    # -----------------------------------------------------

    def profit_quality(self):

        required = {

            "Profit Factor",

            "Reward Risk Ratio"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Profit Quality"] = (

            self.df["Profit Factor"]

            *

            self.df["Reward Risk Ratio"]

        )

    # -----------------------------------------------------

    def expectancy_quality(self):

        required = {

            "Expectancy%",

            "Reward Risk Ratio"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Expectancy Quality"] = (

            self.df["Expectancy%"]

            *

            self.df["Reward Risk Ratio"]

        )

    # -----------------------------------------------------

    def execution_quality(self):

        required = {

            "Win %",

            "Avg days"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Execution Quality"] = self.safe_divide(

            self.df["Win %"],

            self.df["Avg days"]

        )

        self.df["Execution Quality"] = (
            self.df["Holding Efficiency"]
            *
            self.df["Edge Ratio"]
        )

    # -----------------------------------------------------

    def signal_quality(self):

        required = {

            "Trades",

            "Profit Factor"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Signal Quality"] = self.safe_divide(

            self.df["Profit Factor"],

            self.df["Trades"]

        )

    # -----------------------------------------------------

    def holding_quality(self):

        required = {

            "Avg days",

            "Trades"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Holding Quality"] = self.safe_divide(

            self.df["Avg days"],

            self.df["Trades"]

        )

    # -----------------------------------------------------

    def generate(self):

        logger.info(

            "Generating Quality Features..."

        )

        self.trade_quality()

        self.profit_quality()

        self.expectancy_quality()

        self.execution_quality()

        self.signal_quality()

        self.holding_quality()

        logger.info(

            "Quality feature engineering completed."

        )

        return self.df


if __name__ == "__main__":

    print(

        "Import inside feature_engine.py"

    )