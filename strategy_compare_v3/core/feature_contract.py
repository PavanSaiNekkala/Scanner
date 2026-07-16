"""
============================================================
Institutional Strategy Comparison Engine V3

File : core/feature_contract.py

Central Feature Contract Normalization Layer

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)



class FeatureContract:
    """
    Centralized column contract manager.

    Converts raw / cleaned loader columns
    into institutional engine names.


    Flow
    ----

    Raw Dataset

        |

        v

    Feature Contract

        |

        v

    Feature Engineering

        |

        v

    Scoring

    """



    COLUMN_MAP = {


        # ==================================================
        # PERFORMANCE METRICS
        # ==================================================


        "ExpectancyPct":

            "Expectancy%",



        "Expectancy_Pct":

            "Expectancy%",



        "Profit_Factor":

            "Profit Factor",



        "ProfitFactor":

            "Profit Factor",



        "Reward_Risk_Ratio":

            "Reward Risk Ratio",



        "RewardRiskRatio":

            "Reward Risk Ratio",



        "Win_Pct":

            "Win %",



        "WinPct":

            "Win %",



        "Edge_Ratio":

            "Edge Ratio",



        "EdgeRatio":

            "Edge Ratio",



        # ==================================================
        # AVERAGE RETURNS
        # ==================================================


        "Avg_winPct":

            "Avg win%",



        "Avg_lossPct":

            "Avg loss%",



        "Avg_Win_Pct":

            "Avg win%",



        "Avg_Loss_Pct":

            "Avg loss%",



        # ==================================================
        # TARGET STOP
        # ==================================================


        "Target_Pct":

            "Target %",



        "Stop_Pct":

            "Stop %",



        # ==================================================
        # TRADING FREQUENCY
        # ==================================================


        "Trades_Per_Year":

            "Trades / Year",



        "Signals_Today":

            "Signals today",



        # ==================================================
        # HOLDING
        # ==================================================


        "days_held":

            "Avg days",



        "Days_Held":

            "Avg days",



        # ==================================================
        # RETURNS
        # ==================================================


        "net_return_Pct":

            "Net Return %",



        "gross_return_Pct":

            "Gross Return %",


    }



    # ==================================================
    # NORMALIZE
    # ==================================================


    @classmethod
    def normalize(
        cls,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:


        df = dataframe.copy()



        created = []



        for source, target in cls.COLUMN_MAP.items():


            if (

                source in df.columns

                and

                target not in df.columns

            ):


                df[target] = df[source]


                created.append(

                    target

                )



        if created:


            logger.info(

                "Feature contract created columns: %s",

                sorted(

                    set(created)

                )

            )


        else:


            logger.info(

                "Feature contract: no normalization required."

            )



        return df



    # ==================================================
    # VALIDATE
    # ==================================================


    @classmethod
    def validate(
        cls,
        dataframe: pd.DataFrame,
        required: list[str]
    ):


        missing = [

            column

            for column in required

            if column not in dataframe.columns

        ]



        if missing:


            raise ValueError(

                f"Feature contract missing columns: {missing}"

            )



        return True



if __name__ == "__main__":


    print(

        "Import FeatureContract into engines"

    )