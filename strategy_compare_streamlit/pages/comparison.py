"""
Strategy Comparison Page
"""

import streamlit as st

import pandas as pd


###########################################################################
# COMPARISON PAGE
###########################################################################

class ComparisonPage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.ranked = result["ranked"]

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Strategy Comparison"

        )

        if len(self.ranked) < 2:

            st.warning(

                "At least two strategies are required."

            )

            return

        left, right = st.columns(2)

        strategy_a = left.selectbox(

            "Strategy A",

            self.ranked["Strategy"],

            key="strategy_a"

        )

        strategy_b = right.selectbox(

            "Strategy B",

            self.ranked["Strategy"],

            index=min(

                1,

                len(self.ranked) - 1

            ),

            key="strategy_b"

        )

        if strategy_a == strategy_b:

            st.warning(

                "Please choose two different strategies."

            )

            return

        row_a = self.ranked[

            self.ranked["Strategy"]

            ==

            strategy_a

        ].iloc[0]

        row_b = self.ranked[

            self.ranked["Strategy"]

            ==

            strategy_b

        ].iloc[0]

        self.comparison_table(

            row_a,

            row_b

        )

        self.metric_winners(

            row_a,

            row_b

        )

    ###########################################################################
    # COMPARISON TABLE
    ###########################################################################

    def comparison_table(

        self,

        row_a,

        row_b

    ):

        st.subheader(

            "Comparison"

        )

        metrics = [

            "Overall Score",

            "Performance Score_Mean",

            "Reliability Score_Mean",

            "Execution Score_Mean",

            "Opportunity Score_Mean",

            "Grade",

            "Recommendation"

        ]

        metrics = [

            metric

            for metric in metrics

            if metric in self.ranked.columns

        ]

        rows = []

        for metric in metrics:

            value_a = row_a[metric]

            value_b = row_b[metric]

            winner = "-"

            if isinstance(

                value_a,

                (int, float)

            ) and isinstance(

                value_b,

                (int, float)

            ):

                if value_a > value_b:

                    winner = row_a["Strategy"]

                elif value_b > value_a:

                    winner = row_b["Strategy"]

                else:

                    winner = "Tie"

            rows.append({

                "Metric":

                    metric,

                row_a["Strategy"]:

                    value_a,

                row_b["Strategy"]:

                    value_b,

                "Winner":

                    winner

            })

        df = pd.DataFrame(

            rows

        )

        df = df.astype(

            str

        )

        st.dataframe(

            df,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # METRIC WINNERS
    ###########################################################################

    def metric_winners(

        self,

        row_a,

        row_b

    ):

        st.subheader(

            "Winner Summary"

        )

        numeric_metrics = [

            c

            for c in self.ranked.columns

            if c.endswith(

                "_Mean"

            )

        ]

        wins = {

            row_a["Strategy"]: 0,

            row_b["Strategy"]: 0,

            "Tie": 0

        }

        for metric in numeric_metrics:

            value_a = row_a[metric]

            value_b = row_b[metric]

            if value_a > value_b:

                wins[

                    row_a["Strategy"]

                ] += 1

            elif value_b > value_a:

                wins[

                    row_b["Strategy"]

                ] += 1

            else:

                wins["Tie"] += 1

        summary = pd.DataFrame({

            "Strategy": list(

                wins.keys()

            ),

            "Metrics Won": list(

                wins.values()

            )

        })

        summary = summary.astype(

            str

        )

        st.dataframe(

            summary,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # DIFFERENCE TABLE
    ###########################################################################

    def differences(

        self,

        row_a,

        row_b

    ):

        metrics = [

            c

            for c in self.ranked.columns

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

                "Difference":

                    round(

                        row_a[metric]

                        -

                        row_b[metric],

                        2

                    )

            })

        return pd.DataFrame(

            rows

        )