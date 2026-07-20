import pandas as pd


class DashboardBuilder:
    def __init__(self, ranked_table):
        self.df = ranked_table

    def executive_summary(self):
        cols = ["Rank", "Strategy", "Overall Score", "Grade", "Recommendation"]

        return self.df[cols]

    def metric_winners(self):
        winners = []

        metrics = [c for c in self.df.columns if c.endswith("_Mean")]

        for metric in metrics:
            idx = self.df[metric].idxmax()

            winners.append(
                {
                    "Metric": metric.replace("_Mean", ""),
                    "Winner": self.df.loc[idx, "Strategy"],
                    "Value": self.df.loc[idx, metric],
                }
            )

        return pd.DataFrame(winners)

    def recommendation_distribution(self):
        rows = []

        for _, row in self.df.iterrows():
            rows.append(
                {
                    "Strategy": row["Strategy"],
                    "Recommendation": row["Recommendation"],
                    "Grade": row["Grade"],
                }
            )

        return pd.DataFrame(rows)

    def score_breakdown(self):
        cols = [
            "Strategy",
            "Overall Score_Mean",
            "Performance Score_Mean",
            "Reliability Score_Mean",
            "Execution Score_Mean",
            "Opportunity Score_Mean",
            "Overall Score",
        ]

        cols = [c for c in cols if c in self.df.columns]

        return self.df[cols]

    def top10_overlap(self, strategies):
        result = {}

        for name, df in strategies.items():
            if "Stock" not in df.columns:
                continue

            if "Overall Score" not in df.columns:
                continue

            top = df.nlargest(10, "Overall Score")["Stock"].tolist()

            result[name] = top

        return pd.DataFrame(result)
