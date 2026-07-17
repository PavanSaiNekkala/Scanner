"""
=============================================================
Institutional Leaderboard Engine V4

Module:
    comparison/leaderboard.py

Purpose:
    Generate institutional leaderboards from the
    Strategy Comparison Engine outputs.

Produces

    • Overall Leaderboard
    • Best Stocks
    • Best Strategies
    • Best Strategy-Stock Combinations
    • Expectancy Leaders
    • Profit Factor Leaders
    • Reliability Leaders
    • Efficiency Leaders
    • Edge Leaders
    • Opportunity Leaders

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pathlib import Path


class LeaderboardEngine:

    """
    Institutional Leaderboard Engine
    """

    def __init__(

        self,

        comparison_df: pd.DataFrame

    ):

        self.df = comparison_df.copy()

        self.overall = pd.DataFrame()

        self.stock_board = pd.DataFrame()

        self.strategy_board = pd.DataFrame()

        self.edge_board = pd.DataFrame()

        self.expectancy_board = pd.DataFrame()

        self.profit_board = pd.DataFrame()

        self.efficiency_board = pd.DataFrame()

        self.reliability_board = pd.DataFrame()

        self.opportunity_board = pd.DataFrame()

        self.summary = pd.DataFrame()


    # ---------------------------------------------------------

    def validate(self):

        """
        Validate required columns.
        """

        required = [

            "Stock",

            "Strategy",

            "Composite Score",

            "Expectancy",

            "Profit Factor",

            "Reward Risk",

            "Institution Rank",

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

    def overall_leaderboard(

        self,

        top_n=100

    ):

        """
        Overall institutional ranking.
        """

        self.overall = (

            self.df

            .sort_values(

                "Composite Score",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        self.overall.insert(

            0,

            "Leaderboard Rank",

            np.arange(

                1,

                len(self.overall)+1

            )

        )

        return self


    # ---------------------------------------------------------

    def stock_leaderboard(self):

        """
        Best strategy for every stock.
        """

        idx = (

            self.df

            .groupby(

                "Stock"

            )[

                "Composite Score"

            ]

            .idxmax()

        )

        self.stock_board = (

            self.df

            .loc[idx]

            .sort_values(

                "Composite Score",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        self.stock_board.insert(

            0,

            "Rank",

            np.arange(

                1,

                len(

                    self.stock_board

                )+1

            )

        )

        return self


    # ---------------------------------------------------------

    def strategy_leaderboard(self):

        """
        Average score by strategy.
        """

        self.strategy_board = (

            self.df

            .groupby(

                "Strategy",

                as_index=False

            )

            .agg(

                Stocks=(

                    "Stock",

                    "count"

                ),

                Composite=(

                    "Composite Score",

                    "mean"

                ),

                Expectancy=(

                    "Expectancy",

                    "mean"

                ),

                ProfitFactor=(

                    "Profit Factor",

                    "mean"

                ),

                RewardRisk=(

                    "Reward Risk",

                    "mean"

                )

            )

            .sort_values(

                "Composite",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        self.strategy_board.insert(

            0,

            "Rank",

            np.arange(

                1,

                len(

                    self.strategy_board

                )+1

            )

        )

        return self


    # ---------------------------------------------------------

    def edge_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest edge score.
        """

        if "Edge Score" not in self.df.columns:

            return self

        self.edge_board = (

            self.df

            .sort_values(

                "Edge Score",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def expectancy_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest expectancy.
        """

        self.expectancy_board = (

            self.df

            .sort_values(

                "Expectancy",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def profit_factor_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest Profit Factor.
        """

        self.profit_board = (

            self.df

            .sort_values(

                "Profit Factor",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def efficiency_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest Efficiency Score.
        """

        if "Efficiency Score" not in self.df.columns:

            return self

        self.efficiency_board = (

            self.df

            .sort_values(

                "Efficiency Score",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self
    
    # ---------------------------------------------------------

    def reliability_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest Reliability Score.
        """

        if "Reliability Score" not in self.df.columns:

            return self

        self.reliability_board = (

            self.df

            .sort_values(

                "Reliability Score",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def opportunity_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest Opportunity Score.
        """

        if "Opportunity Score" not in self.df.columns:

            return self

        self.opportunity_board = (

            self.df

            .sort_values(

                "Opportunity Score",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def risk_leaderboard(

        self,

        top_n=50

    ):

        """
        Highest Risk Score.
        """

        if "Risk Score" not in self.df.columns:

            return self

        self.risk_board = (

            self.df

            .sort_values(

                "Risk Score",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def multi_factor_leaderboard(

        self,

        top_n=100

    ):

        """
        Multi-factor institutional ranking.
        """

        board = self.df.copy()

        metrics = [

            "Composite Score",

            "Edge Score",

            "Reliability Score",

            "Efficiency Score",

            "Opportunity Score",

            "Risk Score"

        ]

        available = [

            c

            for c in metrics

            if c in board.columns

        ]

        board["Institutional Rating"] = (

            board[available]

            .mean(

                axis=1

            )

            .round(

                2

            )

        )

        board = (

            board

            .sort_values(

                "Institutional Rating",

                ascending=False

            )

            .head(

                top_n

            )

            .reset_index(

                drop=True

            )

        )

        board.insert(

            0,

            "Institutional Rank",

            np.arange(

                1,

                len(board)+1

            )

        )

        self.overall = board

        return self


    # ---------------------------------------------------------

    def summary_report(self):

        """
        Executive Summary.
        """

        self.summary = pd.DataFrame(

            {

                "Metric":[

                    "Total Records",

                    "Unique Stocks",

                    "Strategies",

                    "Average Composite",

                    "Maximum Composite",

                    "Minimum Composite"

                ],

                "Value":[

                    len(

                        self.df

                    ),

                    self.df["Stock"].nunique(),

                    self.df["Strategy"].nunique(),

                    round(

                        self.df["Composite Score"].mean(),

                        2

                    ),

                    round(

                        self.df["Composite Score"].max(),

                        2

                    ),

                    round(

                        self.df["Composite Score"].min(),

                        2

                    )

                ]

            }

        )

        return self


    # ---------------------------------------------------------

    def diagnostics(self):

        """
        Console diagnostics.
        """

        print()

        print("="*70)

        print("INSTITUTIONAL LEADERBOARD")

        print("="*70)

        print(

            f"Records      : {len(self.df)}"

        )

        print(

            f"Stocks       : {self.df['Stock'].nunique()}"

        )

        print(

            f"Strategies   : {self.df['Strategy'].nunique()}"

        )

        print(

            f"Average Score: {self.df['Composite Score'].mean():.2f}"

        )

        print(

            f"Highest Score: {self.df['Composite Score'].max():.2f}"

        )

        print(

            f"Lowest Score : {self.df['Composite Score'].min():.2f}"

        )

        print("="*70)

        print()

        return self


    # ---------------------------------------------------------

    def export(

        self,

        output="Institutional_Leaderboard.xlsx"

    ):

        """
        Export leaderboard workbook.
        """

        with pd.ExcelWriter(

            output,

            engine="openpyxl"

        ) as writer:

            self.overall.to_excel(

                writer,

                sheet_name="Overall",

                index=False

            )

            self.stock_board.to_excel(

                writer,

                sheet_name="Stocks",

                index=False

            )

            self.strategy_board.to_excel(

                writer,

                sheet_name="Strategies",

                index=False

            )

            self.expectancy_board.to_excel(

                writer,

                sheet_name="Expectancy",

                index=False

            )

            self.profit_board.to_excel(

                writer,

                sheet_name="ProfitFactor",

                index=False

            )

            self.edge_board.to_excel(

                writer,

                sheet_name="Edge",

                index=False

            )

            self.reliability_board.to_excel(

                writer,

                sheet_name="Reliability",

                index=False

            )

            self.efficiency_board.to_excel(

                writer,

                sheet_name="Efficiency",

                index=False

            )

            self.opportunity_board.to_excel(

                writer,

                sheet_name="Opportunity",

                index=False

            )

            if hasattr(

                self,

                "risk_board"

            ):

                self.risk_board.to_excel(

                    writer,

                    sheet_name="Risk",

                    index=False

                )

            self.summary.to_excel(

                writer,

                sheet_name="Summary",

                index=False

            )

        return self


    # ---------------------------------------------------------

    def run(self):

        """
        Execute complete leaderboard engine.
        """

        return (

            self

            .validate()

            .overall_leaderboard()

            .stock_leaderboard()

            .strategy_leaderboard()

            .edge_leaderboard()

            .expectancy_leaderboard()

            .profit_factor_leaderboard()

            .efficiency_leaderboard()

            .reliability_leaderboard()

            .opportunity_leaderboard()

            .risk_leaderboard()

            .multi_factor_leaderboard()

            .summary_report()

            .diagnostics()

        )


    # ---------------------------------------------------------

    def get_results(self):

        """
        Return all generated leaderboards.
        """

        return {

            "overall": self.overall,

            "stocks": self.stock_board,

            "strategies": self.strategy_board,

            "edge": self.edge_board,

            "expectancy": self.expectancy_board,

            "profit_factor": self.profit_board,

            "efficiency": self.efficiency_board,

            "reliability": self.reliability_board,

            "opportunity": self.opportunity_board,

            "risk": getattr(self, "risk_board", pd.DataFrame()),

            "summary": self.summary

        }


# ============================================================
# Convenience Function
# ============================================================

def build_leaderboards(

    comparison_df,

    output_file="Institutional_Leaderboard.xlsx"

):

    engine = (

        LeaderboardEngine(

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

        "Import build_leaderboards() from strategy_compare.py"

    )