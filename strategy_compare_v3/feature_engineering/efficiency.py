"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/efficiency.py

Efficiency Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class EfficiencyEngine:
    """
    Institutional Efficiency Feature Engineering.

    Expected Columns
    ----------------
    Expectancy%
    Trades
    Avg days
    Signals today
    Profit Factor
    Win %
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

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

    def expectancy_per_trade(self):

        required = {

            "Expectancy%",

            "Trades"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Expectancy Per Trade"] = self.safe_divide(

            self.df["Expectancy%"],

            self.df["Trades"]

        )

    # -----------------------------------------------------

    def expectancy_per_day(self):

        required = {

            "Expectancy%",

            "Avg days"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Expectancy Per Day"] = self.safe_divide(

            self.df["Expectancy%"],

            self.df["Avg days"]

        )

    # -----------------------------------------------------

    def trades_per_day(self):

        required = {

            "Trades",

            "Avg days"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Trades Per Day"] = self.safe_divide(

            self.df["Trades"],

            self.df["Avg days"]

        )

    # -----------------------------------------------------

    def profit_per_day(self):

        required = {

            "Profit Factor",

            "Avg days"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Profit Per Day"] = self.safe_divide(

            self.df["Profit Factor"],

            self.df["Avg days"]

        )

    # -----------------------------------------------------

    def signal_efficiency(self):

        required = {

            "Signals today",

            "Win %"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Signal Efficiency"] = self.safe_divide(

            self.df["Win %"],

            self.df["Signals today"]

        )

    # -----------------------------------------------------

    def capital_efficiency(self):

        required = {

            "Profit Factor",

            "Trades"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Capital Efficiency"] = self.safe_divide(

            self.df["Profit Factor"],

            self.df["Trades"]

        )


    def trade_efficiency(self):

        if "days_held" not in self.df.columns:

            return


        self.df["Trades Per Day"] = (

            1

            /

            self.df["days_held"].replace(

                0,

                np.nan

            )

        )


    def holding_efficiency(self):

        required = {

            "net_return_Pct",

            "days_held"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Holding Efficiency"] = (

            self.df["net_return_Pct"]

            /

            self.df["days_held"].replace(

                0,

                np.nan

            )

        )



    def capital_efficiency(self):

        required = {

            "net_return_Pct",

            "entry_price"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Capital Efficiency"] = (

            self.df["net_return_Pct"]

            /

            self.df["entry_price"]

        )

    # -----------------------------------------------------

    def holding_efficiency(self):

        required = {

            "Win %",

            "Avg days"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Holding Efficiency"] = self.safe_divide(

            self.df["Win %"],

            self.df["Avg days"]

        )

        self.df["Holding Efficiency"] = (
            self.df["net_return_Pct"]
            /
            self.df["days_held"].replace(
                0,
                np.nan
            )
        )

    # -----------------------------------------------------

    def efficiency_score(self):

        required = {

            "Expectancy Per Trade",

            "Profit Per Day",

            "Holding Efficiency"

        }

        if not required.issubset(self.df.columns):

            return

        self.df["Efficiency Score"] = (

            self.df["Expectancy Per Trade"]

            +

            self.df["Profit Per Day"]

            +

            self.df["Holding Efficiency"]

        ) / 3

    # -----------------------------------------------------

    def efficiency_grade(self):

        if "Efficiency Score" not in self.df.columns:

            return

        score = self.df["Efficiency Score"]

        conditions = [

            score >= 80,

            score >= 60,

            score >= 40,

            score >= 20

        ]

        choices = [

            "Excellent",

            "Good",

            "Average",

            "Below Average"

        ]

        self.df["Efficiency Grade"] = np.select(

            conditions,

            choices,

            default="Poor"

        )

    # -----------------------------------------------------

    def generate(self):

        logger.info(

            "Generating Efficiency Features..."

        )

        self.expectancy_per_trade()

        self.expectancy_per_day()

        self.trades_per_day()

        self.profit_per_day()

        self.signal_efficiency()

        self.trade_efficiency()

        self.capital_efficiency()

        self.holding_efficiency()

        self.efficiency_score()

        self.efficiency_grade()

        logger.info(

            "Efficiency feature engineering completed."

        )

        return self.df


if __name__ == "__main__":

    print(

        "Import inside feature_engine.py"

    )