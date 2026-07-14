"""
Portfolio Statistics Engine
"""

import numpy as np

import pandas as pd


###########################################################################
# STATISTICS ENGINE
###########################################################################

class StatisticsReport:

    def __init__(

        self,

        ranked

    ):

        self.df = ranked.copy()

    ###########################################################################
    # OVERALL SUMMARY
    ###########################################################################

    def overall_summary(self):

        summary = {

            "Total Strategies":

                len(

                    self.df

                ),

            "Average Score":

                round(

                    self.df["Overall Score"].mean(),

                    2

                ),

            "Highest Score":

                round(

                    self.df["Overall Score"].max(),

                    2

                ),

            "Lowest Score":

                round(

                    self.df["Overall Score"].min(),

                    2

                ),

            "Median Score":

                round(

                    self.df["Overall Score"].median(),

                    2

                ),

            "Score Std Dev":

                round(

                    self.df["Overall Score"].std(),

                    2

                )

        }

        return pd.DataFrame(

            summary.items(),

            columns=[

                "Metric",

                "Value"

            ]

        )

    ###########################################################################
    # GRADE SUMMARY
    ###########################################################################

    def grade_summary(self):

        if "Grade" not in self.df.columns:

            return pd.DataFrame()

        grades = (

            self.df["Grade"]

            .value_counts()

            .reset_index()

        )

        grades.columns = [

            "Grade",

            "Count"

        ]

        grades["Percentage"] = (

            grades["Count"]

            /

            grades["Count"].sum()

            *

            100

        ).round(

            2

        )

        return grades

    ###########################################################################
    # RECOMMENDATION SUMMARY
    ###########################################################################

    def recommendation_summary(self):

        if "Recommendation" not in self.df.columns:

            return pd.DataFrame()

        recommendations = (

            self.df["Recommendation"]

            .value_counts()

            .reset_index()

        )

        recommendations.columns = [

            "Recommendation",

            "Count"

        ]

        recommendations["Percentage"] = (

            recommendations["Count"]

            /

            recommendations["Count"].sum()

            *

            100

        ).round(

            2

        )

        return recommendations

    ###########################################################################
    # SCORE DISTRIBUTION
    ###########################################################################

    def score_distribution(self):

        distribution = pd.DataFrame({

            "Strategy":

                self.df["Strategy"],

            "Overall Score":

                self.df["Overall Score"]

        })

        return distribution.sort_values(

            "Overall Score",

            ascending=False

        )

    ###########################################################################
    # METRIC AVERAGES
    ###########################################################################

    def metric_averages(self):

        metrics = [

            c

            for c in self.df.columns

            if c.endswith(

                "_Mean"

            )

        ]

        rows = []

        for metric in metrics:

            rows.append({

                "Metric":

                    metric.replace(

                        "_Mean",

                        ""

                    ),

                "Average":

                    round(

                        self.df[metric].mean(),

                        2

                    ),

                "Maximum":

                    round(

                        self.df[metric].max(),

                        2

                    ),

                "Minimum":

                    round(

                        self.df[metric].min(),

                        2

                    ),

                "Std Dev":

                    round(

                        self.df[metric].std(),

                        2

                    )

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top_strategies(

        self,

        n=5

    ):

        return self.df.head(

            n

        )

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom_strategies(

        self,

        n=5

    ):

        return self.df.tail(

            n

        )

    ###########################################################################
    # EXECUTIVE KPI
    ###########################################################################

    def executive_kpi(self):

        return {

            "Strategies":

                len(

                    self.df

                ),

            "Average Score":

                round(

                    self.df["Overall Score"].mean(),

                    2

                ),

            "Highest Score":

                round(

                    self.df["Overall Score"].max(),

                    2

                ),

            "Strong Buy":

                int(

                    (

                        self.df[

                            "Recommendation"

                        ]

                        ==

                        "Strong Buy"

                    ).sum()

                ),

            "Buy":

                int(

                    (

                        self.df[

                            "Recommendation"

                        ]

                        ==

                        "Buy"

                    ).sum()

                )

        }

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):

        return {

            "summary":

                self.overall_summary(),

            "grades":

                self.grade_summary(),

            "recommendations":

                self.recommendation_summary(),

            "metrics":

                self.metric_averages(),

            "distribution":

                self.score_distribution(),

            "top":

                self.top_strategies(),

            "bottom":

                self.bottom_strategies(),

            "kpi":

                self.executive_kpi()

        }