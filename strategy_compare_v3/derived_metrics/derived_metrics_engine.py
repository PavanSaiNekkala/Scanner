"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/derived_metrics_engine.py

Trade Level -> Strategy Level Metrics

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import numpy as np

import pandas as pd


from core.logger import get_logger



logger = get_logger(__name__)




class DerivedMetricsEngine:
    """
    Converts raw backtest trades into
    strategy comparison metrics.


    Input
    -----

    Trade level dataframe


    Output
    ------

    Strategy level dataframe


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
    def safe_divide(a,b):


        return np.where(

            b == 0,

            np.nan,

            a / b

        )



    # ==================================================
    # BASIC COUNTS
    # ==================================================

    def trade_count(self):


        self.df["Trades"] = len(

            self.df

        )



    # ==================================================
    # WIN LOSS
    # ==================================================

    def win_loss_metrics(self):


        if "outcome" not in self.df.columns:

            return



        wins = (

            self.df["outcome"]

            .astype(str)

            .str.upper()

            .eq("WIN")

        )


        losses = (

            self.df["outcome"]

            .astype(str)

            .str.upper()

            .eq("LOSS")

        )



        self.df["Win %"] = (

            wins.mean()

            *

            100

        )



        self.df["Loss %"] = (

            losses.mean()

            *

            100

        )



    # ==================================================
    # RETURN METRICS
    # ==================================================

    def return_metrics(self):


        if "net_return_Pct" not in self.df.columns:

            return



        win_returns = self.df.loc[

            self.df["net_return_Pct"] > 0,

            "net_return_Pct"

        ]


        loss_returns = self.df.loc[

            self.df["net_return_Pct"] < 0,

            "net_return_Pct"

        ]



        avg_win = win_returns.mean()


        avg_loss = abs(

            loss_returns.mean()

        )



        expectancy = (

            (self.df["net_return_Pct"])

            .mean()

        )



        self.df["Avg win%"] = avg_win


        self.df["Avg loss%"] = avg_loss


        self.df["Expectancy%"] = expectancy



        self.df["Reward Risk Ratio"] = self.safe_divide(

            avg_win,

            avg_loss

        )



    # ==================================================
    # PROFIT FACTOR
    # ==================================================

    def profit_factor(self):


        if "net_return_Pct" not in self.df.columns:

            return



        gross_profit = self.df.loc[

            self.df["net_return_Pct"] > 0,

            "net_return_Pct"

        ].sum()



        gross_loss = abs(

            self.df.loc[

                self.df["net_return_Pct"] < 0,

                "net_return_Pct"

            ].sum()

        )



        self.df["Profit Factor"] = self.safe_divide(

            gross_profit,

            gross_loss

        )



    # ==================================================
    # HOLDING PERIOD
    # ==================================================

    def holding_metrics(self):


        if "days_held" not in self.df.columns:

            return



        self.df["Avg days"] = (

            self.df["days_held"]

            .mean()

        )



        self.df["Expectancy Per Day"] = self.safe_divide(

            self.df["Expectancy%"],

            self.df["Avg days"]

        )



    # ==================================================
    # TRADE FREQUENCY
    # ==================================================

    def frequency_metrics(self):


        if "signal_date" not in self.df.columns:

            return



        years = (

            (

                pd.to_datetime(

                    self.df["signal_date"]

                ).max()

                -

                pd.to_datetime(

                    self.df["signal_date"]

                ).min()

            ).days

            /

            365

        )



        self.df["Years"] = years



        self.df["Trades / Year"] = self.safe_divide(

            len(self.df),

            years

        )



    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):


        logger.info(

            "Generating Derived Metrics..."

        )


        self.trade_count()


        self.win_loss_metrics()


        self.return_metrics()


        self.profit_factor()


        self.holding_metrics()


        self.frequency_metrics()



        # keep one strategy summary row

        summary = self.df.tail(1).copy()



        logger.info(

            "Derived Metrics completed."

        )



        return summary