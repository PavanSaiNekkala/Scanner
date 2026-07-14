"""
Recommendation Engine
"""

import pandas as pd


###########################################################################
# RECOMMENDATION ENGINE
###########################################################################

class RecommendationEngine:

    def __init__(

        self,

        ranked

    ):

        self.df = ranked.copy()

    ###########################################################################
    # BUILD RECOMMENDATIONS
    ###########################################################################

    def generate(self):

        recommendations = []

        for _, row in self.df.iterrows():

            recommendations.append(

                self.build_recommendation(

                    row

                )

            )

        return pd.DataFrame(

            recommendations

        )

    ###########################################################################
    # SINGLE STRATEGY
    ###########################################################################

    def build_recommendation(

        self,

        row

    ):

        strengths = []

        weaknesses = []

        #######################################################################

        if "Overall Score" in row.index:

            if row["Overall Score"] >= 90:

                strengths.append(

                    "Excellent overall performance"

                )

            elif row["Overall Score"] < 70:

                weaknesses.append(

                    "Low overall score"

                )

        #######################################################################

        metrics = [

            "Performance Score_Mean",

            "Reliability Score_Mean",

            "Execution Score_Mean",

            "Opportunity Score_Mean"

        ]

        labels = [

            "Performance",

            "Reliability",

            "Execution",

            "Opportunity"

        ]

        for metric, label in zip(

            metrics,

            labels

        ):

            if metric not in row.index:

                continue

            value = row[metric]

            if pd.isna(value):

                continue

            if value >= 80:

                strengths.append(

                    f"Strong {label}"

                )

            elif value < 60:

                weaknesses.append(

                    f"Weak {label}"

                )

        #######################################################################

        if len(strengths) == 0:

            strengths.append(

                "Balanced profile"

            )

        if len(weaknesses) == 0:

            weaknesses.append(

                "No major weakness"

            )

        return {

            "Strategy":

                row["Strategy"],

            "Overall Score":

                row["Overall Score"],

            "Grade":

                row["Grade"],

            "Recommendation":

                row["Recommendation"],

            "Strengths":

                ", ".join(

                    strengths

                ),

            "Weaknesses":

                ", ".join(

                    weaknesses

                ),

            "Deployment":

                self.deployment(

                    row["Recommendation"]

                )

        }

    ###########################################################################
    # DEPLOYMENT
    ###########################################################################

    def deployment(

        self,

        recommendation

    ):

        mapping = {

            "Strong Buy":

                "Deploy immediately",

            "Buy":

                "Deploy after validation",

            "Watch":

                "Paper trade",

            "Improve":

                "Refine strategy",

            "Avoid":

                "Not recommended",

            "Reject":

                "Discard"

        }

        return mapping.get(

            recommendation,

            "Review manually"

        )

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):

        summary = self.generate()

        return summary[

            [

                "Strategy",

                "Overall Score",

                "Grade",

                "Recommendation",

                "Deployment"

            ]

        ]

    ###########################################################################
    # DEPLOYMENT GUIDE
    ###########################################################################

    def deployment_guide(self):

        guide = self.generate()

        return guide[

            [

                "Strategy",

                "Recommendation",

                "Deployment"

            ]

        ]