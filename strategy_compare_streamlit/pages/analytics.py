"""
Analytics Dashboard Page
"""

import streamlit as st

from charts import ChartEngine


###########################################################################
# ANALYTICS PAGE
###########################################################################

class AnalyticsPage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.ranked = result["ranked"]

        self.charts = ChartEngine(

            self.ranked

        )

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Analytics Dashboard"

        )

        self.score_chart()

        self.pie_charts()

        self.radar_chart()

        self.scatter_chart()

        self.additional_charts()

    ###########################################################################
    # OVERALL SCORE
    ###########################################################################

    def score_chart(self):

        st.subheader(

            "Overall Strategy Scores"

        )

        fig = self.charts.overall_score()

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # PIE CHARTS
    ###########################################################################

    def pie_charts(self):

        left, right = st.columns(2)

        with left:

            st.subheader(

                "Grade Distribution"

            )

            fig = self.charts.grade_distribution()

            st.plotly_chart(

                fig,

                width="stretch"

            )

        with right:

            st.subheader(

                "Recommendation Distribution"

            )

            fig = self.charts.recommendation_distribution()

            st.plotly_chart(

                fig,

                width="stretch"

            )

    ###########################################################################
    # RADAR
    ###########################################################################

    def radar_chart(self):

        st.subheader(

            "Strategy Radar"

        )

        strategy = st.selectbox(

            "Strategy",

            self.ranked["Strategy"],

            key="analytics_radar"

        )

        fig = self.charts.radar(

            strategy

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # SCATTER
    ###########################################################################

    def scatter_chart(self):

        st.subheader(

            "Performance vs Reliability"

        )

        fig = self.charts.scatter()

        if fig is not None:

            st.plotly_chart(

                fig,

                width="stretch"

            )

    ###########################################################################
    # EXTRA CHARTS
    ###########################################################################

    def additional_charts(self):

        left, right = st.columns(2)

        with left:

            st.subheader(

                "Overall Score Distribution"

            )

            fig = self.charts.histogram()

            st.plotly_chart(

                fig,

                width="stretch"

            )

        with right:

            st.subheader(

                "Score Spread"

            )

            fig = self.charts.boxplot()

            st.plotly_chart(

                fig,

                width="stretch"

            )

        st.subheader(

            "Metric Correlation"

        )

        fig = self.charts.correlation()

        if fig is not None:

            st.plotly_chart(

                fig,

                width="stretch"

            )

        st.subheader(

            "Top Strategies"

        )

        fig = self.charts.top_strategies(

            10

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )