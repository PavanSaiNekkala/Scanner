"""
Executive Dashboard Page
"""

import streamlit as st

import pandas as pd

from charts import ChartEngine

###########################################################################
# EXECUTIVE PAGE
###########################################################################


class ExecutivePage:
    def __init__(self, result):
        self.result = result

        self.ranked = result["ranked"]

        self.insights = result.get("insights", {})

        self.charts = ChartEngine(self.ranked)

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):
        st.header("Executive Dashboard")

        self.kpis()

        st.divider()

        self.executive_summary()

        st.divider()

        self.best_strategy()

        st.divider()

        self.top_five()

    ###########################################################################
    # KPI CARDS
    ###########################################################################

    def kpis(self):
        if self.ranked.empty:
            st.warning("No ranking data available.")

            return

        total = len(self.ranked)

        average = round(self.ranked["Overall Score"].mean(), 2)

        highest = round(self.ranked["Overall Score"].max(), 2)

        strong_buy = int((self.ranked["Recommendation"] == "Strong Buy").sum())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Strategies", total)

        col2.metric("Highest Score", highest)

        col3.metric("Average Score", average)

        col4.metric("Strong Buy", strong_buy)

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):
        st.subheader("Executive Summary")

        summary = self.insights.get("executive_summary")

        if summary is None:
            summary = self.insights.get("executive")

        if summary is None:
            st.info("Executive summary is not available.")

            return

        dataframe = summary.copy()

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # BEST STRATEGY
    ###########################################################################

    def best_strategy(self):
        st.subheader("Best Strategy")

        if self.ranked.empty:
            st.info("No strategy available.")

            return

        best = self.ranked.iloc[0]

        dataframe = pd.DataFrame(
            {
                "Metric": ["Strategy", "Overall Score", "Grade", "Recommendation"],
                "Value": [
                    best["Strategy"],
                    round(best["Overall Score"], 2),
                    best["Grade"],
                    best["Recommendation"],
                ],
            }
        )

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # TOP 5 STRATEGIES
    ###########################################################################

    def top_five(self):
        st.subheader("Top 5 Strategies")

        if self.ranked.empty:
            st.info("No ranking available.")

            return

        columns = ["Rank", "Strategy", "Overall Score", "Grade", "Recommendation"]

        columns = [column for column in columns if column in self.ranked.columns]

        dataframe = self.ranked[columns].head(5).copy()

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):
        st.subheader("Metric Leaders")

        leaders = self.insights.get("metric_leaders")

        if leaders is None:
            leaders = self.insights.get("leaders")

        if leaders is None:
            st.info("Metric leaders are unavailable.")

            return

        dataframe = leaders.copy()

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # RECOMMENDATION SUMMARY
    ###########################################################################

    def recommendation_summary(self):
        st.subheader("Recommendation Summary")

        if "Recommendation" not in self.ranked.columns:
            st.info("Recommendation data unavailable.")

            return

        dataframe = self.ranked["Recommendation"].value_counts().reset_index()

        dataframe.columns = ["Recommendation", "Count"]

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # OVERALL SCORE CHART
    ###########################################################################

    def overall_score_chart(self):
        st.subheader("Overall Strategy Scores")

        figure = self.charts.overall_score()

        st.plotly_chart(figure, width="stretch")

    ###########################################################################
    # EXECUTIVE NARRATIVE
    ###########################################################################

    def executive_narrative(self):
        st.subheader("Executive Narrative")

        narrative = self.insights.get("executive_narrative")

        if narrative is None:
            st.info("Executive narrative unavailable.")

            return

        for line in narrative:
            st.write(f"• {line}")

    ###########################################################################
    # STRENGTH ANALYSIS
    ###########################################################################

    def strength_analysis(self):
        st.subheader("Strategy Strengths")

        dataframe = self.insights.get("strength_analysis")

        if dataframe is None:
            st.info("Strength analysis unavailable.")

            return

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # WEAKNESS ANALYSIS
    ###########################################################################

    def weakness_analysis(self):
        st.subheader("Strategy Weaknesses")

        dataframe = self.insights.get("weakness_analysis")

        if dataframe is None:
            st.info("Weakness analysis unavailable.")

            return

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # RISK MATRIX
    ###########################################################################

    def risk_matrix(self):
        st.subheader("Risk Assessment")

        dataframe = self.insights.get("risk_matrix")

        if dataframe is None:
            st.info("Risk assessment unavailable.")

            return

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # OPPORTUNITY MATRIX
    ###########################################################################

    def opportunity_matrix(self):
        st.subheader("Opportunity Assessment")

        dataframe = self.insights.get("opportunity_matrix")

        if dataframe is None:
            st.info("Opportunity assessment unavailable.")

            return

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # GRADE DISTRIBUTION
    ###########################################################################

    def grade_distribution(self):
        st.subheader("Grade Distribution")

        figure = self.charts.grade_distribution()

        st.plotly_chart(figure, width="stretch")

    ###########################################################################
    # RECOMMENDATION DISTRIBUTION
    ###########################################################################

    def recommendation_distribution(self):
        st.subheader("Recommendation Distribution")

        figure = self.charts.recommendation_distribution()

        st.plotly_chart(figure, width="stretch")

    ###########################################################################
    # DASHBOARD SUMMARY
    ###########################################################################

    def dashboard_summary(self):
        st.subheader("Dashboard Summary")

        rows = [
            {"Category": "Strategies", "Value": len(self.ranked)},
            {"Category": "Best Strategy", "Value": self.ranked.iloc[0]["Strategy"]},
            {
                "Category": "Highest Score",
                "Value": round(self.ranked.iloc[0]["Overall Score"], 2),
            },
            {
                "Category": "Average Score",
                "Value": round(self.ranked["Overall Score"].mean(), 2),
            },
        ]

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # COMPLETE DASHBOARD
    ###########################################################################

    def render(self):
        st.header("Executive Dashboard")

        self.kpis()

        st.divider()

        self.executive_summary()

        st.divider()

        self.best_strategy()

        st.divider()

        self.top_five()

        st.divider()

        self.metric_leaders()

        st.divider()

        self.recommendation_summary()

        st.divider()

        self.overall_score_chart()

        st.divider()

        self.grade_distribution()

        st.divider()

        self.recommendation_distribution()

        st.divider()

        self.executive_narrative()

        st.divider()

        left, right = st.columns(2)

        with left:
            self.strength_analysis()

        with right:
            self.weakness_analysis()

        st.divider()

        left, right = st.columns(2)

        with left:
            self.risk_matrix()

        with right:
            self.opportunity_matrix()

        st.divider()

        self.dashboard_summary()
