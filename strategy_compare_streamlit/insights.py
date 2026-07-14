"""
Executive Insight Engine
"""

import pandas as pd


###########################################################################
# INSIGHT ENGINE
###########################################################################

class InsightEngine:

    def __init__(

        self,

        ranked

    ):

        self.df = ranked.copy()

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):

        if self.df.empty:

            return pd.DataFrame()

        best = self.df.iloc[0]

        worst = self.df.iloc[-1]

        rows = [

            {

                "Insight": "Best Strategy",

                "Value": best["Strategy"]

            },

            {

                "Insight": "Best Overall Score",

                "Value": round(

                    best["Overall Score"],

                    2

                )

            },

            {

                "Insight": "Highest Grade",

                "Value": best["Grade"]

            },

            {

                "Insight": "Top Recommendation",

                "Value": best["Recommendation"]

            },

            {

                "Insight": "Lowest Strategy",

                "Value": worst["Strategy"]

            },

            {

                "Insight": "Lowest Score",

                "Value": round(

                    worst["Overall Score"],

                    2

                )

            }

        ]

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):

        rows = []

        metrics = [

            c

            for c in self.df.columns

            if c.endswith(

                "_Mean"

            )

        ]

        for metric in metrics:

            idx = self.df[

                metric

            ].idxmax()

            rows.append({

                "Metric":

                    metric.replace(

                        "_Mean",

                        ""

                    ),

                "Leader":

                    self.df.loc[

                        idx,

                        "Strategy"

                    ],

                "Value":

                    round(

                        self.df.loc[

                            idx,

                            metric

                        ],

                        2

                    )

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # DEPLOYMENT GUIDE
    ###########################################################################

    def deployment(self):

        rows = []

        for _, row in self.df.iterrows():

            recommendation = row[

                "Recommendation"

            ]

            if recommendation == "Strong Buy":

                action = "Deploy Immediately"

            elif recommendation == "Buy":

                action = "Deploy After Validation"

            elif recommendation == "Watch":

                action = "Paper Trade"

            elif recommendation == "Improve":

                action = "Optimize Strategy"

            elif recommendation == "Avoid":

                action = "Do Not Deploy"

            else:

                action = "Reject"

            rows.append({

                "Strategy":

                    row["Strategy"],

                "Grade":

                    row["Grade"],

                "Recommendation":

                    recommendation,

                "Deployment":

                    action

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # STRENGTHS
    ###########################################################################

    def strengths(self):

        rows = []

        metrics = [

            c

            for c in self.df.columns

            if c.endswith(

                "_Mean"

            )

        ]

        for _, row in self.df.iterrows():

            strengths = []

            for metric in metrics:

                if row[metric] >= 80:

                    strengths.append(

                        metric.replace(

                            "_Mean",

                            ""

                        )

                    )

            rows.append({

                "Strategy":

                    row["Strategy"],

                "Strengths":

                    ", ".join(

                        strengths

                    )

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # WEAKNESSES
    ###########################################################################

    def weaknesses(self):

        rows = []

        metrics = [

            c

            for c in self.df.columns

            if c.endswith(

                "_Mean"

            )

        ]

        for _, row in self.df.iterrows():

            weaknesses = []

            for metric in metrics:

                if row[metric] < 60:

                    weaknesses.append(

                        metric.replace(

                            "_Mean",

                            ""

                        )

                    )

            rows.append({

                "Strategy":

                    row["Strategy"],

                "Weaknesses":

                    ", ".join(

                        weaknesses

                    )

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # COMPLETE INSIGHT REPORT
    ###########################################################################

    def report(self):

        return {

            "executive":

                self.executive_summary(),

            "leaders":

                self.metric_leaders(),

            "deployment":

                self.deployment(),

            "strengths":

                self.strengths(),

            "weaknesses":

                self.weaknesses()

        }