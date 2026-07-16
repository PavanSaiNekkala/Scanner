"""
============================================================
Institutional Strategy Comparison Engine V3

File : scoring/efficiency_score.py

Institutional Efficiency Score Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import numpy as np
import pandas as pd


from core.logger import get_logger


logger = get_logger(__name__)



class EfficiencyScoreEngine:
    """
    Computes institutional Efficiency Score.


    Output
    ------

    Efficiency Score


    Supported Features
    ------------------

    Expectancy Per Trade
    Expectancy Per Day
    Trades Per Day
    Trades / Year
    Holding Efficiency
    Capital Efficiency

    """



    DEFAULT_WEIGHTS = {


        "Expectancy Per Trade":

            0.25,


        "Expectancy Per Day":

            0.20,


        "Trades Per Day":

            0.15,


        "Trades / Year":

            0.15,


        "Holding Efficiency":

            0.15,


        "Capital Efficiency":

            0.10,


    }



    def __init__(

        self,

        dataframe: pd.DataFrame,

        weights: dict | None = None

    ):


        self.df = dataframe.copy()


        self.weights = (

            weights

            if weights

            else self.DEFAULT_WEIGHTS

        )



    # ==================================================
    # COLUMN NORMALIZATION
    # ==================================================

    def normalize_columns(self):


        mapping = {


            "Trades_Per_Day":

                "Trades Per Day",


            "Holding_Efficiency":

                "Holding Efficiency",


            "Capital_Efficiency":

                "Capital Efficiency",


            "Expectancy_Per_Trade":

                "Expectancy Per Trade",


            "Expectancy_Per_Day":

                "Expectancy Per Day",

        }



        for source, target in mapping.items():


            if (

                source in self.df.columns

                and

                target not in self.df.columns

            ):


                self.df[target] = self.df[source]



    # ==================================================
    # CREATE FALLBACK FEATURES
    # ==================================================

    def generate_missing_features(self):


        # Trades per day

        if (

            "Trades Per Day"

            not in self.df.columns

        ):


            if "Trades" in self.df.columns and "Avg days" in self.df.columns:


                self.df["Trades Per Day"] = (

                    self.df["Trades"]

                    /

                    self.df["Avg days"]

                    .replace(

                        0,

                        np.nan

                    )

                )



        # Holding efficiency

        if (

            "Holding Efficiency"

            not in self.df.columns

        ):


            if (

                "Expectancy%"

                in self.df.columns

                and

                "Avg days"

                in self.df.columns

            ):


                self.df["Holding Efficiency"] = (

                    self.df["Expectancy%"]

                    /

                    self.df["Avg days"]

                    .replace(

                        0,

                        np.nan

                    )

                )



        # Capital efficiency

        if (

            "Capital Efficiency"

            not in self.df.columns

        ):


            if (

                "Expectancy%"

                in self.df.columns

                and

                "entry_price"

                in self.df.columns

            ):


                self.df["Capital Efficiency"] = (

                    self.df["Expectancy%"]

                    /

                    self.df["entry_price"]

                    .replace(

                        0,

                        np.nan

                    )

                )



    # ==================================================
    # NORMALIZATION
    # ==================================================

    @staticmethod
    def normalize(series):


        minimum = series.min()

        maximum = series.max()


        if maximum == minimum:


            return pd.Series(

                50,

                index=series.index

            )


        return (

            (series - minimum)

            /

            (maximum - minimum)

            *

            100

        )



    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):


        logger.info(

            "Generating Efficiency Score..."

        )



        self.normalize_columns()


        self.generate_missing_features()



        score = pd.Series(

            0.0,

            index=self.df.index

        )


        total_weight = 0



        for feature, weight in self.weights.items():


            if feature not in self.df.columns:


                logger.warning(

                    "Skipping missing efficiency feature: %s",

                    feature

                )

                continue



            normalized = self.normalize(

                self.df[feature]

            )



            score += (

                normalized

                *

                weight

            )


            total_weight += weight



        if total_weight == 0:


            self.df["Efficiency Score"] = 0



        else:


            self.df["Efficiency Score"] = (

                score

                /

                total_weight

            ).round(2)



        logger.info(

            "Efficiency Score generated."

        )


        return self.df[

            [

                "Efficiency Score"

            ]

        ]



if __name__ == "__main__":


    print(

        "Import EfficiencyScoreEngine inside scoring_engine.py"

    )