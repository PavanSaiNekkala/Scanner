"""
Strategy Ranking Page
"""

import streamlit as st

import pandas as pd

from charts import ChartEngine


###########################################################################
# RANKING PAGE
###########################################################################

class RankingPage:

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

            "Strategy Rankings"

        )

        filtered = self.filters()

        st.divider()

        self.kpis(

            filtered

        )

        st.divider()

        self.summary(

            filtered

        )

        st.divider()

        self.table(

            filtered

        )

        st.divider()

        self.strategy_details(

            filtered

        )

    ###########################################################################
    # KPI CARDS
    ###########################################################################

    def kpis(

        self,

        dataframe

    ):

        if dataframe.empty:

            st.warning(

                "No strategies available."

            )

            return

        col1, col2, col3, col4 = st.columns(

            4

        )

        col1.metric(

            "Strategies",

            len(

                dataframe

            )

        )

        col2.metric(

            "Highest Score",

            round(

                dataframe[

                    "Overall Score"

                ].max(),

                2

            )

        )

        col3.metric(

            "Average Score",

            round(

                dataframe[

                    "Overall Score"

                ].mean(),

                2

            )

        )

        col4.metric(

            "Top Strategy",

            dataframe.iloc[

                0

            ][

                "Strategy"

            ]

        )

    ###########################################################################
    # FILTERS
    ###########################################################################

    def filters(self):

        st.subheader(

            "Filters"

        )

        col1, col2, col3 = st.columns(

            3

        )

        search = col1.text_input(

            "Search Strategy",

            ""

        )

        grades = sorted(

            self.ranked[

                "Grade"

            ]

            .dropna()

            .unique()

        )

        selected_grades = col2.multiselect(

            "Grade",

            grades,

            default=grades

        )

        recommendations = sorted(

            self.ranked[

                "Recommendation"

            ]

            .dropna()

            .unique()

        )

        selected_recommendations = col3.multiselect(

            "Recommendation",

            recommendations,

            default=recommendations

        )

        dataframe = self.ranked.copy()

        if search:

            dataframe = dataframe[

                dataframe[

                    "Strategy"

                ]

                .str.contains(

                    search,

                    case=False,

                    na=False

                )

            ]

        if len(

            selected_grades

        ):

            dataframe = dataframe[

                dataframe[

                    "Grade"

                ]

                .isin(

                    selected_grades

                )

            ]

        if len(

            selected_recommendations

        ):

            dataframe = dataframe[

                dataframe[

                    "Recommendation"

                ]

                .isin(

                    selected_recommendations

                )

            ]

        return dataframe

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(

        self,

        dataframe

    ):

        col1, col2, col3 = st.columns(

            3

        )

        col1.metric(

            "Visible Strategies",

            len(

                dataframe

            )

        )

        if dataframe.empty:

            col2.metric(

                "Best Score",

                "-"

            )

            col3.metric(

                "Average",

                "-"

            )

            return

        col2.metric(

            "Best Score",

            round(

                dataframe[

                    "Overall Score"

                ].max(),

                2

            )

        )

        col3.metric(

            "Average",

            round(

                dataframe[

                    "Overall Score"

                ].mean(),

                2

            )

        )

    ###########################################################################
    # RANKING TABLE
    ###########################################################################

    def table(

        self,

        dataframe

    ):

        st.subheader(

            "Strategy Ranking"

        )

        if dataframe.empty:

            st.info(

                "No strategies match the selected filters."

            )

            return

        display_columns = [

            "Rank",

            "Strategy",

            "Overall Score",

            "Grade",

            "Recommendation"

        ]

        display_columns.extend(

            [

                column

                for column in dataframe.columns

                if column.endswith(

                    "_Mean"

                )

            ]

        )

        display_columns = [

            column

            for column in display_columns

            if column in dataframe.columns

        ]

        table = dataframe[

            display_columns

        ].copy()

        table = table.astype(

            str

        )

        st.dataframe(

            table,

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

            dataframe[

                "Strategy"

            ].tolist()

        )

        row = dataframe[

            dataframe[

                "Strategy"

            ]

            ==

            strategy

        ].iloc[0]

        details = (

            row

            .to_frame(

                name="Value"

            )

            .reset_index()

        )

        details.columns = [

            "Metric",

            "Value"

        ]

        details = details.astype(

            str

        )

        st.dataframe(

            details,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top_strategies(

        self,

        n=10

    ):

        st.subheader(

            f"Top {n} Strategies"

        )

        dataframe = (

            self.ranked

            .head(

                n

            )

            .copy()

        )

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom_strategies(

        self,

        n=10

    ):

        st.subheader(

            f"Bottom {n} Strategies"

        )

        dataframe = (

            self.ranked

            .tail(

                n

            )

            .copy()

        )

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # SCORE BREAKDOWN
    ###########################################################################

    def score_breakdown(

        self,

        dataframe

    ):

        if dataframe.empty:

            return

        st.subheader(

            "Metric Score Breakdown"

        )

        metric_columns = [

            column

            for column in dataframe.columns

            if column.endswith(

                "_Mean"

            )

        ]

        if not metric_columns:

            st.info(

                "No metric scores available."

            )

            return

        breakdown = dataframe[

            [

                "Strategy"

            ]

            +

            metric_columns

        ].copy()

        breakdown = breakdown.astype(

            str

        )

        st.dataframe(

            breakdown,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # OVERALL SCORE CHART
    ###########################################################################

    def overall_score_chart(

        self

    ):

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

    def ranking_chart(

        self

    ):

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

    def grade_distribution(

        self

    ):

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

    def recommendation_distribution(

        self

    ):

        st.subheader(

            "Recommendation Distribution"

        )

        figure = self.charts.recommendation_distribution()

        st.plotly_chart(

            figure,

            width="stretch"

        )

    ###########################################################################
    # SCORE DISTRIBUTION
    ###########################################################################

    def score_distribution(

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
    # SCORE SPREAD
    ###########################################################################

    def score_spread(

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
    # DASHBOARD SUMMARY
    ###########################################################################

    def dashboard_summary(

        self,

        dataframe

    ):

        st.subheader(

            "Ranking Summary"

        )

        if dataframe.empty:

            st.info(

                "No data available."

            )

            return

        rows = [

            {

                "Metric":

                    "Strategies",

                "Value":

                    len(

                        dataframe

                    )

            },

            {

                "Metric":

                    "Best Strategy",

                "Value":

                    dataframe.iloc[

                        0

                    ][

                        "Strategy"

                    ]

            },

            {

                "Metric":

                    "Highest Score",

                "Value":

                    round(

                        dataframe[

                            "Overall Score"

                        ].max(),

                        2

                    )

            },

            {

                "Metric":

                    "Average Score",

                "Value":

                    round(

                        dataframe[

                            "Overall Score"

                        ].mean(),

                        2

                    )

            },

            {

                "Metric":

                    "Lowest Score",

                "Value":

                    round(

                        dataframe[

                            "Overall Score"

                        ].min(),

                        2

                    )

            }

        ]

        summary = pd.DataFrame(

            rows

        )

        summary = summary.astype(

            str

        )

        st.dataframe(

            summary,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # EXPORT PREVIEW
    ###########################################################################

    def export_preview(

        self

    ):

        st.subheader(

            "Export Preview"

        )

        if "excel" not in self.result:

            st.info(

                "Export information unavailable."

            )

            return

        rows = [

            {

                "Export":

                    "Excel Report",

                "Location":

                    str(

                        self.result[

                            "excel"

                        ]

                    )

            }

        ]

        dataframe = pd.DataFrame(

            rows

        )

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # COMPLETE PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Strategy Rankings"

        )

        filtered = self.filters()

        st.divider()

        self.kpis(

            filtered

        )

        st.divider()

        self.summary(

            filtered

        )

        st.divider()

        self.table(

            filtered

        )

        st.divider()

        self.strategy_details(

            filtered

        )

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.top_strategies()

        with right:

            self.bottom_strategies()

        st.divider()

        self.score_breakdown(

            filtered

        )

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

            self.score_distribution()

        with right:

            self.score_spread()

        st.divider()

        self.dashboard_summary(

            filtered

        )

        st.divider()

        self.export_preview()