"""
Chart Builder
"""

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

from config import (

    TOP_N,

    DECIMAL_PLACES

)


###########################################################################
# CHART ENGINE
###########################################################################

class ChartEngine:

    def __init__(

        self,

        ranked

    ):

        self.df = ranked.copy()

        self.height = 550

        self.template = "plotly_white"

    ###########################################################################
    # OVERALL SCORE BAR
    ###########################################################################

    def overall_score(self):

        if self.df.empty:

            return go.Figure()

        fig = px.bar(

            self.df,

            x="Strategy",

            y="Overall Score",

            color="Overall Score",

            text="Overall Score",

            template=self.template,

            title="Overall Strategy Score"

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside"

        )

        fig.update_layout(

            height=self.height,

            xaxis_title="Strategy",

            yaxis_title="Overall Score",

            coloraxis_colorbar_title="Score"

        )

        return fig

    ###########################################################################
    # HORIZONTAL RANKING
    ###########################################################################

    def ranking_chart(

        self,

        top_n=TOP_N

    ):

        if self.df.empty:

            return go.Figure()

        dataframe = (

            self.df

            .head(

                top_n

            )

            .sort_values(

                "Overall Score"

            )

        )

        fig = px.bar(

            dataframe,

            x="Overall Score",

            y="Strategy",

            orientation="h",

            color="Overall Score",

            text="Overall Score",

            template=self.template,

            title=f"Top {top_n} Strategies"

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside"

        )

        fig.update_layout(

            height=max(

                450,

                top_n * 40

            ),

            xaxis_title="Overall Score",

            yaxis_title="Strategy"

        )

        return fig

    ###########################################################################
    # GRADE DISTRIBUTION
    ###########################################################################

    def grade_distribution(self):

        if self.df.empty:

            return go.Figure()

        data = (

            self.df[

                "Grade"

            ]

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

            hole=0.45,

            template=self.template,

            title="Grade Distribution"

        )

        fig.update_traces(

            textinfo="percent+label"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # RECOMMENDATION DISTRIBUTION
    ###########################################################################

    def recommendation_distribution(self):

        if self.df.empty:

            return go.Figure()

        data = (

            self.df[

                "Recommendation"

            ]

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

            hole=0.45,

            template=self.template,

            title="Recommendation Distribution"

        )

        fig.update_traces(

            textinfo="percent+label"

        )

        fig.update_layout(

            height=self.height

        )

        return fig
    
    ###########################################################################
    # RADAR CHART
    ###########################################################################

    def radar(

        self,

        strategy

    ):

        if self.df.empty:

            return go.Figure()

        row = self.df[

            self.df[

                "Strategy"

            ]

            ==

            strategy

        ]

        if row.empty:

            return go.Figure()

        row = row.iloc[0]

        metrics = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Mean"

            )

        ]

        values = [

            row[

                metric

            ]

            for metric in metrics

        ]

        labels = [

            metric.replace(

                "_Mean",

                ""

            )

            for metric in metrics

        ]

        fig = go.Figure()

        fig.add_trace(

            go.Scatterpolar(

                r=values,

                theta=labels,

                fill="toself",

                name=strategy

            )

        )

        fig.update_layout(

            template=self.template,

            title=f"{strategy} Radar",

            height=self.height,

            polar=dict(

                radialaxis=dict(

                    visible=True,

                    range=[

                        0,

                        100

                    ]

                )

            )

        )

        return fig

    ###########################################################################
    # MULTI STRATEGY RADAR
    ###########################################################################

    def multi_radar(

        self,

        strategies=None

    ):

        if self.df.empty:

            return go.Figure()

        metrics = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Mean"

            )

        ]

        if strategies is None:

            strategies = self.df[

                "Strategy"

            ].head(

                3

            ).tolist()

        fig = go.Figure()

        for strategy in strategies:

            row = self.df[

                self.df[

                    "Strategy"

                ]

                ==

                strategy

            ]

            if row.empty:

                continue

            row = row.iloc[0]

            fig.add_trace(

                go.Scatterpolar(

                    r=[

                        row[

                            metric

                        ]

                        for metric in metrics

                    ],

                    theta=[

                        metric.replace(

                            "_Mean",

                            ""

                        )

                        for metric in metrics

                    ],

                    fill="toself",

                    name=strategy

                )

            )

        fig.update_layout(

            template=self.template,

            title="Strategy Comparison Radar",

            height=650,

            polar=dict(

                radialaxis=dict(

                    visible=True,

                    range=[

                        0,

                        100

                    ]

                )

            )

        )

        return fig

    ###########################################################################
    # SCATTER PLOT
    ###########################################################################

    def scatter(self):

        x = "Performance Score_Mean"

        y = "Reliability Score_Mean"

        if x not in self.df.columns:

            return go.Figure()

        if y not in self.df.columns:

            return go.Figure()

        fig = px.scatter(

            self.df,

            x=x,

            y=y,

            size="Overall Score",

            color="Overall Score",

            hover_name="Strategy",

            template=self.template,

            title="Performance vs Reliability"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # BUBBLE CHART
    ###########################################################################

    def bubble(self):

        x = "Execution Score_Mean"

        y = "Opportunity Score_Mean"

        if x not in self.df.columns:

            return go.Figure()

        if y not in self.df.columns:

            return go.Figure()

        fig = px.scatter(

            self.df,

            x=x,

            y=y,

            size="Overall Score",

            color="Grade",

            hover_name="Strategy",

            template=self.template,

            title="Execution vs Opportunity"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # HISTOGRAM
    ###########################################################################

    def histogram(self):

        if self.df.empty:

            return go.Figure()

        fig = px.histogram(

            self.df,

            x="Overall Score",

            nbins=10,

            template=self.template,

            title="Overall Score Distribution"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # BOX PLOT
    ###########################################################################

    def boxplot(self):

        if self.df.empty:

            return go.Figure()

        fig = px.box(

            self.df,

            y="Overall Score",

            color="Grade",

            template=self.template,

            title="Overall Score Spread"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # VIOLIN PLOT
    ###########################################################################

    def violin_plot(self):

        if self.df.empty:

            return go.Figure()

        fig = px.violin(

            self.df,

            y="Overall Score",

            color="Grade",

            box=True,

            points="all",

            template=self.template,

            title="Overall Score Density"

        )

        fig.update_layout(

            height=self.height

        )

        return fig
    
    ###########################################################################
    # CORRELATION HEATMAP
    ###########################################################################

    def correlation(self):

        metrics = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Mean"

            )

        ]

        if len(

            metrics

        ) == 0:

            return go.Figure()

        corr = self.df[

            metrics

        ].corr()

        fig = px.imshow(

            corr,

            text_auto=".2f",

            color_continuous_scale="RdBu",

            zmin=-1,

            zmax=1,

            template=self.template,

            title="Metric Correlation"

        )

        fig.update_layout(

            height=650

        )

        return fig

    ###########################################################################
    # WEIGHTED CONTRIBUTION
    ###########################################################################

    def contribution_chart(

        self,

        strategy

    ):

        row = self.df[

            self.df[

                "Strategy"

            ]

            ==

            strategy

        ]

        if row.empty:

            return go.Figure()

        row = row.iloc[0]

        contribution_columns = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Contribution"

            )

        ]

        if len(

            contribution_columns

        ) == 0:

            return go.Figure()

        data = pd.DataFrame({

            "Metric":

                [

                    column.replace(

                        "_Contribution",

                        ""

                    )

                    for column in contribution_columns

                ],

            "Contribution":

                [

                    row[

                        column

                    ]

                    for column in contribution_columns

                ]

        })

        fig = px.bar(

            data,

            x="Metric",

            y="Contribution",

            color="Contribution",

            text="Contribution",

            template=self.template,

            title=f"{strategy} Weighted Contribution"

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # PARALLEL COORDINATES
    ###########################################################################

    def parallel_coordinates(self):

        metrics = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Mean"

            )

        ]

        if len(

            metrics

        ) == 0:

            return go.Figure()

        fig = px.parallel_coordinates(

            self.df,

            dimensions=metrics,

            color="Overall Score",

            color_continuous_scale=px.colors.sequential.Viridis,

            title="Parallel Coordinate Analysis"

        )

        fig.update_layout(

            height=700

        )

        return fig

    ###########################################################################
    # METRIC COMPARISON
    ###########################################################################

    def metric_comparison(self):

        metrics = [

            column

            for column in self.df.columns

            if column.endswith(

                "_Mean"

            )

        ]

        if len(

            metrics

        ) == 0:

            return go.Figure()

        melted = self.df.melt(

            id_vars=[

                "Strategy"

            ],

            value_vars=metrics,

            var_name="Metric",

            value_name="Score"

        )

        melted[

            "Metric"

        ] = melted[

            "Metric"

        ].str.replace(

            "_Mean",

            "",

            regex=False

        )

        fig = px.bar(

            melted,

            x="Metric",

            y="Score",

            color="Strategy",

            barmode="group",

            template=self.template,

            title="Metric Comparison"

        )

        fig.update_layout(

            height=650

        )

        return fig

    ###########################################################################
    # TOP STRATEGIES
    ###########################################################################

    def top_strategies(

        self,

        n=TOP_N

    ):

        if self.df.empty:

            return go.Figure()

        fig = px.bar(

            self.df.head(

                n

            ),

            x="Strategy",

            y="Overall Score",

            color="Grade",

            text="Overall Score",

            template=self.template,

            title=f"Top {n} Strategies"

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # BOTTOM STRATEGIES
    ###########################################################################

    def bottom_strategies(

        self,

        n=TOP_N

    ):

        if self.df.empty:

            return go.Figure()

        fig = px.bar(

            self.df.tail(

                n

            ),

            x="Strategy",

            y="Overall Score",

            color="Recommendation",

            text="Overall Score",

            template=self.template,

            title=f"Bottom {n} Strategies"

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside"

        )

        fig.update_layout(

            height=self.height

        )

        return fig

    ###########################################################################
    # METRIC TREND
    ###########################################################################

    def metric_trend(

        self,

        metric="Overall Score"

    ):

        if metric not in self.df.columns:

            return go.Figure()

        fig = px.line(

            self.df,

            x="Rank",

            y=metric,

            markers=True,

            template=self.template,

            title=f"{metric} Trend"

        )

        fig.update_layout(

            height=self.height

        )

        return fig
    
    ###########################################################################
    # DASHBOARD
    ###########################################################################

    def dashboard(self):

        return {

            "overall_score":

                self.overall_score(),

            "ranking":

                self.ranking_chart(),

            "grade_distribution":

                self.grade_distribution(),

            "recommendation_distribution":

                self.recommendation_distribution(),

            "scatter":

                self.scatter(),

            "bubble":

                self.bubble(),

            "histogram":

                self.histogram(),

            "boxplot":

                self.boxplot(),

            "violin":

                self.violin_plot(),

            "correlation":

                self.correlation(),

            "parallel":

                self.parallel_coordinates(),

            "metric_comparison":

                self.metric_comparison(),

            "top_strategies":

                self.top_strategies(),

            "bottom_strategies":

                self.bottom_strategies()

        }

    ###########################################################################
    # EXECUTIVE KPI
    ###########################################################################

    def executive_kpi(self):

        if self.df.empty:

            return {}

        return {

            "Strategies":

                len(

                    self.df

                ),

            "Average Score":

                round(

                    self.df[

                        "Overall Score"

                    ].mean(),

                    DECIMAL_PLACES

                ),

            "Highest Score":

                round(

                    self.df[

                        "Overall Score"

                    ].max(),

                    DECIMAL_PLACES

                ),

            "Lowest Score":

                round(

                    self.df[

                        "Overall Score"

                    ].min(),

                    DECIMAL_PLACES

                ),

            "Top Strategy":

                self.df.iloc[

                    0

                ][

                    "Strategy"

                ],

            "Average Percentile":

                round(

                    self.df[

                        "Percentile"

                    ].mean(),

                    DECIMAL_PLACES

                )

                if "Percentile" in self.df.columns

                else None

        }

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):

        charts = self.dashboard()

        return {

            "executive_kpi":

                self.executive_kpi(),

            "overall_score":

                charts[

                    "overall_score"

                ],

            "ranking":

                charts[

                    "ranking"

                ],

            "grade_distribution":

                charts[

                    "grade_distribution"

                ],

            "recommendation_distribution":

                charts[

                    "recommendation_distribution"

                ],

            "scatter":

                charts[

                    "scatter"

                ],

            "bubble":

                charts[

                    "bubble"

                ],

            "histogram":

                charts[

                    "histogram"

                ],

            "boxplot":

                charts[

                    "boxplot"

                ],

            "violin":

                charts[

                    "violin"

                ],

            "correlation":

                charts[

                    "correlation"

                ],

            "parallel":

                charts[

                    "parallel"

                ],

            "metric_comparison":

                charts[

                    "metric_comparison"

                ],

            "top_strategies":

                charts[

                    "top_strategies"

                ],

            "bottom_strategies":

                charts[

                    "bottom_strategies"

                ]

        }