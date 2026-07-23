"""
=============================================================
Institutional Stock Comparison Engine V4

Module
------
comparison/stock_compare.py

Purpose
-------
Compare all strategies for every stock and identify
the best performing strategy using institutional
ranking metrics.

=============================================================
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from strategy_compare_v4.utils.math_utils import safe_divide

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
# Stock Comparison Engine
# ============================================================


class StockComparisonEngine:
    """
    Institutional Stock Comparison Engine.

    Responsibilities
    ----------------
    • Compare every strategy for every stock
    • Rank strategies within each stock
    • Compute institutional stock scores
    • Generate recommendations
    • Export institutional reports
    """

    def __init__(
        self,
        comparison_df: pd.DataFrame,
    ):
        self.df = comparison_df.copy()

        self.stock_summary = pd.DataFrame()

        self.stock_rankings = pd.DataFrame()

        self.consistency = pd.DataFrame()

        self.best_strategies = pd.DataFrame()

        self.recommendations = pd.DataFrame()

        self.statistics = pd.DataFrame()

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
            "Validating Stock Comparison Input",
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

        return self

    # ---------------------------------------------------------
    # Rank Strategies Within Stock
    # ---------------------------------------------------------

    def rank_within_stock(self):
        """
        Rank competing strategies
        inside each stock.
        """

        self.df["Strategy Rank"] = self.df.groupby("Stock")[COMPOSITE_SCORE].rank(
            ascending=False,
            method="dense",
        )

        logger.info("Strategy ranking completed.")

        return self

    # ---------------------------------------------------------
    # Best Strategy
    # ---------------------------------------------------------

    def best_strategy(self):
        """
        Determine the highest scoring
        strategy for each stock.
        """

        filtered = self.df.copy()


        if "Trades" in filtered.columns:

            filtered = filtered.loc[
                filtered["Trades"] >= 30
            ]


        idx = (
            filtered
            .groupby("Stock")[COMPOSITE_SCORE]
            .idxmax()
        )


        self.best_strategies = (
            filtered.loc[idx]
            .sort_values(
                COMPOSITE_SCORE,
                ascending=False,
            )
            .reset_index(
                drop=True,
            )
        )


        logger.info(
            "Best strategy identified for %d stocks.",
            len(self.best_strategies),
        )

        return self

    # ---------------------------------------------------------
    # Stock Summary
    # ---------------------------------------------------------

    def summarize_stock(self):
        """
        Generate institutional summary
        statistics for every stock.
        """

        def weighted_average(group, column):

            return np.average(
                group[column],
                weights=group["Trades"],
            )


        self.stock_summary = (
            self.df
            .groupby(
                "Stock",
                as_index=False,
            )
            .apply(
                lambda x: pd.Series(
                    {
                        "Strategies":
                            x["Strategy"].count(),

                        "AverageComposite":
                            weighted_average(
                                x,
                                COMPOSITE_SCORE,
                            ),

                        "AverageExpectancy":
                            weighted_average(
                                x,
                                "Expectancy",
                            ),

                        "AverageProfitFactor":
                            weighted_average(
                                x,
                                "Profit Factor",
                            ),

                        "AverageRewardRisk":
                            weighted_average(
                                x,
                                "Reward Risk",
                            ),

                        "Edge Score":
                            weighted_average(
                                x,
                                "Edge Score",
                            ),

                        "Reliability Score":
                            weighted_average(
                                x,
                                "Reliability Score",
                            ),

                        "Efficiency Score":
                            weighted_average(
                                x,
                                "Efficiency Score",
                            ),

                        "Risk Score":
                            weighted_average(
                                x,
                                "Risk Score",
                            ),

                        "Return Score":
                            weighted_average(
                                x,
                                "Return Score",
                            ),

                        "Opportunity Score":
                            weighted_average(
                                x,
                                "Opportunity Score",
                            ),
                    }
                )
            )
            .reset_index()
        )


        self.stock_summary = round_dataframe(
            self.stock_summary,
            decimals=2,
        )


        logger.info(
            "Generated stock summary for %d stocks.",
            len(self.stock_summary),
        )

        return self

    # ---------------------------------------------------------
    # Stock Statistics
    # ---------------------------------------------------------

    def stock_statistics(self):
        """
        Calculate dispersion statistics
        for each stock.
        """

        self.statistics = self.df.groupby(
            "Stock",
            as_index=False,
        ).agg(
            StdComposite=(
                COMPOSITE_SCORE,
                "std",
            ),
            Variance=(
                COMPOSITE_SCORE,
                "var",
            ),
            Median=(
                COMPOSITE_SCORE,
                "median",
            ),
            Mean=(
                COMPOSITE_SCORE,
                "mean",
            ),
        )

        self.statistics = round_dataframe(
            self.statistics,
            decimals=2,
        )

        logger.info("Calculated stock statistics.")

        return self

    # ---------------------------------------------------------
    # Consistency Score
    # ---------------------------------------------------------

    def consistency_score(self):
        """
        Measure strategy consistency.

        Higher is better.
        """

        self.consistency = self.statistics.copy()


        self.consistency["Consistency Score"] = (
            1
            -
            safe_divide(
                self.consistency["StdComposite"],
                self.consistency["Mean"],
            )
        ).clip(
            0,
            1,
        ) * 100


        self.consistency = round_dataframe(
            self.consistency,
            decimals=2,
        )


        logger.info(
            "Consistency scores computed."
        )


        return self

    # ---------------------------------------------------------
    # Merge Results
    # ---------------------------------------------------------

    def merge_results(self):
        """
        Merge stock summary with
        institutional consistency scores.
        """

        self.stock_rankings = self.stock_summary.merge(
            self.consistency[
                [
                    "Stock",
                    "Consistency Score",
                ]
            ],
            on="Stock",
            how="left",
        )

        logger.info("Merged institutional results.")

        return self

    # ---------------------------------------------------------
    # Agreement Score
    # ---------------------------------------------------------

    def agreement_score(self):
        """
        Measure agreement between
        strategies for every stock.
        """

        agreement = self.df.groupby(
            "Stock",
            as_index=False,
        ).agg(
            CompositeStd=(
                COMPOSITE_SCORE,
                "std",
            ),
            CompositeMean=(
                COMPOSITE_SCORE,
                "mean",
            ),
        )

        agreement["Agreement Score"] = (
            (
                1
                -
                safe_divide(
                    agreement["CompositeStd"],
                    agreement["CompositeMean"],
                )
            )
            .clip(
                0,
                1,
            )
            *
            100
        )

        agreement = round_dataframe(
            agreement,
            decimals=2,
        )

        self.stock_rankings = self.stock_rankings.merge(
            agreement[
                [
                    "Stock",
                    "Agreement Score",
                ]
            ],
            on="Stock",
            how="left",
        )

        logger.info("Agreement scores calculated.")

        return self

    # ---------------------------------------------------------
    # Institutional Score
    # ---------------------------------------------------------

    def institutional_score(self):
        """
        Calculate final institutional
        stock score.
        """

        self.stock_rankings["Institutional Score"] = (

            self.stock_rankings["AverageComposite"]
            * 0.40

            +

            self.stock_rankings["Reliability Score"]
            * 0.20

            +

            self.stock_rankings["Risk Score"]
            * 0.20

            +

            self.stock_rankings["Consistency Score"]
            * 0.10

            +

            self.stock_rankings["Agreement Score"]
            * 0.10
        )


        self.stock_rankings = round_dataframe(
            self.stock_rankings,
            decimals=2,
        )


        logger.info(
            "Institutional scores calculated."
        )


        return self

    # ---------------------------------------------------------
    # Rank Stocks
    # ---------------------------------------------------------

    def rank_stocks(self):
        """
        Rank all stocks using
        institutional score.
        """

        self.stock_rankings = self.stock_rankings.sort_values(
            "Institutional Score",
            ascending=False,
        ).reset_index(
            drop=True,
        )

        self.stock_rankings[INSTITUTION_RANK] = np.arange(
            1,
            len(self.stock_rankings) + 1,
        )

        logger.info("Assigned institutional ranks.")

        return self

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    def recommendation(self):
        """
        Generate institutional
        recommendations.
        """

        recommendation_input = (
            self.stock_rankings[
                [
                    "Institutional Score",
                    "Edge Score",
                    "Reliability Score",
                    "Efficiency Score",
                    "Risk Score",
                    "Return Score",
                    "Opportunity Score",
                    "Consistency Score",
                    "Agreement Score",
                ]
            ]
            .rename(
                columns={
                    "Institutional Score": COMPOSITE_SCORE,
                }
            )
            .copy()
        )

        recommendation_df = assign_recommendations(
            recommendation_input,
        )

        self.stock_rankings[RECOMMENDATION] = recommendation_df[RECOMMENDATION]

        logger.info("Institutional recommendations generated.")

        return self

    # ---------------------------------------------------------
    # Top Opportunities
    # ---------------------------------------------------------

    def top_opportunities(
        self,
        top_n: int = 25,
    ):
        """
        Select the highest ranked
        institutional opportunities.
        """

        self.best_strategies = (
            self.stock_rankings.head(top_n)
            .copy()
            .reset_index(
                drop=True,
            )
        )

        logger.info(
            "Selected top %d institutional opportunities.",
            top_n,
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
            "Stocks": len(self.stock_rankings),
            "Strategies": self.df["Strategy"].nunique(),
            "Average Institutional Score": round(
                self.stock_rankings["Institutional Score"].mean(),
                2,
            ),
            "Highest Institutional Score": round(
                self.stock_rankings["Institutional Score"].max(),
                2,
            ),
            "Lowest Institutional Score": round(
                self.stock_rankings["Institutional Score"].min(),
                2,
            ),
            "Strong Buy": (self.stock_rankings[RECOMMENDATION] == "Strong Buy").sum(),
            "Buy": (self.stock_rankings[RECOMMENDATION] == "Buy").sum(),
            "Watch": (self.stock_rankings[RECOMMENDATION] == "Watch").sum(),
            "Improve": (self.stock_rankings[RECOMMENDATION] == "Improve").sum(),
            "Avoid": (self.stock_rankings[RECOMMENDATION] == "Avoid").sum(),
            "Reject": (self.stock_rankings[RECOMMENDATION] == "Reject").sum(),
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
            "Institutional Stock Comparison Completed",
        )

        for key, value in self.diagnostic_report.items():
            logger.info(
                "%-35s : %s",
                key,
                value,
            )

        logger.info("")

        logger.info("Stock Comparison Engine completed successfully.")

        return self

    # ---------------------------------------------------------
    # Export Results
    # ---------------------------------------------------------

    def export(
        self,
        output_file: str = "Stock_Comparison.xlsx",
    ):
        """
        Export all reports.
        """

        from strategy_compare_v4.utils.io_utils import (
            write_excel,
        )

        sheets = {
            "All Strategies": self.df,
            "Stock Rankings": self.stock_rankings,
            "Top Opportunities": self.best_strategies,
            "Statistics": self.statistics,
            "Stock Summary": self.stock_summary,
            "Consistency": self.consistency,
        }

        write_excel(
            sheets,
            output_file,
        )

        logger.info(
            "Results exported -> %s",
            output_file,
        )

        return self

    # ---------------------------------------------------------
    # Get Results
    # ---------------------------------------------------------

    def get_results(self):
        """
        Return generated dataframes.
        """

        return {
            "all_strategies": self.df,
            "stock_rankings": self.stock_rankings,
            "top_opportunities": self.best_strategies,
            "statistics": self.statistics,
            "stock_summary": self.stock_summary,
            "consistency": self.consistency,
        }

    # ---------------------------------------------------------
    # Execute Pipeline
    # ---------------------------------------------------------

    def run(self):
        """
        Execute the complete
        stock comparison pipeline.
        """

        start = time.perf_counter()

        try:
            (
                self.validate()
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

        except Exception as exc:
            logger.exception("Stock Comparison Engine failed.")

            raise RuntimeError(f"Stock Comparison Engine failed:\n{exc}") from exc

        finally:
            self.execution_time = round(
                time.perf_counter() - start,
                3,
            )

        self.diagnostic_report["Execution Time (s)"] = self.execution_time

        self.execution_report()

        return self


# ============================================================
# Convenience Function
# ============================================================


def compare_stocks(
    comparison_df: pd.DataFrame,
    output_file: str = "Stock_Comparison.xlsx",
) -> StockComparisonEngine:
    """
    Execute the institutional
    stock comparison engine.
    """

    engine = StockComparisonEngine(
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
        description=("Institutional Stock Comparison Engine V4")
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Comparison DataFrame Excel file",
    )

    parser.add_argument(
        "--output",
        default="Stock_Comparison.xlsx",
        help="Output Excel workbook",
    )

    args = parser.parse_args()

    from strategy_compare_v4.utils.io_utils import (
        read_excel,
    )

    comparison_df = read_excel(
        args.input,
    )

    compare_stocks(
        comparison_df=comparison_df,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
