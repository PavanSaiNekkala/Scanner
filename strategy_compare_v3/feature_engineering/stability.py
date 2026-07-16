"""
============================================================
Institutional Strategy Comparison Engine V3

File : feature_engineering/stability.py

Stability Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)



class StabilityEngine:
    """
    Institutional Stability Feature Engineering.

    Generates:

    Trade Density
    Profit Consistency
    Expectancy Stability
    Reward Consistency
    Holding Stability
    Stability Index
    Robustness Index
    Consistency Score
    Stability Grade
    """



    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()



    # =====================================================
    # SAFE DIVIDE
    # =====================================================

    @staticmethod
    def safe_divide(a, b):

        return np.where(

            b == 0,

            np.nan,

            a / b

        )



    # =====================================================
    # TRADE DENSITY
    # =====================================================

    def trade_density(self):


        if "days_held" in self.df.columns:


            self.df["Trade Density"] = (

                1

                /

                self.df["days_held"].replace(

                    0,

                    np.nan

                )

            )


            return



        required = {

            "Trades",

            "Avg days"

        }


        if required.issubset(

            self.df.columns

        ):


            self.df["Trade Density"] = self.safe_divide(

                self.df["Trades"],

                self.df["Avg days"]

            )



    # =====================================================
    # PROFIT CONSISTENCY
    # =====================================================

    def profit_consistency(self):


        required = {

            "Profit Factor",

            "Reward Risk Ratio"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Profit Consistency"] = (

            self.df["Profit Factor"]

            *

            self.df["Reward Risk Ratio"]

        )



    # =====================================================
    # EXPECTANCY STABILITY
    # =====================================================

    def expectancy_stability(self):


        if {

            "Expectancy%",

            "days_held"

        }.issubset(self.df.columns):


            self.df["Expectancy Stability"] = self.safe_divide(

                self.df["Expectancy%"],

                self.df["days_held"]

            )

            return



        if {

            "Expectancy%",

            "Avg days"

        }.issubset(self.df.columns):


            self.df["Expectancy Stability"] = self.safe_divide(

                self.df["Expectancy%"],

                self.df["Avg days"]

            )



    # =====================================================
    # REWARD CONSISTENCY
    # =====================================================

    def reward_consistency(self):


        required = {

            "Reward Risk Ratio",

            "Profit Factor"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Reward Consistency"] = self.safe_divide(

            self.df["Reward Risk Ratio"],

            self.df["Profit Factor"]

        )



    # =====================================================
    # HOLDING STABILITY
    # =====================================================

    def holding_stability(self):


        if {

            "days_held",

            "Trades"

        }.issubset(self.df.columns):


            self.df["Holding Stability"] = self.safe_divide(

                self.df["days_held"],

                self.df["Trades"]

            )


            return



        if {

            "Avg days",

            "Trades"

        }.issubset(self.df.columns):


            self.df["Holding Stability"] = self.safe_divide(

                self.df["Avg days"],

                self.df["Trades"]

            )



    # =====================================================
    # STABILITY INDEX
    # =====================================================

    def stability_index(self):


        required = {

            "Trade Density",

            "Profit Consistency",

            "Expectancy Stability",

            "Reward Consistency"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Stability Index"] = (

            self.df["Trade Density"]

            +

            self.df["Profit Consistency"]

            +

            self.df["Expectancy Stability"]

            +

            self.df["Reward Consistency"]

        ) / 4



    # =====================================================
    # ROBUSTNESS INDEX
    # =====================================================

    def robustness_index(self):


        if {

            "Stability Index",

            "Profit Factor"

        }.issubset(self.df.columns):


            self.df["Robustness Index"] = (

                self.df["Stability Index"]

                *

                self.df["Profit Factor"]

            )



    # =====================================================
    # CONSISTENCY SCORE
    # =====================================================

    def consistency_score(self):


        if {

            "Robustness Index",

            "Expectancy%"

        }.issubset(self.df.columns):


            self.df["Consistency Score"] = (

                self.df["Robustness Index"]

                *

                self.df["Expectancy%"]

            )



    # =====================================================
    # GRADE
    # =====================================================

    def stability_grade(self):


        if "Stability Index" not in self.df.columns:

            return



        score = self.df["Stability Index"]



        self.df["Stability Grade"] = np.select(

            [

                score >= 80,

                score >= 60,

                score >= 40,

                score >= 20,

            ],

            [

                "Excellent",

                "Good",

                "Average",

                "Below Average",

            ],

            default="Poor"

        )



    # =====================================================
    # GENERATE
    # =====================================================

    def generate(self):


        logger.info(

            "Generating Stability Features..."

        )


        self.trade_density()

        self.profit_consistency()

        self.expectancy_stability()

        self.reward_consistency()

        self.holding_stability()

        self.stability_index()

        self.robustness_index()

        self.consistency_score()

        self.stability_grade()



        logger.info(

            "Stability feature engineering completed."

        )


        return self.df



if __name__ == "__main__":

    print(

        "Import StabilityEngine inside feature_engine.py"

    )