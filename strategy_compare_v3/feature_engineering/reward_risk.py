"""
============================================================
Institutional Strategy Comparison Engine V3
File : feature_engineering/reward_risk.py

Production Reward Risk Feature Engineering

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)


class RewardRiskEngine:
    """
    Institutional Reward Risk Feature Engine.

    Generates:

    Reward Risk Ratio
    Target Stop Ratio
    Win Loss Ratio
    Expectancy Per Risk
    Profit Factor Score
    Edge Ratio
    Risk Adjusted Reward

    Also creates scoring contract columns.
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
    # CREATE SCORING CONTRACT COLUMNS
    # ==================================================

    def create_contract_columns(self):


        mappings = {


            "Avg_winPct":
                "Avg win%",


            "Avg_lossPct":
                "Avg loss%",


            "Win_Pct":
                "Win %",


            "Target_Pct":
                "Target %",


            "Stop_Pct":
                "Stop %",


            "ExpectancyPct":
                "Expectancy%",


            "Profit_Factor":
                "Profit Factor",

        }



        created = []


        for source, target in mappings.items():


            if (

                source in self.df.columns

                and

                target not in self.df.columns

            ):

                self.df[target] = (

                    self.df[source]

                )

                created.append(target)



        if created:

            logger.info(

                "Reward Risk contract columns created: %s",

                created

            )



    # ==================================================
    # STOP LOSS METRIC
    # ==================================================

    def generate_stop_metric(self):


        if "Stop %" in self.df.columns:

            return



        if (

            "entry_price" in self.df.columns

            and

            "stop_price" in self.df.columns

        ):


            self.df["Stop %"] = (


                (

                    self.df["entry_price"]

                    -

                    self.df["stop_price"]

                )

                /

                self.df["entry_price"]

                *

                100


            )



    # ==================================================
    # AVG LOSS
    # ==================================================

    def generate_average_loss(self):


        if "Avg loss%" in self.df.columns:

            return



        if "net_return_Pct" in self.df.columns:


            losses = self.df.loc[

                self.df["net_return_Pct"] < 0,

                "net_return_Pct"

            ]



            if len(losses):


                self.df["Avg loss%"] = abs(

                    losses.mean()

                )



    # ==================================================
    # AVG WIN
    # ==================================================

    def generate_average_win(self):


        if "Avg win%" in self.df.columns:

            return



        if "net_return_Pct" in self.df.columns:


            wins = self.df.loc[

                self.df["net_return_Pct"] > 0,

                "net_return_Pct"

            ]



            if len(wins):

                self.df["Avg win%"] = (

                    wins.mean()

                )


    # ==================================================
    # REWARD RISK
    # ==================================================

    def reward_risk_ratio(self):


        required = [

            "Avg win%",

            "Avg loss%"

        ]



        if not all(

            c in self.df.columns

            for c in required

        ):

            return



        self.df["Reward Risk Ratio"] = (

            self.safe_divide(

                self.df["Avg win%"],

                self.df["Avg loss%"].abs()

            )

        )


    # ==================================================
    # TARGET STOP
    # ==================================================

    def target_stop_ratio(self):


        if not {

            "Target %",

            "Stop %"

        }.issubset(self.df.columns):

            return



        self.df["Target Stop Ratio"] = (

            self.safe_divide(

                self.df["Target %"],

                self.df["Stop %"].abs()

            )

        )


    # ==================================================
    # WIN LOSS
    # ==================================================

    def win_loss_ratio(self):


        if not {

            "Win %",

            "Avg loss%"

        }.issubset(self.df.columns):

            return



        self.df["Win Loss Ratio"] = (

            self.safe_divide(

                self.df["Win %"],

                self.df["Avg loss%"].abs()

            )

        )


    # ==================================================
    # EXPECTANCY RISK
    # ==================================================

    def expectancy_per_risk(self):


        if not {

            "Expectancy%",

            "Avg loss%"

        }.issubset(self.df.columns):

            return



        self.df["Expectancy Per Risk"] = (

            self.safe_divide(

                self.df["Expectancy%"],

                self.df["Avg loss%"].abs()

            )

        )


    # ==================================================
    # PROFIT FACTOR
    # ==================================================

    def profit_factor_score(self):


        if "Profit Factor" not in self.df.columns:

            return



        self.df["Profit Factor Score"] = (

            self.df["Profit Factor"]

            *

            100

        )


    # ==================================================
    # EDGE RATIO
    # ==================================================

    def edge_ratio(self):


        if not {

            "Reward Risk Ratio",

            "Win %"

        }.issubset(self.df.columns):

            return



        self.df["Edge Ratio"] = (

            self.df["Reward Risk Ratio"]

            *

            self.df["Win %"]

            /

            100

        )


    # ==================================================
    # RISK ADJUSTED REWARD
    # ==================================================

    def risk_adjusted_reward(self):


        if not {

            "Reward Risk Ratio",

            "Expectancy%"

        }.issubset(self.df.columns):

            return



        self.df["Risk Adjusted Reward"] = (

            self.df["Reward Risk Ratio"]

            *

            self.df["Expectancy%"]

        )


    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):


        logger.info(

            "Generating Reward-Risk Features..."

        )


        self.create_contract_columns()


        self.generate_stop_metric()

        self.generate_average_loss()

        self.generate_average_win()



        self.reward_risk_ratio()

        self.target_stop_ratio()

        self.win_loss_ratio()

        self.expectancy_per_risk()

        self.profit_factor_score()

        self.edge_ratio()

        self.risk_adjusted_reward()



        logger.info(

            "Reward-Risk feature engineering completed."

        )


        return self.df



if __name__ == "__main__":


    print(

        "Import RewardRiskEngine inside feature_engine.py"

    )