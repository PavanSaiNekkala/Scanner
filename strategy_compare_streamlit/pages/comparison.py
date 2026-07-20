"""
Strategy Comparison Page
"""

import streamlit as st

import pandas as pd

from charts import ChartEngine

###########################################################################
# COMPARISON PAGE
###########################################################################


class ComparisonPage:
    def __init__(self, result):
        self.result = result

        self.ranked = result["ranked"]

        self.charts = ChartEngine(self.ranked)

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):
        st.header("Strategy Comparison")

        if len(self.ranked) < 2:
            st.warning("At least two strategies are required.")

            return

        row_a, row_b = self.strategy_selector()

        if row_a is None:
            return

        st.divider()

        self.kpis(row_a, row_b)

        st.divider()

        self.comparison_table(row_a, row_b)

    ###########################################################################
    # STRATEGY SELECTOR
    ###########################################################################

    def strategy_selector(self):
        left, right = st.columns(2)

        strategy_a = left.selectbox(
            "Strategy A", self.ranked["Strategy"], key="comparison_a"
        )

        strategy_b = right.selectbox(
            "Strategy B",
            self.ranked["Strategy"],
            index=min(1, len(self.ranked) - 1),
            key="comparison_b",
        )

        if strategy_a == strategy_b:
            st.warning("Please select two different strategies.")

            return None, None

        row_a = self.ranked[self.ranked["Strategy"] == strategy_a].iloc[0]

        row_b = self.ranked[self.ranked["Strategy"] == strategy_b].iloc[0]

        return row_a, row_b

    ###########################################################################
    # KPI CARDS
    ###########################################################################

    def kpis(self, row_a, row_b):
        st.subheader("Comparison KPIs")

        col1, col2 = st.columns(2)

        col1.metric(
            row_a["Strategy"], round(row_a["Overall Score"], 2), row_a["Recommendation"]
        )

        col2.metric(
            row_b["Strategy"], round(row_b["Overall Score"], 2), row_b["Recommendation"]
        )

    ###########################################################################
    # COMPARISON TABLE
    ###########################################################################

    def comparison_table(self, row_a, row_b):
        st.subheader("Metric Comparison")

        metrics = [
            "Overall Score",
            "Performance Score_Mean",
            "Reliability Score_Mean",
            "Execution Score_Mean",
            "Opportunity Score_Mean",
            "Grade",
            "Recommendation",
        ]

        metrics = [metric for metric in metrics if metric in self.ranked.columns]

        rows = []

        for metric in metrics:
            value_a = row_a[metric]

            value_b = row_b[metric]

            winner = "-"

            if isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
                if value_a > value_b:
                    winner = row_a["Strategy"]

                elif value_b > value_a:
                    winner = row_b["Strategy"]

                else:
                    winner = "Tie"

            rows.append(
                {
                    "Metric": metric,
                    row_a["Strategy"]: value_a,
                    row_b["Strategy"]: value_b,
                    "Winner": winner,
                }
            )

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # WINNER SUMMARY
    ###########################################################################

    def winner_summary(self, row_a, row_b):
        st.subheader("Winner Summary")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        wins = {row_a["Strategy"]: 0, row_b["Strategy"]: 0, "Tie": 0}

        for metric in metrics:
            value_a = row_a[metric]

            value_b = row_b[metric]

            if value_a > value_b:
                wins[row_a["Strategy"]] += 1

            elif value_b > value_a:
                wins[row_b["Strategy"]] += 1

            else:
                wins["Tie"] += 1

        summary = pd.DataFrame(
            {"Strategy": list(wins.keys()), "Metrics Won": list(wins.values())}
        )

        summary = summary.astype(str)

        st.dataframe(summary, width="stretch", hide_index=True)

    ###########################################################################
    # DIFFERENCE TABLE
    ###########################################################################

    def difference_table(self, row_a, row_b):
        st.subheader("Difference Analysis")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            difference = round(row_a[metric] - row_b[metric], 2)

            rows.append(
                {"Metric": metric.replace("_Mean", ""), "Difference": difference}
            )

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # PERCENTAGE DIFFERENCE
    ###########################################################################

    def percentage_difference(self, row_a, row_b):
        st.subheader("Percentage Difference")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            base = row_b[metric]

            if base == 0:
                percentage = 0

            else:
                percentage = round(((row_a[metric] - base) / base) * 100, 2)

            rows.append(
                {"Metric": metric.replace("_Mean", ""), "Difference %": percentage}
            )

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # METRIC ADVANTAGE
    ###########################################################################

    def metric_advantage(self, row_a, row_b):
        st.subheader("Metric Advantage")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            value_a = row_a[metric]

            value_b = row_b[metric]

            if value_a > value_b:
                leader = row_a["Strategy"]

            elif value_b > value_a:
                leader = row_b["Strategy"]

            else:
                leader = "Tie"

            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Leader": leader,
                    "Margin": round(abs(value_a - value_b), 2),
                }
            )

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # RADAR COMPARISON
    ###########################################################################

    def radar_comparison(self, row_a, row_b):
        st.subheader("Radar Comparison")

        figure = self.charts.multi_radar([row_a["Strategy"], row_b["Strategy"]])

        st.plotly_chart(figure, width="stretch")

    ###########################################################################
    # BAR COMPARISON
    ###########################################################################

    def bar_comparison(self, row_a, row_b):
        st.subheader("Metric Comparison Chart")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    row_a["Strategy"]: row_a[metric],
                    row_b["Strategy"]: row_b[metric],
                }
            )

        dataframe = pd.DataFrame(rows)

        st.bar_chart(dataframe.set_index("Metric"), width="stretch")

    ###########################################################################
    # STRENGTH COMPARISON
    ###########################################################################

    def strength_comparison(self, row_a, row_b):
        st.subheader("Strength Comparison")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            if row_a[metric] >= 80:
                leader = row_a["Strategy"]

            elif row_b[metric] >= 80:
                leader = row_b["Strategy"]

            else:
                leader = "-"

            rows.append({"Metric": metric.replace("_Mean", ""), "Strongest": leader})

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # WEAKNESS COMPARISON
    ###########################################################################

    def weakness_comparison(self, row_a, row_b):
        st.subheader("Weakness Comparison")

        metrics = [column for column in self.ranked.columns if column.endswith("_Mean")]

        rows = []

        for metric in metrics:
            if row_a[metric] < 60:
                weaker = row_a["Strategy"]

            elif row_b[metric] < 60:
                weaker = row_b["Strategy"]

            else:
                weaker = "-"

            rows.append(
                {"Metric": metric.replace("_Mean", ""), "Needs Improvement": weaker}
            )

        dataframe = pd.DataFrame(rows)

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # EXECUTIVE COMPARISON SUMMARY
    ###########################################################################

    def executive_summary(self, row_a, row_b):
        st.subheader("Executive Comparison Summary")

        winner = (
            row_a["Strategy"]
            if row_a["Overall Score"] > row_b["Overall Score"]
            else row_b["Strategy"]
        )

        summary = pd.DataFrame(
            {
                "Metric": ["Strategy A", "Strategy B", "Winner", "Winning Score"],
                "Value": [
                    row_a["Strategy"],
                    row_b["Strategy"],
                    winner,
                    round(max(row_a["Overall Score"], row_b["Overall Score"]), 2),
                ],
            }
        )

        summary = summary.astype(str)

        st.dataframe(summary, width="stretch", hide_index=True)

    ###########################################################################
    # FINAL RECOMMENDATION
    ###########################################################################

    def final_recommendation(self, row_a, row_b):
        st.subheader("Final Recommendation")

        score_a = row_a["Overall Score"]

        score_b = row_b["Overall Score"]

        if score_a > score_b:
            winner = row_a["Strategy"]

            recommendation = row_a["Recommendation"]

            margin = round(score_a - score_b, 2)

        elif score_b > score_a:
            winner = row_b["Strategy"]

            recommendation = row_b["Recommendation"]

            margin = round(score_b - score_a, 2)

        else:
            winner = "Tie"

            recommendation = "Manual Review"

            margin = 0

        result = pd.DataFrame(
            {
                "Metric": [
                    "Recommended Strategy",
                    "Recommendation",
                    "Winning Margin",
                    "Decision",
                ],
                "Value": [
                    winner,
                    recommendation,
                    margin,
                    "Deploy" if winner != "Tie" else "Review",
                ],
            }
        )

        result = result.astype(str)

        st.dataframe(result, width="stretch", hide_index=True)

    ###########################################################################
    # EXPORT PREVIEW
    ###########################################################################

    def export_preview(self):
        st.subheader("Export Information")

        if "excel" not in self.result:
            st.info("Export information unavailable.")

            return

        dataframe = pd.DataFrame(
            {"Export": ["Comparison Workbook"], "Location": [str(self.result["excel"])]}
        )

        dataframe = dataframe.astype(str)

        st.dataframe(dataframe, width="stretch", hide_index=True)

    ###########################################################################
    # COMPLETE PAGE
    ###########################################################################

    def render(self):
        st.header("Strategy Comparison")

        if len(self.ranked) < 2:
            st.warning("At least two strategies are required.")

            return

        row_a, row_b = self.strategy_selector()

        if row_a is None:
            return

        st.divider()

        self.kpis(row_a, row_b)

        st.divider()

        self.comparison_table(row_a, row_b)

        st.divider()

        self.winner_summary(row_a, row_b)

        st.divider()

        self.difference_table(row_a, row_b)

        st.divider()

        self.percentage_difference(row_a, row_b)

        st.divider()

        self.metric_advantage(row_a, row_b)

        st.divider()

        self.radar_comparison(row_a, row_b)

        st.divider()

        self.bar_comparison(row_a, row_b)

        st.divider()

        left, right = st.columns(2)

        with left:
            self.strength_comparison(row_a, row_b)

        with right:
            self.weakness_comparison(row_a, row_b)

        st.divider()

        self.executive_summary(row_a, row_b)

        st.divider()

        self.final_recommendation(row_a, row_b)

        st.divider()

        self.export_preview()
