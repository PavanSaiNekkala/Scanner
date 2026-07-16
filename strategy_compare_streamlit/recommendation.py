"""
Recommendation Engine
"""

import pandas as pd

from config import (

    DECIMAL_PLACES

)


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
    # BUILD SINGLE STRATEGY
    ###########################################################################

    def build_recommendation(

        self,

        row

    ):

        strengths = self.identify_strengths(

            row

        )

        weaknesses = self.identify_weaknesses(

            row

        )

        return {

            "Strategy":

                row["Strategy"],

            "Overall Score":

                round(

                    row["Overall Score"],

                    DECIMAL_PLACES

                ),

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

                ),

            "Risk":

                self.risk_level(

                    row

                ),

            "Confidence":

                self.confidence(

                    row

                )

        }

    ###########################################################################
    # IDENTIFY STRENGTHS
    ###########################################################################

    def identify_strengths(

        self,

        row

    ):

        strengths = []

        if row.get(

            "Overall Score",

            0

        ) >= 90:

            strengths.append(

                "Excellent overall performance"

            )

        metric_labels = {

            "Performance Score_Mean":

                "Performance",

            "Reliability Score_Mean":

                "Reliability",

            "Execution Score_Mean":

                "Execution",

            "Opportunity Score_Mean":

                "Opportunity"

        }

        for metric, label in metric_labels.items():

            if metric not in row.index:

                continue

            value = row[

                metric

            ]

            if pd.isna(

                value

            ):

                continue

            if value >= 90:

                strengths.append(

                    f"Outstanding {label}"

                )

            elif value >= 80:

                strengths.append(

                    f"Strong {label}"

                )

        if len(

            strengths

        ) == 0:

            strengths.append(

                "Balanced profile"

            )

        return strengths

    ###########################################################################
    # IDENTIFY WEAKNESSES
    ###########################################################################

    def identify_weaknesses(

        self,

        row

    ):

        weaknesses = []

        if row.get(

            "Overall Score",

            100

        ) < 70:

            weaknesses.append(

                "Low overall score"

            )

        metric_labels = {

            "Performance Score_Mean":

                "Performance",

            "Reliability Score_Mean":

                "Reliability",

            "Execution Score_Mean":

                "Execution",

            "Opportunity Score_Mean":

                "Opportunity"

        }

        for metric, label in metric_labels.items():

            if metric not in row.index:

                continue

            value = row[

                metric

            ]

            if pd.isna(

                value

            ):

                continue

            if value < 50:

                weaknesses.append(

                    f"Critical {label}"

                )

            elif value < 60:

                weaknesses.append(

                    f"Weak {label}"

                )

        if len(

            weaknesses

        ) == 0:

            weaknesses.append(

                "No major weakness"

            )

        return weaknesses
    
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
    # RISK LEVEL
    ###########################################################################

    def risk_level(

        self,

        row

    ):

        score = row.get(

            "Overall Score",

            0

        )

        reliability = row.get(

            "Reliability Score_Mean",

            score

        )

        execution = row.get(

            "Execution Score_Mean",

            score

        )

        average = (

            score

            +

            reliability

            +

            execution

        ) / 3

        if average >= 90:

            return "Very Low"

        elif average >= 80:

            return "Low"

        elif average >= 70:

            return "Moderate"

        elif average >= 60:

            return "High"

        else:

            return "Very High"

    ###########################################################################
    # CONFIDENCE SCORE
    ###########################################################################

    def confidence(

        self,

        row

    ):

        metrics = [

            "Performance Score_Mean",

            "Reliability Score_Mean",

            "Execution Score_Mean",

            "Opportunity Score_Mean"

        ]

        values = []

        for metric in metrics:

            if metric in row.index:

                value = row[

                    metric

                ]

                if not pd.isna(

                    value

                ):

                    values.append(

                        value

                    )

        if len(

            values

        ) == 0:

            return 0.0

        return round(

            sum(

                values

            )

            /

            len(

                values

            ),

            DECIMAL_PLACES

        )

    ###########################################################################
    # PORTFOLIO SUITABILITY
    ###########################################################################

    def portfolio_suitability(

        self,

        row

    ):

        score = row.get(

            "Overall Score",

            0

        )

        recommendation = row.get(

            "Recommendation",

            ""

        )

        if recommendation == "Strong Buy":

            return "Core Holding"

        elif recommendation == "Buy":

            return "Portfolio Candidate"

        elif recommendation == "Watch":

            return "Watchlist"

        elif recommendation == "Improve":

            return "Experimental"

        elif recommendation == "Avoid":

            return "High Risk"

        else:

            return "Not Suitable"

    ###########################################################################
    # DEPLOYMENT PRIORITY
    ###########################################################################

    def deployment_priority(

        self,

        row

    ):

        score = row.get(

            "Overall Score",

            0

        )

        if score >= 90:

            return "Priority 1"

        elif score >= 80:

            return "Priority 2"

        elif score >= 70:

            return "Priority 3"

        elif score >= 60:

            return "Priority 4"

        else:

            return "Priority 5"
        

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):

        recommendations = self.generate()

        if recommendations.empty:

            return pd.DataFrame()

        columns = [

            "Strategy",

            "Overall Score",

            "Grade",

            "Recommendation",

            "Confidence",

            "Risk",

            "Deployment"

        ]

        columns = [

            column

            for column in columns

            if column in recommendations.columns

        ]

        return recommendations[

            columns

        ].copy()

    ###########################################################################
    # DEPLOYMENT GUIDE
    ###########################################################################

    def deployment_guide(self):

        recommendations = self.generate()

        if recommendations.empty:

            return pd.DataFrame()

        rows = []

        for _, row in recommendations.iterrows():

            rows.append({

                "Strategy":

                    row["Strategy"],

                "Recommendation":

                    row["Recommendation"],

                "Deployment":

                    row["Deployment"],

                "Priority":

                    self.deployment_priority(

                        row

                    ),

                "Portfolio":

                    self.portfolio_suitability(

                        row

                    )

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # STRATEGY MATRIX
    ###########################################################################

    def strategy_matrix(self):

        recommendations = self.generate()

        if recommendations.empty:

            return pd.DataFrame()

        rows = []

        for _, row in recommendations.iterrows():

            rows.append({

                "Strategy":

                    row["Strategy"],

                "Overall Score":

                    row["Overall Score"],

                "Recommendation":

                    row["Recommendation"],

                "Confidence":

                    row["Confidence"],

                "Risk":

                    row["Risk"],

                "Priority":

                    self.deployment_priority(

                        row

                    ),

                "Portfolio":

                    self.portfolio_suitability(

                        row

                    )

            })

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # RECOMMENDATION STATISTICS
    ###########################################################################

    def statistics(self):

        recommendations = self.generate()

        if recommendations.empty:

            return {}

        return {

            "Strategies":

                len(

                    recommendations

                ),

            "Strong Buy":

                int(

                    (

                        recommendations[

                            "Recommendation"

                        ]

                        ==

                        "Strong Buy"

                    ).sum()

                ),

            "Buy":

                int(

                    (

                        recommendations[

                            "Recommendation"

                        ]

                        ==

                        "Buy"

                    ).sum()

                ),

            "Watch":

                int(

                    (

                        recommendations[

                            "Recommendation"

                        ]

                        ==

                        "Watch"

                    ).sum()

                ),

            "Improve":

                int(

                    (

                        recommendations[

                            "Recommendation"

                        ]

                        ==

                        "Improve"

                    ).sum()

                ),

            "Avoid":

                int(

                    (

                        recommendations[

                            "Recommendation"

                        ]

                        ==

                        "Avoid"

                    ).sum()

                ),

            "Reject":

                int(

                    (

                        recommendations[

                            "Recommendation"

                        ]

                        ==

                        "Reject"

                    ).sum()

                ),

            "Average Confidence":

                round(

                    recommendations[

                        "Confidence"

                    ].mean(),

                    DECIMAL_PLACES

                )

        }

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):

        recommendations = self.generate()

        return {

            "recommendations":

                recommendations,

            "executive_summary":

                self.executive_summary(),

            "deployment_guide":

                self.deployment_guide(),

            "strategy_matrix":

                self.strategy_matrix(),

            "statistics":

                self.statistics()

        }