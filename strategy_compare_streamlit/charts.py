"""
Chart Builder
"""

import plotly.express as px

import plotly.graph_objects as go


###########################################################################
# CHART ENGINE
###########################################################################

class ChartEngine:

    def __init__(

        self,

        ranked

    ):

        self.df = ranked.copy()

    ###########################################################################
    # OVERALL SCORE BAR
    ###########################################################################

    def overall_score(self):

        fig = px.bar(

            self.df,

            x="Strategy",

            y="Overall Score",

            color="Overall Score",

            text="Overall Score"

        )

        fig.update_layout(

            title="Overall Strategy Score",

            xaxis_title="Strategy",

            yaxis_title="Overall Score",

            height=500

        )

        return fig

    ###########################################################################
    # GRADE PIE
    ###########################################################################

    def grade_distribution(self):

        data = (

            self.df["Grade"]

            .value_counts()

            .reset_index()

        )

        data.columns = [

            "Grade",

            "Count"

        ]

        fig = px.pie(

            data,

            names="Grade",

            values="Count",

            title="Grade Distribution"

        )

        return fig

    ###########################################################################
    # RECOMMENDATION PIE
    ###########################################################################

    def recommendation_distribution(self):

        data = (

            self.df["Recommendation"]

            .value_counts()

            .reset_index()

        )

        data.columns = [

            "Recommendation",

            "Count"

        ]

        fig = px.pie(

            data,

            names="Recommendation",

            values="Count",

            title="Recommendation Distribution"

        )

        return fig

    ###########################################################################
    # RADAR
    ###########################################################################

    def radar(

        self,

        strategy

    ):

        row = self.df[

            self.df["Strategy"] == strategy

        ].iloc[0]

        metrics = [

            c

            for c in self.df.columns

            if c.endswith(

                "_Mean"

            )

        ]

        fig = go.Figure()

        fig.add_trace(

            go.Scatterpolar(

                r=[

                    row[m]

                    for m in metrics

                ],

                theta=[

                    m.replace(

                        "_Mean",

                        ""

                    )

                    for m in metrics

                ],

                fill="toself",

                name=strategy

            )

        )

        fig.update_layout(

            title="Strategy Radar",

            polar=dict(

                radialaxis=dict(

                    visible=True

                )

            ),

            height=600

        )

        return fig

    ###########################################################################
    # SCATTER
    ###########################################################################

    def scatter(self):

        x = "Performance Score_Mean"

        y = "Reliability Score_Mean"

        if x not in self.df.columns:

            return None

        if y not in self.df.columns:

            return None

        fig = px.scatter(

            self.df,

            x=x,

            y=y,

            size="Overall Score",

            color="Overall Score",

            hover_name="Strategy",

            title="Performance vs Reliability"

        )

        return fig

    ###########################################################################
    # HISTOGRAM
    ###########################################################################

    def histogram(self):

        fig = px.histogram(

            self.df,

            x="Overall Score",

            nbins=10,

            title="Overall Score Distribution"

        )

        return fig

    ###########################################################################
    # BOXPLOT
    ###########################################################################

    def boxplot(self):

        fig = px.box(

            self.df,

            y="Overall Score",

            title="Overall Score Spread"

        )

        return fig

    ###########################################################################
    # HEATMAP
    ###########################################################################

    def correlation(self):

        metrics = [

            c

            for c in self.df.columns

            if c.endswith(

                "_Mean"

            )

        ]

        if len(metrics) == 0:

            return None

        corr = self.df[

            metrics

        ].corr()

        fig = px.imshow(

            corr,

            text_auto=True,

            aspect="auto",

            title="Metric Correlation"

        )

        return fig

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top_strategies(

        self,

        n=10

    ):

        fig = px.bar(

            self.df.head(

                n

            ),

            x="Strategy",

            y="Overall Score",

            color="Grade",

            text="Overall Score",

            title=f"Top {n} Strategies"

        )

        return fig

    ###########################################################################
    # COMPLETE CHART SET
    ###########################################################################

    def build(self):

        return {

            "overall":

                self.overall_score(),

            "grades":

                self.grade_distribution(),

            "recommendation":

                self.recommendation_distribution(),

            "scatter":

                self.scatter(),

            "histogram":

                self.histogram(),

            "boxplot":

                self.boxplot(),

            "heatmap":

                self.correlation(),

            "top":

                self.top_strategies()

        }