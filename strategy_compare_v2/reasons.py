import pandas as pd


class ReasonGenerator:

    def __init__(self, ranked_df, strategies):

        self.rank_df = ranked_df
        self.strategies = strategies

    def generate(self):

        rows = []

        metrics = [

            "Composite Score_Mean",
            "Reliability Score_Mean",
            "Edge Score_Mean",
            "Efficiency Score_Mean",
            "Expectancy%_Mean",
            "Profit Factor_Mean",
            "Reward Risk_Mean"

        ]

        for _, row in self.rank_df.iterrows():

            strengths = []
            weaknesses = []

            for metric in metrics:

                if metric not in self.rank_df.columns:
                    continue

                value = row[metric]

                maximum = self.rank_df[metric].max()
                minimum = self.rank_df[metric].min()

                if value == maximum:
                    strengths.append(
                        f"Highest {metric.replace('_Mean','')}"
                    )

                elif value >= self.rank_df[metric].quantile(.75):

                    strengths.append(
                        f"Strong {metric.replace('_Mean','')}"
                    )

                if value == minimum:

                    weaknesses.append(
                        f"Lowest {metric.replace('_Mean','')}"
                    )

                elif value <= self.rank_df[metric].quantile(.25):

                    weaknesses.append(
                        f"Weak {metric.replace('_Mean','')}"
                    )

            rows.append({

                "Rank": row["Rank"],

                "Strategy": row["Strategy"],

                "Strengths":
                    "; ".join(strengths),

                "Weaknesses":
                    "; ".join(weaknesses)

            })

        return pd.DataFrame(rows)