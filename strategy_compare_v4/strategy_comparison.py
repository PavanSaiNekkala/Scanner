"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    strategy_comparison.py

Purpose:
    Master Orchestrator

Pipeline

Raw Reports
        │
        ▼
Derived Metrics
        │
        ▼
Strategy Comparison
        │
        ▼
Stock Comparison
        │
        ▼
Leaderboard
        │
        ▼
Robustness
        │
        ▼
Correlation
        │
        ▼
Portfolio Builder
        │
        ▼
Excel Report

=============================================================
"""

from pathlib import Path
import traceback

import pandas as pd

from derived_metrics.derived_engine import derive_metrics

from comparison.strategy_compare import compare_strategies
from comparison.stock_compare import compare_stocks
from comparison.leaderboard import build_leaderboards
from comparison.robustness import analyze_robustness
from comparison.correlation import analyze_correlations

from portfolio.portfolio_builder import build_portfolio

from reports.excel_exporter import export_excel


###############################################################################
# Configuration
###############################################################################

INPUT_DIRECTORY = "."

OUTPUT_DIRECTORY = "Institutional_Output"

CAPITAL = 1_000_000

TOP_STOCKS = 25

MAX_WEIGHT = 10


###############################################################################
# Main Engine
###############################################################################

class StrategyComparisonPlatform:
    """
    Master Pipeline
    """

    def __init__(
        self,
        input_directory=INPUT_DIRECTORY,
        output_directory=OUTPUT_DIRECTORY
    ):

        self.input_directory = Path(input_directory)

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            exist_ok=True
        )

        self.strategy_engine = None

        self.stock_engine = None

        self.leaderboard_engine = None

        self.robustness_engine = None

        self.correlation_engine = None

        self.portfolio_engine = None

        self.comparison_df = None

###############################################################################
# Stage 0
###############################################################################

def run_derived_metrics(self):

    print()

    print("=" * 70)

    print("Generating Derived Metrics")

    print("=" * 70)

    derive_metrics(

        input_directory=self.input_directory

    )

    return self

###############################################################################
# Stage 1
###############################################################################

    def run_strategy_comparison(self):

        print()

        print("=" * 70)

        print("Running Strategy Comparison")

        print("=" * 70)

        self.strategy_engine = compare_strategies(

            self.input_directory,

            self.output_directory /
            "Strategy_Comparison.xlsx"

        )

        self.comparison_df = (

            self.strategy_engine
            .comparison_df

        )

        return self


###############################################################################
# Stage 2
###############################################################################

    def run_stock_comparison(self):

        print()

        print("=" * 70)

        print("Running Stock Comparison")

        print("=" * 70)

        self.stock_engine = compare_stocks(

            self.comparison_df,

            self.output_directory /
            "Stock_Comparison.xlsx"

        )

        return self


###############################################################################
# Stage 3
###############################################################################

    def run_leaderboards(self):

        print()

        print("=" * 70)

        print("Building Leaderboards")

        print("=" * 70)

        self.leaderboard_engine = build_leaderboards(

            self.comparison_df,

            self.output_directory /
            "Leaderboards.xlsx"

        )

        return self


###############################################################################
# Stage 4
###############################################################################

    def run_robustness(self):

        print()

        print("=" * 70)

        print("Running Robustness Analysis")

        print("=" * 70)

        self.robustness_engine = analyze_robustness(

            self.comparison_df,

            self.output_directory /
            "Robustness.xlsx"

        )

        return self


###############################################################################
# Stage 5
###############################################################################

    def run_correlation(self):

        print()

        print("=" * 70)

        print("Running Correlation Analysis")

        print("=" * 70)

        self.correlation_engine = analyze_correlations(

            self.comparison_df,

            self.output_directory /
            "Correlation.xlsx"

        )

        return self
    
###############################################################################
# Stage 6
###############################################################################

    def run_portfolio(self):

        print()

        print("=" * 70)

        print("Building Institutional Portfolio")

        print("=" * 70)

        self.portfolio_engine = build_portfolio(

            self.comparison_df,

            capital=CAPITAL,

            top_n=TOP_STOCKS,

            max_weight=MAX_WEIGHT,

            output_file=self.output_directory /
            "Institutional_Portfolio.xlsx"

        )

        return self


###############################################################################
# Stage 7
###############################################################################

    def export_final_report(self):

        """
        Export consolidated Excel workbook.
        """

        print()

        print("=" * 70)

        print("Exporting Institutional Report")

        print("=" * 70)

        sheets = {

            "Strategy Comparison":

                self.strategy_engine.comparison_df,

            "Best Strategy":

                self.strategy_engine.best_df,

            "Strategy Summary":

                self.strategy_engine.summary_df,

            "Stock Comparison":

                self.stock_engine.stock_summary,

            "Stock Rankings":

                self.stock_engine.rankings,

            "Overall Leaderboard":

                self.leaderboard_engine.overall,

            "Strategy Leaderboard":

                self.leaderboard_engine.strategy,

            "Stock Leaderboard":

                self.leaderboard_engine.stock,

            "Edge Leaderboard":

                self.leaderboard_engine.edge,

            "Robustness":

                self.robustness_engine.robustness,

            "Stability":

                self.robustness_engine.stability,

            "Correlation":

                self.correlation_engine.pearson,

            "Diversification":

                self.correlation_engine.diversification,

            "Portfolio":

                self.portfolio_engine.portfolio,

            "Portfolio Summary":

                self.portfolio_engine.summary

        }

        export_excel(

            self.output_directory /
            "Institutional_Strategy_Report.xlsx",

            sheets

        )

        return self


###############################################################################
# Diagnostics
###############################################################################

    def diagnostics(self):

        print()

        print("=" * 70)

        print("PIPELINE SUMMARY")

        print("=" * 70)

        print(

            f"Strategies : "

            f"{self.comparison_df['Strategy'].nunique()}"

        )

        print(

            f"Stocks     : "

            f"{self.comparison_df['Stock'].nunique()}"

        )

        print(

            f"Rows       : "

            f"{len(self.comparison_df)}"

        )

        print(

            f"Portfolio  : "

            f"{len(self.portfolio_engine.portfolio)} Positions"

        )

        print("=" * 70)

        print()

        return self
    
###############################################################################
# Pipeline
###############################################################################

    def run(self):

        """
        Execute complete institutional workflow.
        """

        try:

            (

                self

                .run_strategy_comparison()

                .run_stock_comparison()

                .run_leaderboards()

                .run_robustness()

                .run_correlation()

                .run_portfolio()

                .export_final_report()

                .diagnostics()

            )

            print()

            print("=" * 70)

            print("PIPELINE COMPLETED SUCCESSFULLY")

            print("=" * 70)

            print()

        except Exception as e:

            print()

            print("=" * 70)

            print("PIPELINE FAILED")

            print("=" * 70)

            print(f"Error : {e}")

            traceback.print_exc()

            print()

            raise

        return self


###############################################################################
# Results
###############################################################################

    def get_results(self):

        """
        Return all generated engines and outputs.
        """

        return {

            "comparison": self.comparison_df,

            "strategy_engine": self.strategy_engine,

            "stock_engine": self.stock_engine,

            "leaderboard_engine": self.leaderboard_engine,

            "robustness_engine": self.robustness_engine,

            "correlation_engine": self.correlation_engine,

            "portfolio_engine": self.portfolio_engine

        }
    
###############################################################################
# Convenience Function
###############################################################################

def run_strategy_comparison_pipeline(

    input_directory=INPUT_DIRECTORY,

    output_directory=OUTPUT_DIRECTORY

):

    """
    Execute the complete Strategy Comparison pipeline.

    Parameters
    ----------
    input_directory : str | Path
        Directory containing strategy folders.

    output_directory : str | Path
        Directory where reports will be generated.

    Returns
    -------
    StrategyComparisonPlatform
    """

    engine = StrategyComparisonPlatform(

        input_directory=input_directory,

        output_directory=output_directory

    )

    engine.run()

    return engine


###############################################################################
# Main
###############################################################################

def main():

    """
    Entry point.
    """

    print()

    print("=" * 70)

    print("INSTITUTIONAL STRATEGY COMPARISON PLATFORM V4")

    print("=" * 70)

    print()

    run_strategy_comparison_pipeline()

    print()

    print("=" * 70)

    print("REPORTS GENERATED SUCCESSFULLY")

    print("=" * 70)

    print()


###############################################################################
# CLI Entry
###############################################################################

if __name__ == "__main__":

    main()