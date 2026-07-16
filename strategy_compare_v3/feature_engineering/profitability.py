"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/profitability.py

Production Profitability Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class ProfitabilityEngine:
    """
    Institutional Profitability Engine.

    Input Columns
    -------------
    Profit_Factor
    ExpectancyPct
    Avg_winPct
    Avg_lossPct
    Win_Pct
    Trades


    Generated Columns
    -----------------
    Profit Factor
    Win %
    Profit Per Trade
    Profitability Index
    Gross Profit Ratio
    Profitability Score
    Profit Consistency
    Expected Gross Profit
    Expected Gross Loss
    Net Expected Profit
    Profitability Grade
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
    # STANDARDIZE PROFIT FACTOR
    # ==================================================

    def standardize_profit_factor(self):

        if "Profit_Factor" in self.df.columns:

            self.df["Profit Factor"] = (

                self.df["Profit_Factor"]

            )

    # ==================================================
    # STANDARDIZE WIN %
    # ==================================================

    def standardize_win_rate(self):

        if "Win_Pct" in self.df.columns:

            self.df["Win %"] = (

                self.df["Win_Pct"]

            )

    # ==================================================
    # PROFIT PER TRADE
    # ==================================================

    def profit_per_trade(self):

        if not {

            "ExpectancyPct",

            "Trades"

        }.issubset(self.df.columns):

            return


        self.df["Profit Per Trade"] = (

            self.safe_divide(

                self.df["ExpectancyPct"],

                self.df["Trades"]

            )

        )

    # ==================================================
    # PROFITABILITY INDEX
    # ==================================================

    def profitability_index(self):

        if not {

            "Profit Factor",

            "Win %"

        }.issubset(self.df.columns):

            return


        self.df["Profitability Index"] = (

            self.df["Profit Factor"]

            *

            self.df["Win %"]

            /

            100

        )

    # ==================================================
    # GROSS PROFIT RATIO
    # ==================================================

    def gross_profit_ratio(self):

        if not {

            "Avg_winPct",

            "Avg_lossPct"

        }.issubset(self.df.columns):

            return


        self.df["Gross Profit Ratio"] = (

            self.safe_divide(

                self.df["Avg_winPct"],

                self.df["Avg_lossPct"].abs()

            )

        )

    # ==================================================
    # PROFITABILITY SCORE
    # ==================================================

    def profitability_score(self):

        if not {

            "Profitability Index",

            "ExpectancyPct"

        }.issubset(self.df.columns):

            return


        self.df["Profitability Score"] = (

            self.df["Profitability Index"]

            *

            self.df["ExpectancyPct"]

        )

    # ==================================================
    # PROFIT CONSISTENCY
    # ==================================================

    def profit_consistency(self):

        if not {

            "Profit Factor",

            "Reward Risk Ratio"

        }.issubset(self.df.columns):

            return


        self.df["Profit Consistency"] = (

            self.df["Profit Factor"]

            *

            self.df["Reward Risk Ratio"]

        )

    # ==================================================
    # EXPECTED GROSS PROFIT
    # ==================================================

    def expected_gross_profit(self):

        if not {

            "Win %",

            "Avg_winPct"

        }.issubset(self.df.columns):

            return


        self.df["Expected Gross Profit"] = (

            self.df["Win %"]

            /

            100

        ) * self.df["Avg_winPct"]

    # ==================================================
    # EXPECTED GROSS LOSS
    # ==================================================

    def expected_gross_loss(self):

        if not {

            "Win %",

            "Avg_lossPct"

        }.issubset(self.df.columns):

            return


        self.df["Expected Gross Loss"] = (

            1 -

            self.df["Win %"]

            /

            100

        ) * self.df["Avg_lossPct"].abs()

    # ==================================================
    # NET EXPECTED PROFIT
    # ==================================================

    def net_expected_profit(self):

        if not {

            "Expected Gross Profit",

            "Expected Gross Loss"

        }.issubset(self.df.columns):

            return


        self.df["Net Expected Profit"] = (

            self.df["Expected Gross Profit"]

            -

            self.df["Expected Gross Loss"]

        )

    # ==================================================
    # PROFITABILITY GRADE
    # ==================================================

    def profitability_grade(self):

        if "Profitability Score" not in self.df.columns:

            return


        score = self.df["Profitability Score"]


        conditions = [

            score >= 200,

            score >= 100,

            score >= 50,

            score >= 20

        ]


        choices = [

            "Excellent",

            "Good",

            "Average",

            "Below Average"

        ]


        self.df["Profitability Grade"] = np.select(

            conditions,

            choices,

            default="Poor"

        )

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):

        logger.info(

            "Generating Profitability Features..."

        )


        self.standardize_profit_factor()

        self.standardize_win_rate()

        self.profit_per_trade()

        self.profitability_index()

        self.gross_profit_ratio()

        self.profitability_score()

        self.profit_consistency()

        self.expected_gross_profit()

        self.expected_gross_loss()

        self.net_expected_profit()

        self.profitability_grade()


        logger.info(

            "Profitability feature engineering completed."

        )


        return self.df


if __name__ == "__main__":

    print(
        "Import ProfitabilityEngine inside feature_engine.py"
    )