"""
Executive Insight Engine
"""

import pandas as pd

from config import DECIMAL_PLACES

###########################################################################
# INSIGHT ENGINE
###########################################################################


class InsightEngine:
    def __init__(self, ranked):
        self.df = ranked.copy()

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):
        if self.df.empty:
            return pd.DataFrame()

        best = self.best_strategy()

        worst = self.worst_strategy()

        rows = [
            {"Insight": "Total Strategies", "Value": len(self.df)},
            {"Insight": "Best Strategy", "Value": best["Strategy"]},
            {
                "Insight": "Best Overall Score",
                "Value": round(best["Overall Score"], DECIMAL_PLACES),
            },
            {"Insight": "Highest Grade", "Value": best["Grade"]},
            {"Insight": "Top Recommendation", "Value": best["Recommendation"]},
            {"Insight": "Lowest Strategy", "Value": worst["Strategy"]},
            {
                "Insight": "Lowest Score",
                "Value": round(worst["Overall Score"], DECIMAL_PLACES),
            },
            {
                "Insight": "Average Score",
                "Value": round(self.df["Overall Score"].mean(), DECIMAL_PLACES),
            },
        ]

        return pd.DataFrame(rows)

    ###########################################################################
    # KPI SUMMARY
    ###########################################################################

    def kpi_summary(self):
        if self.df.empty:
            return {}

        return {
            "Strategies": len(self.df),
            "Average Score": round(self.df["Overall Score"].mean(), DECIMAL_PLACES),
            "Highest Score": round(self.df["Overall Score"].max(), DECIMAL_PLACES),
            "Lowest Score": round(self.df["Overall Score"].min(), DECIMAL_PLACES),
            "Median Score": round(self.df["Overall Score"].median(), DECIMAL_PLACES),
            "Average Percentile": (
                round(self.df["Percentile"].mean(), DECIMAL_PLACES)
                if "Percentile" in self.df.columns
                else None
            ),
        }

    ###########################################################################
    # BEST STRATEGY
    ###########################################################################

    def best_strategy(self):
        if self.df.empty:
            return pd.Series(dtype=object)

        return self.df.loc[self.df["Overall Score"].idxmax()]

    ###########################################################################
    # WORST STRATEGY
    ###########################################################################

    def worst_strategy(self):
        if self.df.empty:
            return pd.Series(dtype=object)

        return self.df.loc[self.df["Overall Score"].idxmin()]

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):
        if self.df.empty:
            return pd.DataFrame()

        rows = []

        metrics = [column for column in self.df.columns if column.endswith("_Mean")]

        for metric in metrics:
            values = pd.to_numeric(self.df[metric], errors="coerce")

            if values.dropna().empty:
                continue

            index = values.idxmax()

            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Leader": self.df.loc[index, "Strategy"],
                    "Score": round(values.loc[index], DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # METRIC LAGGARDS
    ###########################################################################

    def metric_laggards(self):
        if self.df.empty:
            return pd.DataFrame()

        rows = []

        metrics = [column for column in self.df.columns if column.endswith("_Mean")]

        for metric in metrics:
            values = pd.to_numeric(self.df[metric], errors="coerce")

            if values.dropna().empty:
                continue

            index = values.idxmin()

            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Strategy": self.df.loc[index, "Strategy"],
                    "Score": round(values.loc[index], DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # STRATEGY HIGHLIGHTS
    ###########################################################################

    def strategy_highlights(self):
        if self.df.empty:
            return pd.DataFrame()

        rows = []

        for _, row in self.df.iterrows():
            highlights = []

            metrics = [column for column in self.df.columns if column.endswith("_Mean")]

            for metric in metrics:
                value = row[metric]

                if pd.isna(value):
                    continue

                name = metric.replace("_Mean", "")

                if value >= 90:
                    highlights.append(f"Outstanding {name}")

                elif value >= 80:
                    highlights.append(f"Strong {name}")

            if not highlights:
                highlights.append("Balanced Strategy")

            rows.append(
                {"Strategy": row["Strategy"], "Highlights": ", ".join(highlights)}
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # DEPLOYMENT MATRIX
    ###########################################################################

    def deployment_matrix(self):
        if self.df.empty:
            return pd.DataFrame()

        columns = ["Strategy", "Overall Score", "Grade", "Recommendation"]

        if "Percentile" in self.df.columns:
            columns.append("Percentile")

        if "Score Band" in self.df.columns:
            columns.append("Score Band")

        matrix = self.df[columns].copy()

        matrix["Deployment"] = (
            matrix["Recommendation"]
            .map(
                {
                    "Strong Buy": "Immediate",
                    "Buy": "Validate & Deploy",
                    "Watch": "Paper Trade",
                    "Improve": "Optimize",
                    "Avoid": "Do Not Deploy",
                    "Reject": "Discard",
                }
            )
            .fillna("Review")
        )

        return matrix

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):
        if self.df.empty:
            return pd.DataFrame()

        rows = []

        metrics = [column for column in self.df.columns if column.endswith("_Mean")]

        for metric in metrics:
            values = pd.to_numeric(self.df[metric], errors="coerce")

            if values.dropna().empty:
                continue

            index = values.idxmax()

            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Leader": self.df.loc[index, "Strategy"],
                    "Score": round(values.loc[index], DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # METRIC LAGGARDS
    ###########################################################################

    def metric_laggards(self):
        if self.df.empty:
            return pd.DataFrame()

        rows = []

        metrics = [column for column in self.df.columns if column.endswith("_Mean")]

        for metric in metrics:
            values = pd.to_numeric(self.df[metric], errors="coerce")

            if values.dropna().empty:
                continue

            index = values.idxmin()

            rows.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Strategy": self.df.loc[index, "Strategy"],
                    "Score": round(values.loc[index], DECIMAL_PLACES),
                }
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # STRATEGY HIGHLIGHTS
    ###########################################################################

    def strategy_highlights(self):
        if self.df.empty:
            return pd.DataFrame()

        rows = []

        for _, row in self.df.iterrows():
            highlights = []

            metrics = [column for column in self.df.columns if column.endswith("_Mean")]

            for metric in metrics:
                value = row[metric]

                if pd.isna(value):
                    continue

                name = metric.replace("_Mean", "")

                if value >= 90:
                    highlights.append(f"Outstanding {name}")

                elif value >= 80:
                    highlights.append(f"Strong {name}")

            if not highlights:
                highlights.append("Balanced Strategy")

            rows.append(
                {"Strategy": row["Strategy"], "Highlights": ", ".join(highlights)}
            )

        return pd.DataFrame(rows)

    ###########################################################################
    # DEPLOYMENT MATRIX
    ###########################################################################

    def deployment_matrix(self):
        if self.df.empty:
            return pd.DataFrame()

        columns = ["Strategy", "Overall Score", "Grade", "Recommendation"]

        if "Percentile" in self.df.columns:
            columns.append("Percentile")

        if "Score Band" in self.df.columns:
            columns.append("Score Band")

        matrix = self.df[columns].copy()

        matrix["Deployment"] = (
            matrix["Recommendation"]
            .map(
                {
                    "Strong Buy": "Immediate",
                    "Buy": "Validate & Deploy",
                    "Watch": "Paper Trade",
                    "Improve": "Optimize",
                    "Avoid": "Do Not Deploy",
                    "Reject": "Discard",
                }
            )
            .fillna("Review")
        )

        return matrix

    ###########################################################################
    # EXECUTIVE NARRATIVE
    ###########################################################################

    def executive_narrative(self):
        if self.df.empty:
            return []

        best = self.best_strategy()

        worst = self.worst_strategy()

        average_score = round(self.df["Overall Score"].mean(), DECIMAL_PLACES)

        recommendations = self.df["Recommendation"].value_counts()

        dominant = recommendations.idxmax()

        narrative = [
            f"Total strategies evaluated: {len(self.df)}.",
            f"Best performing strategy: {best['Strategy']} "
            f"({best['Overall Score']:.{DECIMAL_PLACES}f}).",
            f"Lowest performing strategy: {worst['Strategy']} "
            f"({worst['Overall Score']:.{DECIMAL_PLACES}f}).",
            f"Average overall score: {average_score:.{DECIMAL_PLACES}f}.",
            f"Most common recommendation: {dominant}.",
            "Deployment should prioritize Strong Buy and Buy strategies.",
            "Strategies classified as Watch "
            "should undergo paper trading "
            "before live deployment.",
            "Avoid and Reject strategies "
            "require significant improvement "
            "before reconsideration.",
        ]

        return narrative

    ###########################################################################
    # DASHBOARD CARDS
    ###########################################################################

    def dashboard_cards(self):
        if self.df.empty:
            return {}

        recommendations = self.df["Recommendation"].value_counts()

        return {
            "Total Strategies": len(self.df),
            "Best Strategy": self.best_strategy()["Strategy"],
            "Best Score": round(self.best_strategy()["Overall Score"], DECIMAL_PLACES),
            "Average Score": round(self.df["Overall Score"].mean(), DECIMAL_PLACES),
            "Strong Buy": int(recommendations.get("Strong Buy", 0)),
            "Buy": int(recommendations.get("Buy", 0)),
            "Watch": int(recommendations.get("Watch", 0)),
            "Improve": int(recommendations.get("Improve", 0)),
            "Avoid": int(recommendations.get("Avoid", 0)),
            "Reject": int(recommendations.get("Reject", 0)),
        }

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):
        return {
            "executive_summary": self.executive_summary(),
            "kpi_summary": self.kpi_summary(),
            "metric_leaders": self.metric_leaders(),
            "metric_laggards": self.metric_laggards(),
            "strategy_highlights": self.strategy_highlights(),
            "deployment_matrix": self.deployment_matrix(),
            "executive_narrative": self.executive_narrative(),
            "dashboard_cards": self.dashboard_cards(),
        }
