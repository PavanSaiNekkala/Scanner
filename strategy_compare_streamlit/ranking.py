"""
Strategy Ranking Engine
"""

import numpy as np

import pandas as pd

from config import (

    WEIGHTS,

    GRADE_RULES,

    RECOMMENDATION_RULES,

    DECIMAL_PLACES

)


###########################################################################
# RANKING ENGINE
###########################################################################

class RankingEngine:

    def __init__(

        self,

        statistics

    ):

        self.df = statistics.copy()

        self._normalized = {}

    ###########################################################################
    # VALIDATE
    ###########################################################################

    def validate(self):

        if self.df.empty:

            raise ValueError(

                "Statistics dataframe is empty."

            )

        return True

    ###########################################################################
    # NORMALIZE
    ###########################################################################

    def normalize(

        self,

        series

    ):

        name = series.name

        if name in self._normalized:

            return self._normalized[

                name

            ]

        series = pd.to_numeric(

            series,

            errors="coerce"

        )

        minimum = series.min()

        maximum = series.max()

        if pd.isna(

            minimum

        ) or pd.isna(

            maximum

        ):

            normalized = pd.Series(

                0,

                index=series.index,

                dtype=float

            )

        elif maximum == minimum:

            normalized = pd.Series(

                100,

                index=series.index,

                dtype=float

            )

        else:

            normalized = (

                (

                    series

                    -

                    minimum

                )

                /

                (

                    maximum

                    -

                    minimum

                )

            ) * 100

        self._normalized[

            name

        ] = normalized

        return normalized

    ###########################################################################
    # CALCULATE WEIGHTED SCORE
    ###########################################################################

    def calculate_scores(self):

        self.validate()

        score = np.zeros(

            len(

                self.df

            ),

            dtype=float

        )

        #######################################################################
        # WEIGHTED SCORING
        #######################################################################

        for metric, weight in WEIGHTS.items():

            column = f"{metric}_Mean"

            if column not in self.df.columns:

                continue

            normalized = self.normalize(

                self.df[

                    column

                ]

            )

            contribution = (

                normalized

                *

                weight

            )

            self.df[

                f"{metric}_Normalized"

            ] = normalized.round(

                DECIMAL_PLACES

            )

            self.df[

                f"{metric}_Contribution"

            ] = contribution.round(

                DECIMAL_PLACES

            )

            score += contribution

        #######################################################################
        # FINAL SCORE
        #######################################################################

        self.df[

            "Overall Score"

        ] = np.round(

            score,

            DECIMAL_PLACES

        )

        return self.df
    
    ###########################################################################
    # ASSIGN RANK
    ###########################################################################

    def assign_rank(self):

        self.validate()

        self.df = self.df.sort_values(

            "Overall Score",

            ascending=False,

            kind="mergesort"

        )

        self.df.reset_index(

            drop=True,

            inplace=True

        )

        self.df[

            "Rank"

        ] = (

            self.df[

                "Overall Score"

            ]

            .rank(

                method="dense",

                ascending=False

            )

            .astype(

                int

            )

        )

        return self.df

    ###########################################################################
    # ASSIGN GRADE
    ###########################################################################

    def assign_grade(self):

        grades = []

        for score in self.df[

            "Overall Score"

        ]:

            grade = "F"

            for limit, label in sorted(

                GRADE_RULES.items(),

                reverse=True

            ):

                if score >= limit:

                    grade = label

                    break

            grades.append(

                grade

            )

        self.df[

            "Grade"

        ] = grades

        return self.df

    ###########################################################################
    # ASSIGN RECOMMENDATION
    ###########################################################################

    def assign_recommendation(self):

        recommendations = []

        for score in self.df[

            "Overall Score"

        ]:

            recommendation = "Reject"

            for limit, label in sorted(

                RECOMMENDATION_RULES.items(),

                reverse=True

            ):

                if score >= limit:

                    recommendation = label

                    break

            recommendations.append(

                recommendation

            )

        self.df[

            "Recommendation"

        ] = recommendations

        return self.df

    ###########################################################################
    # ASSIGN PERCENTILE
    ###########################################################################

    def assign_percentile(self):

        self.df[

            "Percentile"

        ] = (

            self.df[

                "Overall Score"

            ]

            .rank(

                pct=True

            )

            * 100

        ).round(

            DECIMAL_PLACES

        )

        return self.df

    ###########################################################################
    # ASSIGN SCORE BAND
    ###########################################################################

    def assign_score_band(self):

        bands = []

        for score in self.df[

            "Overall Score"

        ]:

            if score >= 90:

                band = "Elite"

            elif score >= 80:

                band = "Excellent"

            elif score >= 70:

                band = "Strong"

            elif score >= 60:

                band = "Average"

            elif score >= 50:

                band = "Weak"

            else:

                band = "Poor"

            bands.append(

                band

            )

        self.df[

            "Score Band"

        ] = bands

        return self.df
    
    ###########################################################################
    # FINAL RANKING
    ###########################################################################

    def rank(self):

        self.assign_rank()

        self.assign_grade()

        self.assign_recommendation()

        self.assign_percentile()

        self.assign_score_band()

        columns = [

            "Rank",

            "Strategy",

            "Overall Score",

            "Percentile",

            "Score Band",

            "Grade",

            "Recommendation"

        ]

        remaining = [

            column

            for column in self.df.columns

            if column not in columns

        ]

        self.df = self.df[

            columns

            +

            remaining

        ]

        return self.df

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top(

        self,

        n=5

    ):

        return self.rank().head(

            n

        )

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom(

        self,

        n=5

    ):

        return self.rank().tail(

            n

        )

    ###########################################################################
    # SCORE BREAKDOWN
    ###########################################################################

    def score_breakdown(self):

        contribution_columns = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Contribution"

            )

        ]

        if not contribution_columns:

            return pd.DataFrame()

        columns = [

            "Strategy",

            "Overall Score"

        ]

        columns.extend(

            contribution_columns

        )

        return self.df[

            columns

        ].copy()

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(self):

        dataframe = self.rank()

        return {

            "Strategies":

                len(

                    dataframe

                ),

            "Average Score":

                round(

                    dataframe[

                        "Overall Score"

                    ].mean(),

                    DECIMAL_PLACES

                ),

            "Highest Score":

                round(

                    dataframe[

                        "Overall Score"

                    ].max(),

                    DECIMAL_PLACES

                ),

            "Lowest Score":

                round(

                    dataframe[

                        "Overall Score"

                    ].min(),

                    DECIMAL_PLACES

                ),

            "Median Score":

                round(

                    dataframe[

                        "Overall Score"

                    ].median(),

                    DECIMAL_PLACES

                ),

            "Top Strategy":

                dataframe.iloc[

                    0

                ][

                    "Strategy"

                ],

            "Top Grade":

                dataframe.iloc[

                    0

                ][

                    "Grade"

                ],

            "Top Recommendation":

                dataframe.iloc[

                    0

                ][

                    "Recommendation"

                ]

        }

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):

        ranked = self.rank()

        return {

            "ranking":

                ranked,

            "top":

                self.top(),

            "bottom":

                self.bottom(),

            "score_breakdown":

                self.score_breakdown(),

            "summary":

                self.summary()

        }