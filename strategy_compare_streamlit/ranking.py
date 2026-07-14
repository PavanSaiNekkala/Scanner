"""
Strategy Ranking Engine
"""

import numpy as np

import pandas as pd

from config import WEIGHTS

from config import GRADE_RULES

from config import RECOMMENDATION_RULES


###########################################################################
# RANKING ENGINE
###########################################################################

class RankingEngine:

    def __init__(

        self,

        statistics

    ):

        self.df = statistics.copy()

    ###########################################################################
    # NORMALIZE
    ###########################################################################

    def normalize(

        self,

        series

    ):

        minimum = series.min()

        maximum = series.max()

        if maximum == minimum:

            return pd.Series(

                100,

                index=series.index

            )

        return (

            (

                series - minimum

            )

            /

            (

                maximum - minimum

            )

        ) * 100

    ###########################################################################
    # CALCULATE WEIGHTED SCORE
    ###########################################################################

    def calculate_scores(self):

        score = np.zeros(

            len(self.df)

        )

        for metric, weight in WEIGHTS.items():

            column = f"{metric}_Mean"

            if column not in self.df.columns:

                continue

            normalized = self.normalize(

                self.df[column]

            )

            score += (

                normalized * weight

            )

        self.df["Overall Score"] = score.round(

            2

        )

        return self.df

    ###########################################################################
    # ASSIGN RANK
    ###########################################################################

    def assign_rank(self):

        self.df = self.df.sort_values(

            "Overall Score",

            ascending=False

        )

        self.df.reset_index(

            drop=True,

            inplace=True

        )

        self.df["Rank"] = (

            self.df.index + 1

        )

        return self.df

    ###########################################################################
    # ASSIGN GRADE
    ###########################################################################

    def assign_grade(self):

        grades = []

        for value in self.df["Overall Score"]:

            grade = "F"

            for limit, label in sorted(

                GRADE_RULES.items(),

                reverse=True

            ):

                if value >= limit:

                    grade = label

                    break

            grades.append(

                grade

            )

        self.df["Grade"] = grades

        return self.df

    ###########################################################################
    # ASSIGN RECOMMENDATION
    ###########################################################################

    def assign_recommendation(self):

        recommendations = []

        for value in self.df["Overall Score"]:

            recommendation = "Reject"

            for limit, label in sorted(

                RECOMMENDATION_RULES.items(),

                reverse=True

            ):

                if value >= limit:

                    recommendation = label

                    break

            recommendations.append(

                recommendation

            )

        self.df["Recommendation"] = recommendations

        return self.df

    ###########################################################################
    # RANK TABLE
    ###########################################################################

    def rank(self):

        self.assign_rank()

        columns = [

            "Rank",

            "Strategy",

            "Overall Score",

            "Grade",

            "Recommendation"

        ]

        remaining = [

            c

            for c in self.df.columns

            if c not in columns

        ]

        self.df = self.df[

            columns + remaining

        ]

        return self.df

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top(

        self,

        n=5

    ):

        return self.df.head(

            n

        )

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom(

        self,

        n=5

    ):

        return self.df.tail(

            n

        )

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(self):

        return {

            "Strategies": len(

                self.df

            ),

            "Average Score": round(

                self.df["Overall Score"].mean(),

                2

            ),

            "Highest Score": round(

                self.df["Overall Score"].max(),

                2

            ),

            "Lowest Score": round(

                self.df["Overall Score"].min(),

                2

            )

        }