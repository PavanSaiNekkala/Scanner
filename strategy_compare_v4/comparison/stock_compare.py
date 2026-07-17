"""
=============================================================
Institutional Stock Comparison Engine V4

Module:
    comparison/stock_compare.py

Purpose:
    Compare all strategies for every stock and identify
    the best performing strategy.

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pathlib import Path


class StockComparisonEngine:

    """
    Institutional Stock Comparison Engine
    """

    def __init__(self, comparison_df):

        self.df = comparison_df.copy()

        self.stock_summary = pd.DataFrame()

        self.stock_rankings = pd.DataFrame()

        self.consistency = pd.DataFrame()

        self.best_strategies = pd.DataFrame()

        self.recommendations = pd.DataFrame()

        self.statistics = pd.DataFrame()


    # ----------------------------------------------------------

    def validate(self):

        required = [

            "Stock",

            "Strategy",

            "Composite Score",

            "Expectancy",

            "Profit Factor",

            "Reward Risk"

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


    # ----------------------------------------------------------

    def rank_within_stock(self):

        """
        Rank strategies for each stock.
        """

        self.df["Strategy Rank"] = (

            self.df

            .groupby("Stock")["Composite Score"]

            .rank(

                ascending=False,

                method="dense"

            )

        )

        return self


    # ----------------------------------------------------------

    def best_strategy(self):

        """
        Highest ranked strategy
        for every stock.
        """

        idx = (

            self.df

            .groupby("Stock")["Composite Score"]

            .idxmax()

        )

        self.best_strategies = (

            self.df

            .loc[idx]

            .sort_values(

                "Composite Score",

                ascending=False

            )

            .reset_index(drop=True)

        )

        return self


    # ----------------------------------------------------------

    def summarize_stock(self):

        """
        Aggregate statistics
        for every stock.
        """

        self.stock_summary = (

            self.df

            .groupby(

                "Stock",

                as_index=False

            )

            .agg(

                Strategies=(

                    "Strategy",

                    "count"

                ),

                AverageComposite=(

                    "Composite Score",

                    "mean"

                ),

                MaximumComposite=(

                    "Composite Score",

                    "max"

                ),

                MinimumComposite=(

                    "Composite Score",

                    "min"

                ),

                AverageExpectancy=(

                    "Expectancy",

                    "mean"

                ),

                AverageProfitFactor=(

                    "Profit Factor",

                    "mean"

                ),

                AverageRewardRisk=(

                    "Reward Risk",

                    "mean"

                )

            )

        )

        return self


    # ----------------------------------------------------------

    def stock_statistics(self):

        """
        Dispersion statistics.
        """

        stats = (

            self.df

            .groupby("Stock")

            .agg(

                StdComposite=(

                    "Composite Score",

                    "std"

                ),

                Variance=(

                    "Composite Score",

                    "var"

                ),

                Median=(

                    "Composite Score",

                    "median"

                ),

                Mean=(

                    "Composite Score",

                    "mean"

                )

            )

            .reset_index()

        )

        self.statistics = stats

        return self


    # ----------------------------------------------------------

    def consistency_score(self):

        """
        Lower variation =
        higher consistency.
        """

        self.consistency = (

            self.statistics.copy()

        )

        self.consistency["Consistency Score"] = (

            100

            -

            self.consistency["StdComposite"]

            .fillna(0)

        ).clip(

            lower=0,

            upper=100

        )

        return self


    # ----------------------------------------------------------

    def merge_results(self):

        """
        Merge all stock level
        statistics.
        """

        self.stock_rankings = (

            self.stock_summary

            .merge(

                self.consistency[

                    [

                        "Stock",

                        "Consistency Score"

                    ]

                ],

                on="Stock",

                how="left"

            )

        )

        return self
    
    # ----------------------------------------------------------

    def agreement_score(self):

        """
        Measure how consistently
        strategies favour a stock.
        """

        agreement = (

            self.df

            .groupby("Stock")

            .agg(

                CompositeStd=(

                    "Composite Score",

                    "std"

                ),

                CompositeMean=(

                    "Composite Score",

                    "mean"

                )

            )

            .reset_index()

        )

        agreement["Agreement Score"] = (

            100

            -

            agreement["CompositeStd"]

            .fillna(0)

        ).clip(

            0,

            100

        )

        self.stock_rankings = (

            self.stock_rankings

            .merge(

                agreement[

                    [

                        "Stock",

                        "Agreement Score"

                    ]

                ],

                on="Stock",

                how="left"

            )

        )

        return self


    # ----------------------------------------------------------

    def institutional_score(self):

        """
        Final stock score.
        """

        self.stock_rankings[

            "Institutional Score"

        ] = (

            self.stock_rankings[

                "AverageComposite"

            ] * 0.60

            +

            self.stock_rankings[

                "Consistency Score"

            ] * 0.25

            +

            self.stock_rankings[

                "Agreement Score"

            ] * 0.15

        ).round(2)

        return self


    # ----------------------------------------------------------

    def rank_stocks(self):

        """
        Global stock ranking.
        """

        self.stock_rankings = (

            self.stock_rankings

            .sort_values(

                "Institutional Score",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        self.stock_rankings[

            "Institution Rank"

        ] = np.arange(

            1,

            len(

                self.stock_rankings

            ) + 1

        )

        return self


    # ----------------------------------------------------------

    def recommendation(self):

        """
        Institutional recommendation.
        """

        score = self.stock_rankings[

            "Institutional Score"

        ]

        conditions = [

            score >= 90,

            score >= 80,

            score >= 70,

            score >= 60,

            score >= 50

        ]

        values = [

            "Strong Buy",

            "Buy",

            "Watch",

            "Improve",

            "Avoid"

        ]

        self.stock_rankings[

            "Recommendation"

        ] = np.select(

            conditions,

            values,

            default="Reject"

        )

        return self


    # ----------------------------------------------------------

    def top_opportunities(

        self,

        top_n=25

    ):

        """
        Top ranked stocks.
        """

        self.best_strategies = (

            self.stock_rankings

            .head(

                top_n

            )

            .copy()

        )

        return self


    # ----------------------------------------------------------

    def diagnostics(self):

        """
        Diagnostics.
        """

        self.diagnostic_report = {

            "Stocks":

                len(

                    self.stock_rankings

                ),

            "Strategies":

                self.df[

                    "Strategy"

                ].nunique(),

            "Average Score":

                round(

                    self.stock_rankings[

                        "Institutional Score"

                    ].mean(),

                    2

                ),

            "Highest Score":

                round(

                    self.stock_rankings[

                        "Institutional Score"

                    ].max(),

                    2

                ),

            "Lowest Score":

                round(

                    self.stock_rankings[

                        "Institutional Score"

                    ].min(),

                    2

                )

        }

        return self


    # ----------------------------------------------------------

    def export(

        self,

        output="Stock_Comparison.xlsx"

    ):

        """
        Export reports.
        """

        with pd.ExcelWriter(

            output,

            engine="openpyxl"

        ) as writer:

            self.df.to_excel(

                writer,

                sheet_name="All Strategies",

                index=False

            )

            self.stock_rankings.to_excel(

                writer,

                sheet_name="Stock Rankings",

                index=False

            )

            self.best_strategies.to_excel(

                writer,

                sheet_name="Top Opportunities",

                index=False

            )

            self.statistics.to_excel(

                writer,

                sheet_name="Statistics",

                index=False

            )

        return self


    # ----------------------------------------------------------

    def run(self):

        """
        Execute stock comparison.
        """

        return (

            self

            .validate()

            .rank_within_stock()

            .best_strategy()

            .summarize_stock()

            .stock_statistics()

            .consistency_score()

            .merge_results()

            .agreement_score()

            .institutional_score()

            .rank_stocks()

            .recommendation()

            .top_opportunities()

            .diagnostics()

        )


# ============================================================
# Convenience Function
# ============================================================

def compare_stocks(

    comparison_df,

    output_file="Stock_Comparison.xlsx"

):

    engine = (

        StockComparisonEngine(

            comparison_df

        )

        .run()

    )

    engine.export(

        output_file

    )

    return engine


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print(

        "Use compare_stocks() from strategy_compare.py"

    )