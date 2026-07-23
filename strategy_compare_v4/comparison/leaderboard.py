"""
=============================================================
Institutional Leaderboard Engine V4

Module
------
comparison/leaderboard.py

Purpose
-------
Generate institutional leaderboards from the
Strategy Comparison Engine outputs.

Produces
--------
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
• Risk Leaders

=============================================================
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    INSTITUTION_RANK,
    RECOMMENDATION,
    REQUIRED_COMPARISON_COLUMNS,
)
from strategy_compare_v4.config.recommendations import (
    assign_recommendations,
)
from strategy_compare_v4.utils.helpers import (
    require_columns,
)
from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)
from strategy_compare_v4.utils.math_utils import (
    round_dataframe,
)

logger = get_logger(__name__)


# ============================================================
# Leaderboard Engine
# ============================================================


class LeaderboardEngine:
    """
    Institutional Leaderboard Engine.

    Responsibilities
    ----------------
    • Generate overall leaderboard
    • Generate stock leaderboard
    • Generate strategy leaderboard
    • Generate metric-specific leaderboards
    • Produce executive summaries
    • Export institutional reports
    """

    def __init__(
        self,
        comparison_df: pd.DataFrame,
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

        self.risk_board = pd.DataFrame()

        self.summary = pd.DataFrame()

        self.diagnostic_report: dict = {}

        self.execution_time: float = 0.0

    # ---------------------------------------------------------
    # Validate Input
    # ---------------------------------------------------------

    def validate(self):
        """
        Validate comparison dataframe.
        """

        banner(
            logger,
            "Validating Leaderboard Input",
        )

        require_columns(
            self.df,
            REQUIRED_COMPARISON_COLUMNS,
        )

        logger.info("Validation successful.")

        logger.info(
            "Rows       : %d",
            len(self.df),
        )

        logger.info(
            "Stocks     : %d",
            self.df["Stock"].nunique(),
        )

        logger.info(
            "Strategies : %d",
            self.df["Strategy"].nunique(),
        )

        logger.info(
            "Average Composite : %.2f",
            self.df[COMPOSITE_SCORE].mean(),
        )

        return self

    # ---------------------------------------------------------
    # Overall Leaderboard
    # ---------------------------------------------------------

    def overall_leaderboard(
        self,
        top_n: int = 100,
    ):
        """
        Generate the overall institutional
        leaderboard.
        """

        ranking_column = (
            "Institutional Score"
            if "Institutional Score"
            in self.df.columns
            else COMPOSITE_SCORE
        )


        self.overall = (
            self.df
            .sort_values(
                ranking_column,
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )


        self.overall.insert(
            0,
            "Leaderboard Rank",
            np.arange(
                1,
                len(self.overall)+1,
            ),
        )


        self.overall = round_dataframe(
            self.overall,
            decimals=2,
        )


        return self

    # ---------------------------------------------------------
    # Stock Leaderboard
    # ---------------------------------------------------------

    def stock_leaderboard(self):
        """
        Generate best strategy
        for every stock.
        """

        filtered = self.df.copy()


        if "Trades" in filtered.columns:

            filtered = filtered.loc[
                filtered["Trades"] >= 30
            ]


        ranking_column = (
            "Institutional Score"
            if "Institutional Score"
            in filtered.columns
            else COMPOSITE_SCORE
        )


        idx = (
            filtered
            .groupby(
                "Stock",
            )[ranking_column]
            .idxmax()
        )


        self.stock_board = (
            filtered.loc[idx]
            .sort_values(
                ranking_column,
                ascending=False,
            )
            .reset_index(
                drop=True,
            )
        )


        self.stock_board.insert(
            0,
            INSTITUTION_RANK,
            np.arange(
                1,
                len(self.stock_board)+1,
            ),
        )

        return self

    # ---------------------------------------------------------
    # Strategy Leaderboard
    # ---------------------------------------------------------

    def strategy_leaderboard(self):
        """
        Generate strategy leaderboard
        using average institutional score.
        """

        self.strategy_board = (
            self.df
            .groupby(
                "Strategy",
            )
            .apply(
                lambda x: pd.Series(
                    {
                        "Stocks":
                            x["Stock"].count(),

                        "Composite":
                            np.average(
                                x[COMPOSITE_SCORE],
                                weights=(
                                    x["Trades"]
                                    if "Trades"
                                    in x.columns
                                    else None
                                ),
                            ),

                        "Expectancy":
                            np.average(
                                x["Expectancy"],
                                weights=(
                                    x["Trades"]
                                    if "Trades"
                                    in x.columns
                                    else None
                                ),
                            ),

                        "ProfitFactor":
                            np.average(
                                x["Profit Factor"],
                                weights=(
                                    x["Trades"]
                                    if "Trades"
                                    in x.columns
                                    else None
                                ),
                            ),

                        "RewardRisk":
                            np.average(
                                x["Reward Risk"],
                                weights=(
                                    x["Trades"]
                                    if "Trades"
                                    in x.columns
                                    else None
                                ),
                            ),
                    }
                )
            )
            .reset_index()
        )

        self.strategy_board = (
            self.strategy_board
            .sort_values(
                "Composite",
                ascending=False,
            )
            .reset_index(
                drop=True,
            )
        )


        self.strategy_board.insert(
            0,
            INSTITUTION_RANK,
            np.arange(
                1,
                len(self.strategy_board) + 1,
            ),
        )

        self.strategy_board = round_dataframe(
            self.strategy_board,
            decimals=2,
        )

        logger.info("Strategy leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Edge Leaderboard
    # ---------------------------------------------------------

    def edge_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Edge Score leaderboard.
        """

        if "Edge Score" not in self.df.columns:
            logger.warning("Edge Score not available.")

            return self

        self.edge_board = (
            self.df.sort_values(
                "Edge Score",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.edge_board = round_dataframe(
            self.edge_board,
            decimals=2,
        )

        logger.info("Edge leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Expectancy Leaderboard
    # ---------------------------------------------------------

    def expectancy_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Expectancy leaderboard.
        """

        self.expectancy_board = (
            self.df.sort_values(
                "Expectancy",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.expectancy_board = round_dataframe(
            self.expectancy_board,
            decimals=2,
        )

        logger.info("Expectancy leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Profit Factor Leaderboard
    # ---------------------------------------------------------

    def profit_factor_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Profit Factor leaderboard.
        """

        self.profit_board = (
            self.df.sort_values(
                "Profit Factor",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.profit_board = round_dataframe(
            self.profit_board,
            decimals=2,
        )

        logger.info("Profit Factor leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Efficiency Leaderboard
    # ---------------------------------------------------------

    def efficiency_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Efficiency Score leaderboard.
        """

        if "Efficiency Score" not in self.df.columns:
            logger.warning("Efficiency Score not available.")

            return self

        self.efficiency_board = (
            self.df.sort_values(
                "Efficiency Score",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.efficiency_board = round_dataframe(
            self.efficiency_board,
            decimals=2,
        )

        logger.info("Efficiency leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Reliability Leaderboard
    # ---------------------------------------------------------

    def reliability_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Reliability Score leaderboard.
        """

        if "Reliability Score" not in self.df.columns:
            logger.warning("Reliability Score not available.")

            return self

        self.reliability_board = (
            self.df.sort_values(
                "Reliability Score",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.reliability_board = round_dataframe(
            self.reliability_board,
            decimals=2,
        )

        logger.info("Reliability leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Opportunity Leaderboard
    # ---------------------------------------------------------

    def opportunity_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Opportunity Score leaderboard.
        """

        if "Opportunity Score" not in self.df.columns:
            logger.warning("Opportunity Score not available.")

            return self

        self.opportunity_board = (
            self.df.sort_values(
                "Opportunity Score",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.opportunity_board = round_dataframe(
            self.opportunity_board,
            decimals=2,
        )

        logger.info("Opportunity leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Risk Leaderboard
    # ---------------------------------------------------------

    def risk_leaderboard(
        self,
        top_n: int = 50,
    ):
        """
        Generate Risk Score leaderboard.
        """

        if "Risk Score" not in self.df.columns:
            logger.warning("Risk Score not available.")

            return self

        self.risk_board = (
            self.df.sort_values(
                "Risk Score",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )

        self.risk_board = round_dataframe(
            self.risk_board,
            decimals=2,
        )

        logger.info("Risk leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Multi-Factor Leaderboard
    # ---------------------------------------------------------

    def multi_factor_leaderboard(
        self,
        top_n: int = 100,
    ):
        """
        Generate institutional multi-factor
        leaderboard.
        """

        board = self.df.copy()

        if "Institutional Score" in board.columns:

            board["Institutional Rating"] = (
                board["Institutional Score"]
            )

        else:

            score = pd.Series(
                0,
                index=board.index,
                dtype=float,
            )


            weights = {
                COMPOSITE_SCORE: 0.40,
                "Reliability Score": 0.20,
                "Risk Score": 0.20,
                "Efficiency Score": 0.10,
                "Opportunity Score": 0.10,
            }


            for column, weight in weights.items():

                if column in board.columns:

                    score += (
                        board[column]
                        *
                        weight
                    )


            board["Institutional Rating"] = score

        board = (
            board
            .sort_values(
                "Institutional Rating",
                ascending=False,
            )
            .head(
                top_n,
            )
            .reset_index(
                drop=True,
            )
        )


        ranks = np.arange(
            1,
            len(board) + 1,
        )


        if INSTITUTION_RANK in board.columns:
            board[INSTITUTION_RANK] = ranks

            cols = board.columns.tolist()

            cols.remove(
                INSTITUTION_RANK,
            )

            board = board[[INSTITUTION_RANK] + cols]

        else:
            board.insert(
                0,
                INSTITUTION_RANK,
                ranks,
            )

        recommendation_columns = [
            "Institutional Rating",
            "Edge Score",
            "Reliability Score",
            "Efficiency Score",
            "Risk Score",
            "Opportunity Score",
            "Consistency Score",
            "Validation Score",
        ]


        available_columns = [
            column
            for column in recommendation_columns
            if column in board.columns
        ]

        if not available_columns:

            board[RECOMMENDATION] = "Watch"

            self.overall = board

            return self
        
        recommendation_df = assign_recommendations(
            board[
                available_columns
            ]
            .rename(
                columns={
                    "Institutional Rating":
                    COMPOSITE_SCORE,
                }
            )
            .copy()
        )

        board[RECOMMENDATION] = recommendation_df[RECOMMENDATION]

        self.overall = board

        logger.info("Multi-factor leaderboard generated.")

        return self

    # ---------------------------------------------------------
    # Executive Summary
    # ---------------------------------------------------------
    def summary_report(self):
        """
        Generate executive summary.
        """

        institutional_series = None

        if "Institutional Score" in self.df.columns:

            institutional_series = (
                self.df["Institutional Score"]
            )

        elif "Institutional Rating" in self.df.columns:

            institutional_series = (
                self.df["Institutional Rating"]
            )


        self.summary = pd.DataFrame(
            {
                "Metric": [
                    "Total Records",
                    "Unique Stocks",
                    "Strategies",
                    "Average Composite",
                    "Maximum Composite",
                    "Minimum Composite",
                    "Average Institutional Score",
                    "Highest Institutional Score",
                ],

                "Value": [
                    len(
                        self.df,
                    ),

                    self.df["Stock"].nunique(),

                    self.df["Strategy"].nunique(),

                    round(
                        self.df[COMPOSITE_SCORE].mean(),
                        2,
                    ),

                    round(
                        self.df[COMPOSITE_SCORE].max(),
                        2,
                    ),

                    round(
                        self.df[COMPOSITE_SCORE].min(),
                        2,
                    ),

                    round(
                        institutional_series.mean(),
                        2,
                    )
                    if institutional_series is not None
                    else None,

                    round(
                        institutional_series.max(),
                        2,
                    )
                    if institutional_series is not None
                    else None,
                ],
            }
        )

        logger.info(
            "Executive summary generated."
        )

        return self

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    def diagnostics(self):
        """
        Generate execution diagnostics.
        """

        self.diagnostic_report = {
            "Records": len(
                self.df,
            ),
            "Stocks": self.df["Stock"].nunique(),
            "Strategies": self.df["Strategy"].nunique(),
            "Average Composite": round(
                self.df[COMPOSITE_SCORE].mean(),
                2,
            ),
            "Highest Composite": round(
                self.df[COMPOSITE_SCORE].max(),
                2,
            ),
            "Lowest Composite": round(
                self.df[COMPOSITE_SCORE].min(),
                2,
            ),
            "Leaderboard Entries": len(
                self.overall,
            ),
        }

        logger.info("Diagnostics generated.")

        return self

    # ---------------------------------------------------------
    # Execution Report
    # ---------------------------------------------------------

    def execution_report(self):
        """
        Log execution summary.
        """

        banner(
            logger,
            "Institutional Leaderboard Completed",
        )

        for key, value in self.diagnostic_report.items():
            logger.info(
                "%-30s : %s",
                key,
                value,
            )

        logger.info("")

        logger.info("Leaderboard Engine completed successfully.")

        return self

    # ---------------------------------------------------------
    # Export Results
    # ---------------------------------------------------------

    def export(
        self,
        output_file: str = "Institutional_Leaderboard.xlsx",
    ):
        """
        Export all leaderboard reports.
        """

        from strategy_compare_v4.utils.io_utils import (
            write_excel,
        )

        sheets = {
            "Overall": self.overall,
            "Stocks": self.stock_board,
            "Strategies": self.strategy_board,
            "Expectancy": self.expectancy_board,
            "Profit Factor": self.profit_board,
            "Edge": self.edge_board,
            "Reliability": self.reliability_board,
            "Efficiency": self.efficiency_board,
            "Opportunity": self.opportunity_board,
            "Risk": self.risk_board,
            "Summary": self.summary,
        }

        write_excel(
            sheets,
            output_file,
        )

        logger.info(
            "Leaderboards exported -> %s",
            output_file,
        )

        return self

    # ---------------------------------------------------------
    # Execute Pipeline
    # ---------------------------------------------------------

    def run(self):
        """
        Execute the complete
        leaderboard pipeline.
        """

        start = time.perf_counter()

        try:
            (
                self.validate()
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

        except Exception as exc:
            logger.exception("Leaderboard Engine failed.")

            raise RuntimeError(f"Leaderboard Engine failed:\n{exc}") from exc

        finally:
            self.execution_time = round(
                time.perf_counter() - start,
                3,
            )

        self.diagnostic_report["Execution Time (s)"] = self.execution_time

        self.execution_report()

        return self

    # ---------------------------------------------------------
    # Get Results
    # ---------------------------------------------------------

    def get_results(self):
        """
        Return every generated leaderboard.
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
            "risk": self.risk_board,
            "summary": self.summary,
        }


# ============================================================
# Convenience Function
# ============================================================


def build_leaderboards(
    comparison_df: pd.DataFrame,
    output_file: str = "Institutional_Leaderboard.xlsx",
) -> LeaderboardEngine:
    """
    Execute the institutional
    leaderboard engine.
    """

    engine = LeaderboardEngine(
        comparison_df,
    ).run()

    engine.export(
        output_file,
    )

    return engine


# ============================================================
# Main
# ============================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=("Institutional Leaderboard Engine V4")
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Comparison workbook",
    )

    parser.add_argument(
        "--output",
        default="Institutional_Leaderboard.xlsx",
        help="Output Excel workbook",
    )

    args = parser.parse_args()

    from strategy_compare_v4.utils.io_utils import (
        read_excel,
    )

    comparison_df = read_excel(
        args.input,
    )

    build_leaderboards(
        comparison_df=comparison_df,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
