"""
Strategy Ranking Page
"""

import streamlit as st

import pandas as pd


###########################################################################
# RANKING PAGE
###########################################################################

class RankingPage:

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

            "Strategy Rankings"

        )

        filtered = self.filters()

        self.summary(

            filtered

        )

        self.table(

            filtered

        )

        self.strategy_details(

            filtered

        )

    ###########################################################################
    # FILTERS
    ###########################################################################

    def filters(self):

        left, right = st.columns(2)

        search = left.text_input(

            "Search Strategy",

            ""

        )

        grades = sorted(

            self.ranked["Grade"].dropna().unique()

        )

        selected = right.multiselect(

            "Grade",

            grades,

            default=grades

        )

        df = self.ranked.copy()

        if search:

            df = df[

                df["Strategy"].str.contains(

                    search,

                    case=False,

                    na=False

                )

            ]

        if len(selected):

            df = df[

                df["Grade"].isin(

                    selected

                )

            ]

        return df

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(

        self,

        dataframe

    ):

        c1, c2, c3 = st.columns(3)

        c1.metric(

            "Visible Strategies",

            len(

                dataframe

            )

        )

        if dataframe.empty:

            c2.metric(

                "Best Score",

                "-"

            )

            c3.metric(

                "Average",

                "-"

            )

            return

        c2.metric(

            "Best Score",

            round(

                dataframe["Overall Score"].max(),

                2

            )

        )

        c3.metric(

            "Average",

            round(

                dataframe["Overall Score"].mean(),

                2

            )

        )

    ###########################################################################
    # TABLE
    ###########################################################################

    def table(

        self,

        dataframe

    ):

        st.subheader(

            "Ranking Table"

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # STRATEGY DETAILS
    ###########################################################################

    def strategy_details(

        self,

        dataframe

    ):

        if dataframe.empty:

            return

        st.subheader(

            "Strategy Details"

        )

        strategy = st.selectbox(

            "Select Strategy",

            dataframe["Strategy"]

        )

        row = dataframe[

            dataframe["Strategy"]

            ==

            strategy

        ].iloc[0]

        details = row.to_frame()

        details.columns = [

            "Value"

        ]

        st.dataframe(

            details,

            width="stretch"

        )

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top(

        self,

        n=10

    ):

        return self.ranked.head(

            n

        )

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom(

        self,

        n=10

    ):

        return self.ranked.tail(

            n

        )