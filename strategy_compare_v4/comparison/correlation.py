"""
=============================================================
Institutional Correlation Engine V4

Module:
    comparison/correlation.py

Purpose:
    Analyze similarity and diversification between
    strategies using institutional-level correlation
    analysis.

Outputs

    • Pearson Correlation
    • Spearman Correlation
    • Kendall Correlation
    • Strategy Similarity
    • Stock Similarity
    • Diversification Score
    • Correlation Ranking

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class CorrelationEngine:

    """
    Institutional Correlation Engine
    """

    def __init__(

        self,

        comparison_df: pd.DataFrame

    ):

        self.df = comparison_df.copy()

        self.strategy_matrix = pd.DataFrame()

        self.stock_matrix = pd.DataFrame()

        self.pearson = pd.DataFrame()

        self.spearman = pd.DataFrame()

        self.kendall = pd.DataFrame()

        self.diversification = pd.DataFrame()

        self.summary = pd.DataFrame()


    # ---------------------------------------------------------

    def validate(self):

        """
        Validate required columns.
        """

        required = [

            "Stock",

            "Strategy",

            "Composite Score"

        ]

        missing = [

            c

            for c in required

            if c not in self.df.columns

        ]

        if missing:

            raise ValueError(

                "Missing columns:\n"

                +

                "\n".join(missing)

            )

        return self


    # ---------------------------------------------------------

    def create_strategy_matrix(self):

        """
        Strategy vs Stock matrix.
        """

        self.strategy_matrix = (

            self.df

            .pivot_table(

                index="Stock",

                columns="Strategy",

                values="Composite Score",

                aggfunc="mean"

            )

        )

        return self


    # ---------------------------------------------------------

    def create_stock_matrix(self):

        """
        Stock similarity matrix.
        """

        self.stock_matrix = (

            self.df

            .pivot_table(

                index="Strategy",

                columns="Stock",

                values="Composite Score",

                aggfunc="mean"

            )

        )

        return self


    # ---------------------------------------------------------

    def pearson_correlation(self):

        """
        Pearson correlation.
        """

        self.pearson = (

            self.strategy_matrix

            .corr(

                method="pearson"

            )

        )

        return self


    # ---------------------------------------------------------

    def spearman_correlation(self):

        """
        Spearman correlation.
        """

        self.spearman = (

            self.strategy_matrix

            .corr(

                method="spearman"

            )

        )

        return self


    # ---------------------------------------------------------

    def kendall_correlation(self):

        """
        Kendall correlation.
        """

        self.kendall = (

            self.strategy_matrix

            .corr(

                method="kendall"

            )

        )

        return self


    # ---------------------------------------------------------

    def diversification_score(self):

        """
        Diversification score
        based on Pearson correlation.
        """

        corr = self.pearson.copy()

        np.fill_diagonal(

            corr.values,

            np.nan

        )

        score = (

            1

            -

            corr.abs().mean()

        ) * 100

        self.diversification = pd.DataFrame(

            {

                "Strategy":

                    score.index,

                "Diversification Score":

                    score.round(2)

            }

        )

        return self


    # ---------------------------------------------------------

    def similarity_rank(self):

        """
        Rank diversification.
        """

        self.diversification = (

            self.diversification

            .sort_values(

                "Diversification Score",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        self.diversification.insert(

            0,

            "Rank",

            np.arange(

                1,

                len(

                    self.diversification

                ) + 1

            )

        )

        return self


    # ---------------------------------------------------------

    def summary_report(self):

        """
        Executive summary.
        """

        self.summary = pd.DataFrame(

            {

                "Metric":[

                    "Strategies",

                    "Stocks",

                    "Average Diversification",

                    "Maximum Diversification",

                    "Minimum Diversification"

                ],

                "Value":[

                    self.df["Strategy"].nunique(),

                    self.df["Stock"].nunique(),

                    round(

                        self.diversification[

                            "Diversification Score"

                        ].mean(),

                        2

                    ),

                    round(

                        self.diversification[

                            "Diversification Score"

                        ].max(),

                        2

                    ),

                    round(

                        self.diversification[

                            "Diversification Score"

                        ].min(),

                        2

                    )

                ]

            }

        )

        return self
    
    # ---------------------------------------------------------

    def classify_correlations(self):

        """
        Classify pairwise strategy correlations.
        """

        corr = self.pearson.copy()

        rows = []

        for i in corr.index:

            for j in corr.columns:

                if i >= j:

                    continue

                value = corr.loc[i, j]

                if pd.isna(value):

                    continue

                abs_corr = abs(value)

                if abs_corr >= 0.90:

                    level = "Very High"

                elif abs_corr >= 0.75:

                    level = "High"

                elif abs_corr >= 0.50:

                    level = "Moderate"

                elif abs_corr >= 0.25:

                    level = "Low"

                else:

                    level = "Very Low"

                rows.append(

                    {

                        "Strategy A": i,

                        "Strategy B": j,

                        "Correlation": round(value, 4),

                        "Strength": level

                    }

                )

        self.correlation_pairs = (

            pd.DataFrame(rows)

            .sort_values(

                "Correlation",

                ascending=False

            )

            .reset_index(drop=True)

        )

        return self


    # ---------------------------------------------------------

    def detect_clusters(self):

        """
        Detect highly similar strategies.
        """

        clusters = []

        for _, row in self.correlation_pairs.iterrows():

            if abs(row["Correlation"]) >= 0.80:

                clusters.append(row)

        self.cluster_report = pd.DataFrame(clusters)

        return self


    # ---------------------------------------------------------

    def heatmap_matrix(self):

        """
        Rounded matrix for heatmaps.
        """

        self.heatmap = (

            self.pearson

            .round(3)

        )

        return self


    # ---------------------------------------------------------

    def diagnostics(self):

        """
        Console diagnostics.
        """

        print()

        print("=" * 70)

        print("INSTITUTIONAL CORRELATION ENGINE")

        print("=" * 70)

        print(

            f"Strategies : {self.df['Strategy'].nunique()}"

        )

        print(

            f"Stocks     : {self.df['Stock'].nunique()}"

        )

        print(

            f"Average Diversification : "

            f"{self.diversification['Diversification Score'].mean():.2f}"

        )

        print(

            f"Maximum Diversification : "

            f"{self.diversification['Diversification Score'].max():.2f}"

        )

        print(

            f"Highly Correlated Pairs : "

            f"{len(self.cluster_report)}"

        )

        print("=" * 70)

        print()

        return self


    # ---------------------------------------------------------

    def export(

        self,

        output="Institutional_Correlation.xlsx"

    ):

        """
        Export workbook.
        """

        with pd.ExcelWriter(

            output,

            engine="openpyxl"

        ) as writer:

            self.pearson.to_excel(

                writer,

                sheet_name="Pearson"

            )

            self.spearman.to_excel(

                writer,

                sheet_name="Spearman"

            )

            self.kendall.to_excel(

                writer,

                sheet_name="Kendall"

            )

            self.heatmap.to_excel(

                writer,

                sheet_name="Heatmap"

            )

            self.diversification.to_excel(

                writer,

                sheet_name="Diversification",

                index=False

            )

            self.correlation_pairs.to_excel(

                writer,

                sheet_name="Correlation Pairs",

                index=False

            )

            self.cluster_report.to_excel(

                writer,

                sheet_name="Clusters",

                index=False

            )

            self.summary.to_excel(

                writer,

                sheet_name="Summary",

                index=False

            )

        return self


    # ---------------------------------------------------------

    def get_results(self):

        """
        Return all generated reports.
        """

        return {

            "pearson": self.pearson,

            "spearman": self.spearman,

            "kendall": self.kendall,

            "heatmap": self.heatmap,

            "diversification": self.diversification,

            "pairs": self.correlation_pairs,

            "clusters": self.cluster_report,

            "summary": self.summary

        }


    # ---------------------------------------------------------

    def run(self):

        """
        Execute complete pipeline.
        """

        return (

            self

            .validate()

            .create_strategy_matrix()

            .create_stock_matrix()

            .pearson_correlation()

            .spearman_correlation()

            .kendall_correlation()

            .diversification_score()

            .similarity_rank()

            .summary_report()

            .classify_correlations()

            .detect_clusters()

            .heatmap_matrix()

            .diagnostics()

        )


# ==========================================================
# Convenience Function
# ==========================================================

def analyze_correlations(

    comparison_df,

    output_file="Institutional_Correlation.xlsx"

):

    engine = (

        CorrelationEngine(

            comparison_df

        )

        .run()

    )

    engine.export(

        output_file

    )

    return engine


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    print(

        "Import analyze_correlations() from strategy_compare.py"

    )