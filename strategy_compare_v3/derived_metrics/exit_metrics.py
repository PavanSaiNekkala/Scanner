"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/exit_metrics.py

Exit Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)


class ExitMetricsEngine:
    """
    Generates exit behaviour metrics.

    Input Fields
    ------------
    Trades
    Target #
    Target %
    Trail #
    Trail %
    Stop #
    Stop %
    Time #
    Time-win
    Time-loss


    Generated Fields
    ----------------
    Target Ratio
    Trail Ratio
    Stop Ratio
    Time Exit Ratio
    Winning Exit %
    Losing Exit %
    Exit Edge
    Exit Efficiency
    Exit Quality
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
    # TARGET RATIO
    # ==================================================

    def target_ratio(self):

        required = {

            "Target #",

            "Trades"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Target Ratio"] = (

            self.safe_divide(

                self.df["Target #"],

                self.df["Trades"]

            )

            *

            100

        )


    # ==================================================
    # TRAIL RATIO
    # ==================================================

    def trail_ratio(self):

        required = {

            "Trail #",

            "Trades"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Trail Ratio"] = (

            self.safe_divide(

                self.df["Trail #"],

                self.df["Trades"]

            )

            *

            100

        )


    # ==================================================
    # STOP RATIO
    # ==================================================

    def stop_ratio(self):

        required = {

            "Stop #",

            "Trades"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Stop Ratio"] = (

            self.safe_divide(

                self.df["Stop #"],

                self.df["Trades"]

            )

            *

            100

        )


    # ==================================================
    # TIME EXIT RATIO
    # ==================================================

    def time_exit_ratio(self):

        required = {

            "Time #",

            "Trades"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Time Exit Ratio"] = (

            self.safe_divide(

                self.df["Time #"],

                self.df["Trades"]

            )

            *

            100

        )


    # ==================================================
    # WINNING EXIT %
    # ==================================================

    def winning_exit_percentage(self):

        required = {

            "Target %",

            "Trail %",

            "Time-win"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Winning Exit %"] = (

            self.df["Target %"]

            +

            self.df["Trail %"]

            +

            self.df["Time-win"]

        )


    # ==================================================
    # LOSING EXIT %
    # ==================================================

    def losing_exit_percentage(self):

        required = {

            "Stop %",

            "Time-loss"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Losing Exit %"] = (

            self.df["Stop %"]

            +

            self.df["Time-loss"]

        )


    # ==================================================
    # EXIT EDGE
    # ==================================================

    def exit_edge(self):

        required = {

            "Winning Exit %",

            "Losing Exit %"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Exit Edge"] = (

            self.df["Winning Exit %"]

            -

            self.df["Losing Exit %"]

        )


    # ==================================================
    # EXIT EFFICIENCY
    # ==================================================

    def exit_efficiency(self):

        required = {

            "Winning Exit %",

            "Losing Exit %"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Exit Efficiency"] = (

            self.safe_divide(

                self.df["Winning Exit %"],

                self.df["Losing Exit %"].abs()

            )

        )


    # ==================================================
    # EXIT QUALITY
    # ==================================================

    def exit_quality(self):

        required = {

            "Exit Edge",

            "Target Ratio",

            "Stop Ratio"

        }


        if not required.issubset(

            self.df.columns

        ):

            return



        self.df["Exit Quality"] = (

            self.df["Exit Edge"]

            +

            self.df["Target Ratio"]

            -

            self.df["Stop Ratio"]

        )



    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):

        logger.info(

            "Generating Exit Metrics..."

        )


        self.target_ratio()

        self.trail_ratio()

        self.stop_ratio()

        self.time_exit_ratio()

        self.winning_exit_percentage()

        self.losing_exit_percentage()

        self.exit_edge()

        self.exit_efficiency()

        self.exit_quality()


        logger.info(

            "Exit Metrics completed."

        )


        return self.df



if __name__ == "__main__":

    print(

        "Import ExitMetricsEngine"

    )