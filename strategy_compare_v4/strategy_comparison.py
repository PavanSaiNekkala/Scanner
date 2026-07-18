"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
strategy_comparison.py

Purpose
-------
Master Orchestrator for the complete
Institutional Strategy Comparison Platform.

Pipeline
--------
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
Leaderboards
      │
      ▼
Robustness Analysis
      │
      ▼
Correlation Analysis
      │
      ▼
Portfolio Builder
      │
      ▼
Institutional Excel Report

=============================================================
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd

from strategy_compare_v4.config.constants import (
    CAPITAL,
    INPUT_DIRECTORY,
    MAX_POSITION_WEIGHT,
    OUTPUT_DIRECTORY,
    TOP_STOCKS,
)

from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)

from strategy_compare_v4.utils.helpers import (
    require_columns,
)

from strategy_compare_v4.derived_metrics.derived_engine import (
    derive_metrics,
)

from strategy_compare_v4.comparison.strategy_compare import (
    compare_strategies,
)

from strategy_compare_v4.comparison.stock_compare import (
    compare_stocks,
)

from strategy_compare_v4.comparison.leaderboard import (
    build_leaderboards,
)

from strategy_compare_v4.comparison.robustness import (
    analyze_robustness,
)

from strategy_compare_v4.comparison.correlation import (
    analyze_correlations,
)

from strategy_compare_v4.portfolio.portfolio_builder import (
    build_portfolio,
)

from strategy_compare_v4.reports.excel_exporter import (
    export_excel,
)

logger = get_logger(__name__)


# ============================================================
# Master Orchestrator
# ============================================================

