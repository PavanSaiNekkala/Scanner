"""
============================================================
Institutional Strategy Comparison Engine V3

Filters Component

============================================================
"""

from __future__ import annotations

import pandas as pd


class Filters:

    @staticmethod
    def recommendation(

        dataframe: pd.DataFrame,

        recommendation: str

    ):

        return dataframe[

            dataframe["Recommendation"]

            ==

            recommendation

        ]

    @staticmethod
    def top_n(

        dataframe: pd.DataFrame,

        n: int

    ):

        return (

            dataframe

            .sort_values(

                "Composite Score",

                ascending=False

            )

            .head(n)

        )