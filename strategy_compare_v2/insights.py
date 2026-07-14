import pandas as pd


class InsightEngine:

    def __init__(self, ranked_df):

        self.df = ranked_df.copy()

    ###########################################################################
    # BEST STRATEGY
    ###########################################################################

    def best_strategy(self):

        return self.df.iloc[0]

    ###########################################################################
    # WORST STRATEGY
    ###########################################################################

    def worst_strategy(self):

        return self.df.iloc[-1]

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def executive_summary(self):

        best = self.best_strategy()

        worst = self.worst_strategy()

        rows = []

        rows.append({

            "Insight":"Best Strategy",

            "Value":best["Strategy"]

        })

        rows.append({

            "Insight":"Best Overall Score",

            "Value":round(best["Overall Score"],2)

        })

        rows.append({

            "Insight":"Recommendation",

            "Value":best["Recommendation"]

        })

        rows.append({

            "Insight":"Lowest Ranked Strategy",

            "Value":worst["Strategy"]

        })

        rows.append({

            "Insight":"Lowest Score",

            "Value":round(worst["Overall Score"],2)

        })

        rows.append({

            "Insight":"Strategies Compared",

            "Value":len(self.df)

        })

        return pd.DataFrame(rows)

    ###########################################################################
    # LEADERS
    ###########################################################################

    def metric_leaders(self):

        metrics = [

            c

            for c in self.df.columns

            if c.endswith("_Mean")

        ]

        rows = []

        for metric in metrics:

            idx = self.df[metric].idxmax()

            rows.append({

                "Metric":metric.replace("_Mean",""),

                "Winner":self.df.loc[idx,"Strategy"],

                "Value":round(

                    self.df.loc[idx,metric],

                    2

                )

            })

        return pd.DataFrame(rows)

    ###########################################################################
    # DEPLOYMENT
    ###########################################################################

    def deployment(self):

        rows = []

        for _, row in self.df.iterrows():

            if row["Overall Score"] >= 90:

                decision = "Deploy"

                reason = "Excellent overall performance."

            elif row["Overall Score"] >= 80:

                decision = "Paper Trade"

                reason = "Strong strategy with good consistency."

            elif row["Overall Score"] >= 70:

                decision = "Watch"

                reason = "Promising but requires monitoring."

            else:

                decision = "Reject"

                reason = "Below acceptable threshold."

            rows.append({

                "Strategy":row["Strategy"],

                "Decision":decision,

                "Reason":reason

            })

        return pd.DataFrame(rows)