class StrategyComparisonPlatform:
    """
    Master orchestration engine
    for the Institutional
    Strategy Comparison Platform.
    """

    def __init__(
        self,
        input_directory: str | Path = INPUT_DIRECTORY,
        output_directory: str | Path = OUTPUT_DIRECTORY,
    ):
        """
        Initialize platform.
        """

        banner(

            logger,

            "Strategy Comparison Platform",

        )

        self.input_directory = Path(

            input_directory,

        )

        self.output_directory = Path(

            output_directory,

        )

        self.output_directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        # --------------------------------------------------
        # Pipeline Engines
        # --------------------------------------------------

        self.strategy_engine = None

        self.stock_engine = None

        self.leaderboard_engine = None

        self.robustness_engine = None

        self.correlation_engine = None

        self.portfolio_engine = None

        # --------------------------------------------------
        # Outputs
        # --------------------------------------------------

        self.comparison_df: pd.DataFrame | None = None

        self.execution_time: float = 0.0

        self.diagnostic_report: dict[str, Any] = {}

        logger.info(

            "Input Directory  : %s",

            self.input_directory,

        )

        logger.info(

            "Output Directory : %s",

            self.output_directory,

        )

    # ============================================================
    # Stage 0
    # ============================================================

    def run_derived_metrics(
        self,
    ):
        """
        Generate all derived
        institutional metrics.
        """

        banner(

            logger,

            "Stage 0 : Derived Metrics",

        )

        derive_metrics(

            input_directory=self.input_directory,

        )

        logger.info(

            "Derived metrics generated successfully."

        )

        return self


    # ============================================================
    # Stage 1
    # ============================================================

    def run_strategy_comparison(
        self,
    ):
        """
        Execute strategy
        comparison engine.
        """

        banner(

            logger,

            "Stage 1 : Strategy Comparison",

        )

        self.strategy_engine = compare_strategies(

            self.input_directory,

            self.output_directory
            / "Strategy_Comparison.xlsx",

        )

        self.comparison_df = (

            self.strategy_engine
            .comparison_df

        )

        require_columns(

            self.comparison_df,

            [

                "Strategy",

                "Stock",

            ],

        )

        logger.info(

            "Strategies : %d",

            self.comparison_df[
                "Strategy"
            ].nunique(),

        )

        logger.info(

            "Stocks : %d",

            self.comparison_df[
                "Stock"
            ].nunique(),

        )

        logger.info(

            "Rows : %d",

            len(

                self.comparison_df,

            ),

        )

        return self


    # ============================================================
    # Stage 2
    # ============================================================

    def run_stock_comparison(
        self,
    ):
        """
        Execute stock
        comparison engine.
        """

        banner(

            logger,

            "Stage 2 : Stock Comparison",

        )

        require_columns(

            self.comparison_df,

            [

                "Stock",

            ],

        )

        self.stock_engine = compare_stocks(

            self.comparison_df,

            self.output_directory
            / "Stock_Comparison.xlsx",

        )

        logger.info(

            "Stock comparison completed."

        )

        return self


    # ============================================================
    # Stage 3
    # ============================================================

    def run_leaderboards(
        self,
    ):
        """
        Build institutional
        leaderboards.
        """

        banner(

            logger,

            "Stage 3 : Leaderboards",

        )

        self.leaderboard_engine = (

            build_leaderboards(

                self.comparison_df,

                self.output_directory
                / "Leaderboards.xlsx",

            )

        )

        logger.info(

            "Leaderboards generated successfully."

        )

        return self
    
    # ============================================================
    # Stage 4
    # ============================================================

    def run_robustness(
        self,
    ):
        """
        Execute robustness
        analysis.
        """

        banner(

            logger,

            "Stage 4 : Robustness Analysis",

        )

        self.robustness_engine = (

            analyze_robustness(

                self.comparison_df,

                self.output_directory
                / "Robustness.xlsx",

            )

        )

        logger.info(

            "Robustness analysis completed."

        )

        return self


    # ============================================================
    # Stage 5
    # ============================================================

    def run_correlation(
        self,
    ):
        """
        Execute correlation
        analysis.
        """

        banner(

            logger,

            "Stage 5 : Correlation Analysis",

        )

        self.correlation_engine = (

            analyze_correlations(

                self.comparison_df,

                self.output_directory
                / "Correlation.xlsx",

            )

        )

        logger.info(

            "Correlation analysis completed."

        )

        return self


    # ============================================================
    # Stage 6
    # ============================================================

    def run_portfolio(
        self,
    ):
        """
        Build the institutional
        portfolio.
        """

        banner(

            logger,

            "Stage 6 : Portfolio Builder",

        )

        self.portfolio_engine = (

            build_portfolio(

                self.comparison_df,

                capital=CAPITAL,

                top_n=TOP_STOCKS,

                max_weight=MAX_POSITION_WEIGHT,

                output_file=(

                    self.output_directory

                    / "Institutional_Portfolio.xlsx"

                ),

            )

        )

        logger.info(

            "Portfolio built successfully."

        )

        logger.info(

            "Portfolio Positions : %d",

            len(

                self.portfolio_engine.portfolio,

            ),

        )

        return self


    # ============================================================
    # Stage 7
    # ============================================================

    def export_final_report(
        self,
    ):
        """
        Export consolidated
        institutional report.
        """

        banner(

            logger,

            "Stage 7 : Export Report",

        )

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

                self.portfolio_engine.summary,

        }

        export_excel(

            self.output_directory

            / "Institutional_Strategy_Report.xlsx",

            sheets,

        )

        logger.info(

            "Final institutional report exported."

        )

        logger.info(

            "Worksheets Exported : %d",

            len(

                sheets,

            ),

        )

        return self

    # ============================================================
    # Diagnostics
    # ============================================================

    def diagnostics(
        self,
    ):
        """
        Generate pipeline
        diagnostics.
        """

        banner(

            logger,

            "Pipeline Summary",

        )

        require_columns(

            self.comparison_df,

            [

                "Strategy",

                "Stock",

            ],

        )

        self.diagnostic_report = {

            "strategies":

                self.comparison_df[
                    "Strategy"
                ].nunique(),

            "stocks":

                self.comparison_df[
                    "Stock"
                ].nunique(),

            "rows":

                len(

                    self.comparison_df,

                ),

            "portfolio_positions":

                len(

                    self.portfolio_engine
                    .portfolio,

                ),

            "execution_time":

                round(

                    self.execution_time,

                    3,

                ),

        }

        for key, value in (

            self.diagnostic_report

            .items()

        ):

            logger.info(

                "%-22s : %s",

                key.replace(

                    "_",

                    " ",

                ).title(),

                value,

            )

        return self


    # ============================================================
    # Execute Pipeline
    # ============================================================

    def run(
        self,
    ):
        """
        Execute the complete
        institutional workflow.
        """

        start = time.perf_counter()

        try:

            (

                self

                .run_derived_metrics()

                .run_strategy_comparison()

                .run_stock_comparison()

                .run_leaderboards()

                .run_robustness()

                .run_correlation()

                .run_portfolio()

                .export_final_report()

            )

        except Exception:

            logger.exception(

                "Strategy Comparison Platform failed."

            )

            raise

        finally:

            self.execution_time = (

                time.perf_counter()

                - start

            )

            self.diagnostics()

            banner(

                logger,

                "Pipeline Completed",

            )

            logger.info(

                "Execution Time : %.3f seconds",

                self.execution_time,

            )

        return self


    # ============================================================
    # Results
    # ============================================================

    def get_results(
        self,
    ) -> dict[str, Any]:
        """
        Return all generated
        engines and outputs.
        """

        return {

            "comparison":

                self.comparison_df,

            "strategy_engine":

                self.strategy_engine,

            "stock_engine":

                self.stock_engine,

            "leaderboard_engine":

                self.leaderboard_engine,

            "robustness_engine":

                self.robustness_engine,

            "correlation_engine":

                self.correlation_engine,

            "portfolio_engine":

                self.portfolio_engine,

            "diagnostics":

                self.diagnostic_report,

            "execution_time":

                self.execution_time,

        }
    
# ============================================================
# Convenience Function
# ============================================================

def run_strategy_comparison_pipeline(
    input_directory: str | Path = INPUT_DIRECTORY,
    output_directory: str | Path = OUTPUT_DIRECTORY,
) -> StrategyComparisonPlatform:
    """
    Execute the complete
    Institutional Strategy
    Comparison pipeline.

    Parameters
    ----------
    input_directory : str | Path
        Directory containing
        strategy reports.

    output_directory : str | Path
        Destination directory
        for generated reports.

    Returns
    -------
    StrategyComparisonPlatform
        Fully executed
        pipeline instance.
    """

    banner(

        logger,

        "Launching Strategy Comparison Pipeline",

    )

    engine = StrategyComparisonPlatform(

        input_directory=input_directory,

        output_directory=output_directory,

    )

    engine.run()

    logger.info(

        "Pipeline finished successfully."

    )

    return engine


# ============================================================
# Main
# ============================================================

def main():
    """
    Application entry point.
    """

    banner(

        logger,

        "Institutional Strategy Comparison Platform V4",

    )

    engine = run_strategy_comparison_pipeline()

    logger.info(

        "Reports generated successfully."

    )

    logger.info(

        "Output Directory : %s",

        engine.output_directory,

    )

    logger.info(

        "Execution Time : %.3f seconds",

        engine.execution_time,

    )


# ============================================================
# CLI Entry
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        logger.warning(

            "Pipeline interrupted by user."

        )

    except Exception:

        logger.exception(

            "Unexpected fatal error."

        )

        raise