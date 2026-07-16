from __future__ import annotations

import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)


class FeatureContract:


    COLUMN_MAP = {


        # Performance

        "ExpectancyPct":
            "Expectancy%",


        "Profit_Factor":
            "Profit Factor",


        "Reward_Risk_Ratio":
            "Reward Risk Ratio",


        "Win_Pct":
            "Win %",


        "Edge_Ratio":
            "Edge Ratio",



        # Returns

        "net_return_Pct":
            "Net Return %",


        "gross_return_Pct":
            "Gross Return %",


        # Holding

        "days_held":
            "Days Held",

    }



    @classmethod
    def normalize(
        cls,
        df: pd.DataFrame
    ):


        dataframe = df.copy()


        created = []


        for source,target in cls.COLUMN_MAP.items():


            if (

                source in dataframe.columns

                and

                target not in dataframe.columns

            ):


                dataframe[target] = dataframe[source]


                created.append(target)



        logger.info(

            "Feature contract created: %s",

            created

        )


        return dataframe