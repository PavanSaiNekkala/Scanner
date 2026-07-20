"""
Statistics Engine
"""

import numpy as np

import pandas as pd

from config import PRIMARY_METRICS, DECIMAL_PLACES

from utils import numeric, dataframe_info

###########################################################################
# STATISTICS ENGINE
###########################################################################


class StatisticsEngine:
    def __init__(self, strategies):
        self.strategies = strategies

        self._statistics = None

    ###########################################################################
    # BUILD STRATEGY STATISTICS
    ###########################################################################

    def strategy_statistics(self):
        if self._statistics is not None:
            return self._statistics

        rows = []

        for strategy, dataframe in self.strategies.items():
            rows.append(self.calculate_strategy(strategy, dataframe))

        self._statistics = pd.DataFrame(rows)

        return self._statistics

    ###########################################################################
    # CALCULATE SINGLE STRATEGY
    ###########################################################################

    def calculate_strategy(self, strategy, dataframe):
        summary = {"Strategy": strategy}

        #######################################################################
        # PRIMARY METRICS
        #######################################################################

        for metric in PRIMARY_METRICS:
            if metric not in dataframe.columns:
                continue

            values = numeric(dataframe[metric]).dropna()

            if values.empty:
                continue

            summary[f"{metric}_Mean"] = round(values.mean(), DECIMAL_PLACES)

            summary[f"{metric}_Median"] = round(values.median(), DECIMAL_PLACES)

            summary[f"{metric}_Minimum"] = round(values.min(), DECIMAL_PLACES)

            summary[f"{metric}_Maximum"] = round(values.max(), DECIMAL_PLACES)

            summary[f"{metric}_Std"] = round(values.std(), DECIMAL_PLACES)

            summary[f"{metric}_Variance"] = round(values.var(), DECIMAL_PLACES)

            summary[f"{metric}_Q1"] = round(values.quantile(0.25), DECIMAL_PLACES)

            summary[f"{metric}_Q3"] = round(values.quantile(0.75), DECIMAL_PLACES)

        #######################################################################
        # DATASET INFORMATION
        #######################################################################

        summary["Total Stocks"] = len(dataframe)

        info = dataframe_info(dataframe)

        summary["Rows"] = info["Rows"]

        summary["Columns"] = info["Columns"]

        summary["Memory (KB)"] = info["Memory (KB)"]

        summary["Missing Values"] = int(dataframe.isna().sum().sum())

        summary["Duplicate Rows"] = int(dataframe.duplicated().sum())

        summary["Missing (%)"] = (
            round(
                (
                    dataframe.isna().sum().sum()
                    / (dataframe.shape[0] * dataframe.shape[1])
                )
                * 100,
                DECIMAL_PLACES,
            )
            if (dataframe.shape[0] * dataframe.shape[1]) > 0
            else 0
        )

        #######################################################################
        # RECOMMENDATION COUNTS
        #######################################################################

        if "Recommendation" in dataframe.columns:
            recommendations = (
                dataframe["Recommendation"].astype(str).str.strip().value_counts()
            )

            for recommendation, count in recommendations.items():
                summary[f"{recommendation}_Count"] = int(count)

        #######################################################################
        # GRADE COUNTS
        #######################################################################

        if "Grade" in dataframe.columns:
            grades = dataframe["Grade"].astype(str).str.strip().value_counts()

            for grade, count in grades.items():
                summary[f"{grade}_Count"] = int(count)

        return summary

    ###########################################################################
    # OVERALL SUMMARY
    ###########################################################################

    def overall_summary(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        numeric_df = dataframe.select_dtypes(include=np.number)

        if numeric_df.empty:
            return pd.DataFrame()

        rows = []

        for column in numeric_df.columns:
            values = numeric_df[column].dropna()

            if values.empty:
                continue

            rows.append(
                {
                    "Metric": column,
                    "Average": round(values.mean(), DECIMAL_PLACES),
                    "Median": round(values.median(), DECIMAL_PLACES),
                    "Maximum": round(values.max(), DECIMAL_PLACES),
                    "Minimum": round(values.min(), DECIMAL_PLACES),
                    "Std Dev": round(values.std(), DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        leaders = []

        for metric in PRIMARY_METRICS:
            column = f"{metric}_Mean"

            if column not in dataframe.columns:
                continue

            values = numeric(dataframe[column])

            if values.dropna().empty:
                continue

            idx = values.idxmax()

            leaders.append(
                {
                    "Metric": metric,
                    "Strategy": dataframe.loc[idx, "Strategy"],
                    "Value": round(dataframe.loc[idx, column], DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(leaders)

    ###########################################################################
    # DATA QUALITY
    ###########################################################################

    def data_quality(self):
        rows = []

        for strategy, dataframe in self.strategies.items():
            info = dataframe_info(dataframe)

            rows.append(
                {
                    "Strategy": strategy,
                    "Rows": info["Rows"],
                    "Columns": info["Columns"],
                    "Memory (KB)": info["Memory (KB)"],
                    "Missing Values": int(dataframe.isna().sum().sum()),
                    "Duplicate Rows": int(dataframe.duplicated().sum()),
                    "Completeness (%)": (
                        round(
                            (
                                1
                                - dataframe.isna().sum().sum()
                                / (dataframe.shape[0] * dataframe.shape[1])
                            )
                            * 100,
                            DECIMAL_PLACES,
                        )
                        if (dataframe.shape[0] * dataframe.shape[1]) > 0
                        else 100
                    ),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # METRIC DISTRIBUTION
    ###########################################################################

    def metric_distribution(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        rows = []

        for metric in PRIMARY_METRICS:
            column = f"{metric}_Mean"

            if column not in dataframe.columns:
                continue

            values = numeric(dataframe[column]).dropna()

            if values.empty:
                continue

            rows.append(
                {
                    "Metric": metric,
                    "Count": len(values),
                    "Mean": round(values.mean(), DECIMAL_PLACES),
                    "Median": round(values.median(), DECIMAL_PLACES),
                    "Minimum": round(values.min(), DECIMAL_PLACES),
                    "Maximum": round(values.max(), DECIMAL_PLACES),
                    "Variance": round(values.var(), DECIMAL_PLACES),
                    "Std Dev": round(values.std(), DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return {}

        summary = {"Strategies": len(dataframe)}

        score_column = "Overall Score_Mean"

        if score_column in dataframe.columns:
            scores = numeric(dataframe[score_column]).dropna()

            if not scores.empty:
                best_idx = scores.idxmax()

                worst_idx = scores.idxmin()

                summary.update(
                    {
                        "Average Score": round(scores.mean(), DECIMAL_PLACES),
                        "Median Score": round(scores.median(), DECIMAL_PLACES),
                        "Highest Score": round(scores.max(), DECIMAL_PLACES),
                        "Lowest Score": round(scores.min(), DECIMAL_PLACES),
                        "Best Strategy": dataframe.loc[best_idx, "Strategy"],
                        "Worst Strategy": dataframe.loc[worst_idx, "Strategy"],
                    }
                )

        return summary

    ###########################################################################
    # SCORE STATISTICS
    ###########################################################################

    def score_statistics(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        column = "Overall Score_Mean"

        if column not in dataframe.columns:
            return pd.DataFrame()

        values = numeric(dataframe[column]).dropna()

        if values.empty:
            return pd.DataFrame()

        statistics = {
            "Statistic": [
                "Count",
                "Mean",
                "Median",
                "Minimum",
                "Maximum",
                "Variance",
                "Std Dev",
                "Q1",
                "Q3",
            ],
            "Value": [
                len(values),
                round(values.mean(), DECIMAL_PLACES),
                round(values.median(), DECIMAL_PLACES),
                round(values.min(), DECIMAL_PLACES),
                round(values.max(), DECIMAL_PLACES),
                round(values.var(), DECIMAL_PLACES),
                round(values.std(), DECIMAL_PLACES),
                round(values.quantile(0.25), DECIMAL_PLACES),
                round(values.quantile(0.75), DECIMAL_PLACES),
            ],
        }

        return pd.DataFrame(statistics)

    ###########################################################################
    # RECOMMENDATION STATISTICS
    ###########################################################################

    def recommendation_statistics(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        columns = [
            column
            for column in dataframe.columns
            if column.endswith("_Count")
            and any(
                recommendation in column
                for recommendation in [
                    "Strong Buy",
                    "Buy",
                    "Watch",
                    "Improve",
                    "Avoid",
                    "Reject",
                ]
            )
        ]

        if not columns:
            return pd.DataFrame()

        rows = []

        for column in columns:
            rows.append(
                {
                    "Recommendation": column.replace("_Count", ""),
                    "Total": int(dataframe[column].fillna(0).sum()),
                    "Average": round(
                        dataframe[column].fillna(0).mean(), DECIMAL_PLACES
                    ),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # GRADE STATISTICS
    ###########################################################################

    def grade_statistics(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        columns = [
            column
            for column in dataframe.columns
            if column.endswith("_Count")
            and column.startswith(("A", "B", "C", "D", "F"))
        ]

        if not columns:
            return pd.DataFrame()

        rows = []

        for column in columns:
            rows.append(
                {
                    "Grade": column.replace("_Count", ""),
                    "Total": int(dataframe[column].fillna(0).sum()),
                    "Average": round(
                        dataframe[column].fillna(0).mean(), DECIMAL_PLACES
                    ),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # STRATEGY HEALTH
    ###########################################################################

    def strategy_health(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.DataFrame()

        rows = []

        score_column = "Overall Score_Mean"

        if score_column not in dataframe.columns:
            return pd.DataFrame()

        for _, row in dataframe.iterrows():
            score = row.get(score_column, np.nan)

            if pd.isna(score):
                health = "Unknown"

            elif score >= 90:
                health = "Excellent"

            elif score >= 80:
                health = "Very Good"

            elif score >= 70:
                health = "Good"

            elif score >= 60:
                health = "Average"

            elif score >= 50:
                health = "Weak"

            else:
                health = "Poor"

            rows.append(
                {
                    "Strategy": row["Strategy"],
                    "Overall Score": (
                        round(score, DECIMAL_PLACES) if not pd.isna(score) else np.nan
                    ),
                    "Health": health,
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # BEST STRATEGY
    ###########################################################################

    def best_strategy(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.Series(dtype=object)

        column = "Overall Score_Mean"

        if column not in dataframe.columns:
            return pd.Series(dtype=object)

        values = numeric(dataframe[column]).dropna()

        if values.empty:
            return pd.Series(dtype=object)

        index = values.idxmax()

        return dataframe.loc[index]

    ###########################################################################
    # WORST STRATEGY
    ###########################################################################

    def worst_strategy(self):
        dataframe = self.strategy_statistics()

        if dataframe.empty:
            return pd.Series(dtype=object)

        column = "Overall Score_Mean"

        if column not in dataframe.columns:
            return pd.Series(dtype=object)

        values = numeric(dataframe[column]).dropna()

        if values.empty:
            return pd.Series(dtype=object)

        index = values.idxmin()

        return dataframe.loc[index]

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):
        return {
            "strategy_statistics": self.strategy_statistics(),
            "overall_summary": self.overall_summary(),
            "metric_leaders": self.metric_leaders(),
            "metric_distribution": self.metric_distribution(),
            "data_quality": self.data_quality(),
            "executive_summary": self.executive_summary(),
            "score_statistics": self.score_statistics(),
            "recommendation_statistics": self.recommendation_statistics(),
            "grade_statistics": self.grade_statistics(),
            "strategy_health": self.strategy_health(),
            "best_strategy": self.best_strategy(),
            "worst_strategy": self.worst_strategy(),
        }
