"""
Executive Dashboard Page
"""

import streamlit as st

import pandas as pd


###########################################################################
# EXECUTIVE PAGE
###########################################################################

class ExecutivePage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.ranked = result["ranked"]

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Executive Dashboard"

        )

        self.kpis()

        self.best_strategy()

        self.top_five()

    ###########################################################################
    # KPI CARDS
    ###########################################################################

    def kpis(self):

        total = len(

            self.ranked

        )

        average = round(

            self.ranked["Overall Score"].mean(),

            2

        )

        best = self.ranked.iloc[0]

        strong_buy = int(

            (

                self.ranked["Recommendation"]

                ==

                "Strong Buy"

            ).sum()

        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(

            "Strategies",

            total

        )

        c2.metric(

            "Best Strategy",

            best["Strategy"]

        )

        c3.metric(

            "Average Score",

            average

        )

        c4.metric(

            "Strong Buy",

            strong_buy

        )

    ###########################################################################
    # BEST STRATEGY
    ###########################################################################

    def best_strategy(self):

        st.subheader(

            "Best Strategy"

        )

        best = self.ranked.iloc[0]

        df = pd.DataFrame({

            "Metric":[

                "Strategy",

                "Overall Score",

                "Grade",

                "Recommendation"

            ],

            "Value":[

                best["Strategy"],

                best["Overall Score"],

                best["Grade"],

                best["Recommendation"]

            ]

        })

        df = df.astype(str)

        st.table(
            df,
            width="stretch"
        )

        st.table(

            df

        )

    ###########################################################################
    # TOP 5
    ###########################################################################

    def top_five(self):

        st.subheader(

            "Top 5 Strategies"

        )

        cols = [

            "Rank",

            "Strategy",

            "Overall Score",

            "Grade",

            "Recommendation"

        ]

        cols = [

            c

            for c in cols

            if c in self.ranked.columns

        ]

        df = self.ranked[

            cols

        ].head(

            5

        ).copy()

        df = df.astype(

            str

        )

        st.dataframe(

            df,

            width="stretch",

            hide_index=True

        )