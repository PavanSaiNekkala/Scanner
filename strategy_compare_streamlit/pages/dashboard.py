import streamlit as st

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

from pathlib import Path

###########################################################################
# EXECUTIVE DASHBOARD
###########################################################################

class DashboardPage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.ranked = result["ranked"]

        self.filtered = self.filtered.copy()

    ###########################################################################

    def render(self):

        self.sidebar_filters()

        self.header()

        self.kpi_cards()

        tabs = st.tabs([

            "Executive",

            "Ranking",

            "Comparison",

            "Analytics",

            "Downloads"

        ])

        with tabs[0]:

            self.best_strategy()

            self.top5()

        with tabs[1]:

            self.ranking_table()

            self.strategy_selector()

        with tabs[2]:

            self.compare_strategies()

            self.metric_leaders()

        with tabs[3]:

            self.overall_score_chart()

            self.grade_chart()

            self.recommendation_chart()

            self.radar_chart()

            self.scatter_chart()

        with tabs[4]:

            self.downloads()

    ###########################################################################

    def header(self):

        st.header(

            "Executive Dashboard"

        )

    ###########################################################################

    def kpi_cards(self):

        total = len(

            self.filtered

        )

        if self.filtered.empty:

            st.warning(

                "No strategies match the selected filters."

            )

            return

        best = self.filtered.iloc[0]

        average = round(

            self.filtered["Overall Score"].mean(),

            2

        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(

            "Strategies",

            total

        )

        col2.metric(

            "Best Strategy",

            best["Strategy"]

        )

        col3.metric(

            "Best Score",

            round(

                best["Overall Score"],

                2

            )

        )

        col4.metric(

            "Average Score",

            average

        )

    ###########################################################################

    def best_strategy(self):

        st.subheader(

            "Best Strategy"

        )

        best = self.filtered.iloc[0]

        info = pd.DataFrame({

            "Metric":[

                "Strategy",

                "Overall Score",

                "Grade",

                "Recommendation"

            ],

            "Value":[

                best["Strategy"],

                round(

                    best["Overall Score"],

                    2

                ),

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

            info

        )

    ###########################################################################

    def top5(self):

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

            if c in self.filtered.columns

        ]

        st.dataframe(

            self.filtered[cols].head(5),

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # RANKING TABLE
    ###########################################################################

    def ranking_table(self):

        st.subheader(

            "Strategy Ranking"

        )

        search = st.text_input(

            "Search Strategy",

            ""

        )

        table = self.filtered.copy()

        if search:

            table = table[

                table["Strategy"].str.contains(

                    search,

                    case=False,

                    na=False

                )

            ]

        st.dataframe(

            table,

            width="stretch",

            hide_index=True

        )


    ###########################################################################
    # STRATEGY SELECTOR
    ###########################################################################

    def strategy_selector(self):

        st.subheader(

            "Strategy Details"

        )

        strategy = st.selectbox(

            "Select Strategy",

            self.filtered["Strategy"]

        )

        row = self.filtered[

            self.filtered["Strategy"] == strategy

        ].iloc[0]

        self.strategy_details(

            row

        )

    ###########################################################################
    # STRATEGY DETAILS
    ###########################################################################

    def strategy_details(

        self,

        row

    ):

        details = row.to_frame()

        details.columns = [

            "Value"

        ]

        st.dataframe(

            details,

            width="stretch"

        )

    ###########################################################################
    # STRATEGY COMPARISON
    ###########################################################################

    def compare_strategies(self):

        st.subheader(

            "Strategy Comparison"

        )

        strategies = self.filtered["Strategy"].tolist()

        col1, col2 = st.columns(2)

        left = col1.selectbox(

            "Strategy A",

            strategies,

            key="strategy_a"

        )

        right = col2.selectbox(

            "Strategy B",

            strategies,

            index=min(1, len(strategies) - 1),

            key="strategy_b"

        )

        if left == right:

            st.warning(

                "Please choose two different strategies."

            )

            return

        row_a = self.filtered[

            self.filtered["Strategy"] == left

        ].iloc[0]

        row_b = self.filtered[

            self.filtered["Strategy"] == right

        ].iloc[0]

        self.comparison_table(

            row_a,

            row_b

        )

    ###########################################################################
    # COMPARISON TABLE
    ###########################################################################

    def comparison_table(

        self,

        row_a,

        row_b

    ):

        metrics = [

            "Overall Score",

            "Performance Score_Mean",

            "Reliability Score_Mean",

            "Execution Score_Mean",

            "Opportunity Score_Mean",

            "Grade",

            "Recommendation"

        ]

        metrics = [

            m

            for m in metrics

            if m in self.filtered.columns

        ]

        rows = []

        for metric in metrics:

            value_a = row_a[metric]

            value_b = row_b[metric]

            winner = "-"

            if isinstance(

                value_a,

                (int, float)

            ) and isinstance(

                value_b,

                (int, float)

            ):

                if value_a > value_b:

                    winner = row_a["Strategy"]

                elif value_b > value_a:

                    winner = row_b["Strategy"]

                else:

                    winner = "Tie"

            rows.append({

                "Metric": metric,

                row_a["Strategy"]: value_a,

                row_b["Strategy"]: value_b,

                "Winner": winner

            })

        st.dataframe(

            rows,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):

        st.subheader(

            "Metric Leaders"

        )

        metrics = [

            c

            for c in self.filtered.columns

            if c.endswith("_Mean")

        ]

        leaders = []

        for metric in metrics:

            idx = self.filtered[metric].idxmax()

            leaders.append({

                "Metric":

                    metric.replace(

                        "_Mean",

                        ""

                    ),

                "Leader":

                    self.filtered.loc[

                        idx,

                        "Strategy"

                    ],

                "Value":

                    round(

                        self.filtered.loc[

                            idx,

                            metric

                        ],

                        2

                    )

            })

        st.dataframe(

            leaders,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # OVERALL SCORE CHART
    ###########################################################################

    def overall_score_chart(self):

        st.subheader(

            "Overall Strategy Score"

        )

        fig = px.bar(

            self.filtered,

            x="Strategy",

            y="Overall Score",

            color="Overall Score",

            text="Overall Score"

        )

        fig.update_layout(

            height=500,

            xaxis_title="Strategy",

            yaxis_title="Overall Score"

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # GRADE DISTRIBUTION
    ###########################################################################

    def grade_chart(self):

        if "Grade" not in self.filtered.columns:

            return

        st.subheader(

            "Grade Distribution"

        )

        df = (

            self.filtered["Grade"]

            .value_counts()

            .reset_index()

        )

        df.columns = [

            "Grade",

            "Count"

        ]

        fig = px.pie(

            df,

            values="Count",

            names="Grade"

        )

        fig.update_layout(

            height=450

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # RECOMMENDATION DISTRIBUTION
    ###########################################################################

    def recommendation_chart(self):

        st.subheader(

            "Recommendation Distribution"

        )

        df = (

            self.filtered["Recommendation"]

            .value_counts()

            .reset_index()

        )

        df.columns = [

            "Recommendation",

            "Count"

        ]

        fig = px.pie(

            df,

            values="Count",

            names="Recommendation"

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # RADAR CHART
    ###########################################################################

    def radar_chart(self):

        metrics = [

            "Overall Score_Mean",

            "Performance Score_Mean",

            "Reliability Score_Mean",

            "Execution Score_Mean",

            "Opportunity Score_Mean"

        ]

        metrics = [

            m

            for m in metrics

            if m in self.filtered.columns

        ]

        if len(metrics) == 0:

            return

        st.subheader(

            "Strategy Radar"

        )

        strategy = st.selectbox(

            "Radar Strategy",

            self.filtered["Strategy"],

            key="radar"

        )

        row = self.filtered[

            self.filtered["Strategy"] == strategy

        ].iloc[0]

        fig = go.Figure()

        fig.add_trace(

            go.Scatterpolar(

                r=[

                    row[m]

                    for m in metrics

                ],

                theta=[

                    m.replace(

                        "_Mean",

                        ""

                    )

                    for m in metrics

                ],

                fill="toself",

                name=strategy

            )

        )

        fig.update_layout(

            polar=dict(

                radialaxis=dict(

                    visible=True

                )

            ),

            height=600

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # SCATTER
    ###########################################################################

    def scatter_chart(self):

        x = "Performance Score_Mean"

        y = "Reliability Score_Mean"

        if x not in self.filtered.columns:

            return

        if y not in self.filtered.columns:

            return

        st.subheader(

            "Performance vs Reliability"

        )

        fig = px.scatter(

            self.filtered,

            x=x,

            y=y,

            hover_name="Strategy",

            size="Overall Score",

            color="Overall Score"

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

    ###########################################################################
    # DOWNLOADS
    ###########################################################################

    def downloads(self):

        st.subheader(

            "Download Reports"

        )

        excel = self.result["excel"]

        with open(

            excel,

            "rb"

        ) as f:

            st.download_button(

                "Download Excel Report",

                f,

                file_name=Path(

                    excel

                ).name,

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            )

        csv = self.filtered.to_csv(

            index=False

        ).encode(

            "utf-8"

        )

        st.download_button(

            "Download Ranking CSV",

            csv,

            file_name="ranking.csv",

            mime="text/csv"

        )

        json_data = self.filtered.to_json(

            orient="records",

            indent=4

        )

        st.download_button(

            "Download Ranking JSON",

            json_data,

            file_name="ranking.json",

            mime="application/json"

        )

    ###########################################################################
    # SIDEBAR FILTERS
    ###########################################################################

    def sidebar_filters(self):

        st.sidebar.header(

            "Dashboard Filters"

        )

        grades = sorted(

            self.filtered["Grade"].unique()

        )

        selected = st.sidebar.multiselect(

            "Grades",

            grades,

            default=grades

        )

        self.filtered = self.filtered[

            self.filtered["Grade"].isin(

                selected

            )

        ]