"""
Analytics Dashboard Page
"""

import streamlit as st

import pandas as pd

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

        self.ranked = result[

            "ranked"

        ]

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

        self.kpis()

        st.divider()

        self.overall_score_chart()

        st.divider()

        self.ranking_chart()

    ###########################################################################
    # KPI CARDS
    ###########################################################################

    def kpis(self):

        if self.ranked.empty:

            st.warning(

                "No strategy data available."

            )

            return

        total = len(

            self.ranked

        )

        highest = round(

            self.ranked[

                "Overall Score"

            ].max(),

            2

        )

        average = round(

            self.ranked[

                "Overall Score"

            ].mean(),

            2

        )

        best = self.ranked.iloc[

            0

        ][

            "Strategy"

        ]

        col1, col2, col3, col4 = st.columns(

            4

        )

        col1.metric(

            "Strategies",

            total

        )

        col2.metric(

            "Highest Score",

            highest

        )

        col3.metric(

            "Average Score",

            average

        )

        col4.metric(

            "Top Strategy",

            best

        )

    ###########################################################################
    # OVERALL SCORE CHART
    ###########################################################################

    def overall_score_chart(self):

        st.subheader(

            "Overall Strategy Scores"

        )

        figure = self.charts.overall_score()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # RANKING CHART
    ###########################################################################

    def ranking_chart(self):

        st.subheader(

            "Strategy Ranking"

        )

        figure = self.charts.ranking_chart()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # GRADE DISTRIBUTION
    ###########################################################################

    def grade_distribution(self):

        st.subheader(

            "Grade Distribution"

        )

        figure = self.charts.grade_distribution()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # RECOMMENDATION DISTRIBUTION
    ###########################################################################

    def recommendation_distribution(self):

        st.subheader(

            "Recommendation Distribution"

        )

        figure = self.charts.recommendation_distribution()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # SINGLE STRATEGY RADAR
    ###########################################################################

    def radar_chart(self):

        st.subheader(

            "Strategy Radar"

        )

        strategy = st.selectbox(

            "Select Strategy",

            self.ranked[

                "Strategy"

            ],

            key="analytics_radar"

        )

        figure = self.charts.radar(

            strategy

        )

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # MULTI STRATEGY RADAR
    ###########################################################################

    def multi_radar_chart(self):

        st.subheader(

            "Multi Strategy Radar"

        )

        selected = st.multiselect(

            "Compare Strategies",

            self.ranked[

                "Strategy"

            ],

            default=list(

                self.ranked[

                    "Strategy"

                ].head(

                    2

                )

            ),

            key="analytics_multi_radar"

        )

        if len(

            selected

        ) < 2:

            st.info(

                "Select at least two strategies."

            )

            return

        figure = self.charts.multi_radar(

            selected

        )

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # SCATTER PLOT
    ###########################################################################

    def scatter_chart(self):

        st.subheader(

            "Performance vs Reliability"

        )

        figure = self.charts.scatter()

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Scatter chart unavailable."

            )

    ###########################################################################
    # BUBBLE CHART
    ###########################################################################

    def bubble_chart(self):

        st.subheader(

            "Bubble Analysis"

        )

        figure = self.charts.bubble()

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Bubble chart unavailable."

            )

    ###########################################################################
    # HISTOGRAM
    ###########################################################################

    def histogram(

        self

    ):

        st.subheader(

            "Overall Score Distribution"

        )

        figure = self.charts.histogram()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # BOXPLOT
    ###########################################################################

    def boxplot(

        self

    ):

        st.subheader(

            "Overall Score Spread"

        )

        figure = self.charts.boxplot()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # VIOLIN PLOT
    ###########################################################################

    def violin_plot(

        self

    ):

        st.subheader(

            "Overall Score Density"

        )

        figure = self.charts.violin_plot()

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Violin plot unavailable."

            )

    ###########################################################################
    # CORRELATION HEATMAP
    ###########################################################################

    def correlation_heatmap(

        self

    ):

        st.subheader(

            "Metric Correlation"

        )

        figure = self.charts.correlation()

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Correlation heatmap unavailable."

            )

    ###########################################################################
    # PARALLEL COORDINATES
    ###########################################################################

    def parallel_coordinates(

        self

    ):

        st.subheader(

            "Parallel Coordinates"

        )

        figure = self.charts.parallel_coordinates()

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Parallel coordinates unavailable."

            )

    ###########################################################################
    # METRIC COMPARISON
    ###########################################################################

    def metric_comparison(

        self

    ):

        st.subheader(

            "Metric Comparison"

        )

        figure = self.charts.metric_comparison()

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Metric comparison chart unavailable."

            )

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top_strategies(

        self

    ):

        st.subheader(

            "Top Strategies"

        )

        figure = self.charts.top_strategies(

            10

        )

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Top strategies chart unavailable."

            )

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom_strategies(

        self

    ):

        st.subheader(

            "Bottom Strategies"

        )

        figure = self.charts.bottom_strategies(

            10

        )

        if figure is not None:

            st.plotly_chart(

                figure,

                width="stretch"

            )

        else:

            st.info(

                "Bottom strategies chart unavailable."

            )

    ###########################################################################
    # DASHBOARD SUMMARY
    ###########################################################################

    def dashboard_summary(

        self

    ):

        st.subheader(

            "Analytics Summary"

        )

        summary = pd.DataFrame({

            "Metric": [

                "Strategies",

                "Highest Score",

                "Average Score",

                "Lowest Score",

                "Top Strategy"

            ],

            "Value": [

                len(

                    self.ranked

                ),

                round(

                    self.ranked[

                        "Overall Score"

                    ].max(),

                    2

                ),

                round(

                    self.ranked[

                        "Overall Score"

                    ].mean(),

                    2

                ),

                round(

                    self.ranked[

                        "Overall Score"

                    ].min(),

                    2

                ),

                self.ranked.iloc[

                    0

                ][

                    "Strategy"

                ]

            ]

        })

        summary = summary.astype(

            str

        )

        st.dataframe(

            summary,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # COMPLETE PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Analytics Dashboard"

        )

        self.kpis()

        st.divider()

        self.overall_score_chart()

        st.divider()

        self.ranking_chart()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.grade_distribution()

        with right:

            self.recommendation_distribution()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.radar_chart()

        with right:

            self.multi_radar_chart()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.scatter_chart()

        with right:

            self.bubble_chart()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.histogram()

        with right:

            self.boxplot()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.violin_plot()

        with right:

            self.correlation_heatmap()

        st.divider()

        self.parallel_coordinates()

        st.divider()

        self.metric_comparison()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.top_strategies()

        with right:

            self.bottom_strategies()

        st.divider()

        self.dashboard_summary()