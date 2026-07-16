"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/opportunity_metrics.py

Opportunity Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)


class OpportunityMetricsEngine:
    """
    Generates opportunity related derived metrics.

    Input Fields
    ------------
    Signals today
    RS%
    Rank
    Trades
    Win%
    Expectancy%


    Generated Fields
    ----------------
    Signal Strength
    Rank Quality
    RS Impact
    Opportunity Index
    Opportunity Density
    Opportunity Quality
    Market Opportunity Factor
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
    # SIGNAL STRENGTH
    # ==================================================

    def signal_strength(self):

        if "Signals today" not in self.df.columns:

            return



        self.df["Signal Strength"] = (

            np.sqrt(

                self.df["Signals today"]

            )

        )



    # ==================================================
    # RANK QUALITY
    # ==================================================

    def rank_quality(self):

        if "Rank" not in self.df.columns:

            return



        self.df["Rank Quality"] = (

            1

            /

            np.log1p(

                self.df["Rank"]

            )

        )



    # ==================================================
    # RELATIVE STRENGTH IMPACT
    # ==================================================

    def rs_impact(self):

        if "RS%" not in self.df.columns:

            return



        self.df["RS Impact"] = (

            self.df["RS%"]

            /

            100

        )



    # ==================================================
    # OPPORTUNITY INDEX
    # ==================================================

    def opportunity_index(self):

        required = {

            "Signals today",

            "RS%",

            "Rank"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Opportunity Index"] = (

            np.sqrt(

                self.df["Signals today"]

            )

            *

            (

                self.df["RS%"]

                /

                100

            )

            /

            np.log1p(

                self.df["Rank"]

            )

        )



    # ==================================================
    # OPPORTUNITY DENSITY
    # ==================================================

    def opportunity_density(self):

        required = {

            "Signals today",

            "Trades"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Opportunity Density"] = (

            self.safe_divide(

                self.df["Signals today"],

                self.df["Trades"]

            )

        )



    # ==================================================
    # OPPORTUNITY QUALITY
    # ==================================================

    def opportunity_quality(self):

        required = {

            "Opportunity Index",

            "Win%"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Opportunity Quality"] = (

            self.df["Opportunity Index"]

            *

            (

                self.df["Win%"]

                /

                100

            )

        )



    # ==================================================
    # MARKET OPPORTUNITY FACTOR
    # ==================================================

    def market_opportunity_factor(self):

        required = {

            "Opportunity Index",

            "Expectancy%"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Market Opportunity Factor"] = (

            self.df["Opportunity Index"]

            *

            self.df["Expectancy%"]

        )



    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):

        logger.info(

            "Generating Opportunity Metrics..."

        )


        self.signal_strength()

        self.rank_quality()

        self.rs_impact()

        self.opportunity_index()

        self.opportunity_density()

        self.opportunity_quality()

        self.market_opportunity_factor()



        logger.info(

            "Opportunity Metrics completed."

        )


        return self.df



if __name__ == "__main__":

    print(

        "Import OpportunityMetricsEngine"

    )