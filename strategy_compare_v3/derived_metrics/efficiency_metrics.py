"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/efficiency_metrics.py

Efficiency Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)


class EfficiencyMetricsEngine:
    """
    Generates efficiency related derived metrics.

    Input Fields
    ------------
    Expectancy%
    Avg days
    Avg win%
    Avg loss%
    Trades
    Years
    Target %
    Stop %


    Generated Fields
    ----------------
    Holding Efficiency
    Return Per Holding Day
    Profit Velocity
    Trade Efficiency
    Capital Efficiency
    Time Efficiency
    Annual Capital Productivity
    Strategy Efficiency Index
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
    # HOLDING EFFICIENCY
    # ==================================================

    def holding_efficiency(self):

        required = {

            "Expectancy%",

            "Avg days"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Holding Efficiency"] = (

            self.safe_divide(

                self.df["Expectancy%"],

                self.df["Avg days"]

            )

        )



    # ==================================================
    # RETURN PER HOLDING DAY
    # ==================================================

    def return_per_holding_day(self):

        required = {

            "Avg win%",

            "Avg days"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Return Per Holding Day"] = (

            self.safe_divide(

                self.df["Avg win%"],

                self.df["Avg days"]

            )

        )



    # ==================================================
    # PROFIT VELOCITY
    # ==================================================

    def profit_velocity(self):

        required = {

            "Expectancy%",

            "Avg days"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Profit Velocity"] = (

            self.safe_divide(

                self.df["Expectancy%"],

                self.df["Avg days"]

            )

            *

            365

        )



    # ==================================================
    # TRADE EFFICIENCY
    # ==================================================

    def trade_efficiency(self):

        required = {

            "Trades",

            "Years"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Trade Efficiency"] = (

            self.safe_divide(

                self.df["Trades"],

                self.df["Years"]

            )

        )



    # ==================================================
    # CAPITAL EFFICIENCY
    # ==================================================

    def capital_efficiency(self):

        required = {

            "Expectancy%",

            "Avg loss%"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        risk = (

            self.df["Avg loss%"]

            .abs()

        )



        self.df["Capital Efficiency"] = (

            self.safe_divide(

                self.df["Expectancy%"],

                risk

            )

        )



    # ==================================================
    # TIME EFFICIENCY
    # ==================================================

    def time_efficiency(self):

        required = {

            "Avg days",

            "Years"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Time Efficiency"] = (

            self.safe_divide(

                self.df["Years"],

                self.df["Avg days"]

            )

        )



    # ==================================================
    # ANNUAL CAPITAL PRODUCTIVITY
    # ==================================================

    def annual_capital_productivity(self):

        required = {

            "Expectancy%",

            "Trades",

            "Years"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        annual_trades = (

            self.safe_divide(

                self.df["Trades"],

                self.df["Years"]

            )

        )



        self.df["Annual Capital Productivity"] = (

            self.df["Expectancy%"]

            *

            annual_trades

        )



    # ==================================================
    # STRATEGY EFFICIENCY INDEX
    # ==================================================

    def strategy_efficiency_index(self):

        required = {

            "Holding Efficiency",

            "Capital Efficiency",

            "Trade Efficiency"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Strategy Efficiency Index"] = (

            self.df["Holding Efficiency"]

            +

            self.df["Capital Efficiency"]

            +

            self.df["Trade Efficiency"]

        ) / 3


    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):

        logger.info(

            "Generating Efficiency Metrics..."

        )


        self.holding_efficiency()

        self.return_per_holding_day()

        self.profit_velocity()

        self.trade_efficiency()

        self.capital_efficiency()

        self.time_efficiency()

        self.annual_capital_productivity()

        self.strategy_efficiency_index()


        logger.info(

            "Efficiency Metrics completed."

        )


        return self.df



if __name__ == "__main__":

    print(

        "Import EfficiencyMetricsEngine"

    )