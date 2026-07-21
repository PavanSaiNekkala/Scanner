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

=============================================================
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

import pandas as pd

from strategy_compare_v4.comparison.correlation import (
    analyze_correlations,
)
from strategy_compare_v4.comparison.leaderboard import (
    build_leaderboards,
)
from strategy_compare_v4.comparison.robustness import (
    analyze_robustness,
)
from strategy_compare_v4.comparison.stock_compare import (
    compare_stocks,
)
from strategy_compare_v4.comparison.strategy_compare import (
    compare_strategies,
)
from strategy_compare_v4.config.constants import (
    CAPITAL,
    INPUT_DIRECTORY,
    MAX_POSITION_WEIGHT,
    OUTPUT_DIRECTORY,
    STRATEGY_FOLDERS,
    TOP_STOCKS,
)
from strategy_compare_v4.derived_metrics.derived_engine import (
    derive_metrics,
)
from strategy_compare_v4.portfolio.portfolio_builder import (
    build_portfolio,
)
from strategy_compare_v4.reports.excel_exporter import (
    export_excel,
)
from strategy_compare_v4.summary.summary_engine import (
    generate_strategy_summary,
)
from strategy_compare_v4.utils.helpers import (
    require_columns,
)
from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)

logger = get_logger(__name__)

# ============================================================
# Pipeline State
# ============================================================


class PipelineState(Enum):
    """
    Execution state of the pipeline.
    """

    NOT_STARTED = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()


# ============================================================
# Configuration
# ============================================================


@dataclass(slots=True)
class PipelineConfig:
    """
    Pipeline configuration.
    """

    input_directory: Path = Path(INPUT_DIRECTORY)
    output_directory: Path = Path(OUTPUT_DIRECTORY)

    capital: float = CAPITAL
    top_n: int = TOP_STOCKS
    max_position_weight: float = MAX_POSITION_WEIGHT

    comparison_file: str = "Strategy_Comparison.xlsx"
    stock_file: str = "Stock_Comparison.xlsx"
    leaderboard_file: str = "Leaderboards.xlsx"
    robustness_file: str = "Robustness.xlsx"
    correlation_file: str = "Correlation.xlsx"
    portfolio_file: str = "Institutional_Portfolio.xlsx"
    final_report_file: str = "Institutional_Strategy_Report.xlsx"


# ============================================================
# Diagnostics
# ============================================================


@dataclass(slots=True)
class PipelineDiagnostics:
    """
    Pipeline statistics.
    """

    strategies: int = 0
    stocks: int = 0
    rows: int = 0
    portfolio_positions: int = 0
    execution_time: float = 0.0

    stage_times: dict[str, float] = field(default_factory=dict)


# ============================================================
# Pipeline Result
# ============================================================


@dataclass(slots=True)
class PipelineResult:
    """
    Final pipeline outputs.
    """

    comparison_df: pd.DataFrame | None

    strategy_engine: Any
    stock_engine: Any
    leaderboard_engine: Any
    robustness_engine: Any
    correlation_engine: Any
    portfolio_engine: Any

    diagnostics: PipelineDiagnostics

    execution_time: float


# ============================================================
# Stage Executor
# ============================================================


class StageExecutor:
    """
    Executes a pipeline stage while
    automatically handling logging,
    timing and exception reporting.
    """

    def __init__(
        self,
        logger,
        diagnostics: PipelineDiagnostics,
    ):
        self.logger = logger
        self.diagnostics = diagnostics

    def execute(
        self,
        stage_name: str,
        func: Callable,
        *args,
        **kwargs,
    ):
        """
        Execute one pipeline stage.
        """

        banner(
            self.logger,
            stage_name,
        )

        start = time.perf_counter()

        try:
            result = func(
                *args,
                **kwargs,
            )

        except Exception:
            self.logger.exception(
                "%s failed.",
                stage_name,
            )

            raise

        elapsed = time.perf_counter() - start

        self.diagnostics.stage_times[stage_name] = round(
            elapsed,
            3,
        )

        self.logger.info(
            "%s completed in %.3f seconds.",
            stage_name,
            elapsed,
        )

        return result


# ============================================================
# Master Orchestrator
# ============================================================


class StrategyComparisonPlatform:
    """
    Institutional Strategy
    Comparison Platform.

    Responsible only for
    orchestration.

    No business logic should
    exist in this class.
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
    ):
        banner(
            logger,
            "Institutional Strategy Comparison Platform",
        )

        self.config = config if config else PipelineConfig()

        self.config.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.state = PipelineState.NOT_STARTED

        self.execution_time = 0.0

        self.diagnostics = PipelineDiagnostics()

        self.executor = StageExecutor(
            logger,
            self.diagnostics,
        )

        # ------------------------------------------------
        # Engine Objects
        # ------------------------------------------------

        self.strategy_engine = None
        self.stock_engine = None
        self.leaderboard_engine = None
        self.robustness_engine = None
        self.correlation_engine = None
        self.portfolio_engine = None

        # ------------------------------------------------
        # Intermediate Data
        # ------------------------------------------------

        self.comparison_df: pd.DataFrame | None = None

        logger.info(
            "Input Directory  : %s",
            self.config.input_directory,
        )

        logger.info(
            "Output Directory : %s",
            self.config.output_directory,
        )

    # ====================================================
    # Internal Helpers
    # ====================================================

    @property
    def output_directory(self) -> Path:
        """
        Output directory.
        """

        return self.config.output_directory

    @property
    def input_directory(self) -> Path:
        """
        Input directory.
        """

        return self.config.input_directory

    def _validate_comparison_dataframe(self) -> pd.DataFrame:
        if self.comparison_df is None:
            raise RuntimeError("Comparison dataframe not loaded.")

        require_columns(
            self.comparison_df,
            [
                "Strategy",
                "Stock",
            ],
        )

        return self.comparison_df

    def _log_dataset_summary(
        self,
    ) -> None:
        """
        Log comparison dataset statistics.
        """

        df = self._validate_comparison_dataframe()

        logger.info(
            "Strategies : %d",
            df["Strategy"].nunique(),
        )

        logger.info(
            "Stocks : %d",
            df["Stock"].nunique(),
        )

        logger.info(
            "Rows : %d",
            len(df),
        )

    # ============================================================
    # Pipeline Stages
    # ============================================================

    def run_derived_metrics(self):
        """
        Stage 0

        Generate institutional summary from trade logs
        and derive institutional metrics.
        """

        banner(
            logger,
            "Stage 0 : Derived Metrics",
        )

        processed = 0

        for strategy in STRATEGY_FOLDERS:
            strategy_dir = self.input_directory / strategy

            if not strategy_dir.exists():
                logger.warning(
                    "Strategy folder not found: %s",
                    strategy_dir,
                )

                continue

            logger.info(
                "Generating summary for %s",
                strategy,
            )

            summary_df = generate_strategy_summary(
                strategy_directory=strategy_dir,
            )

            logger.info("Calculating institutional metrics...")

            institutional_df = derive_metrics(summary_df)

            output_file = strategy_dir / f"{strategy}_Institutional.csv"

            institutional_df.to_csv(
                output_file,
                index=False,
            )

            logger.info(
                "Saved %s",
                output_file.name,
            )

            processed += 1

        logger.info(
            "Completed %d strategies.",
            processed,
        )

        return self

    # ========================================================

    def run_strategy_comparison(self) -> StrategyComparisonPlatform:
        """
        Stage 1
        Strategy comparison.
        """

        self.strategy_engine = self.executor.execute(
            "Stage 1 : Strategy Comparison",
            compare_strategies,
            self.input_directory,
            self.output_directory / self.config.comparison_file,
        )

        assert self.strategy_engine is not None

        self.comparison_df = self.strategy_engine.comparison_df

        self._log_dataset_summary()

        return self

    # ========================================================

    def run_stock_comparison(self):
        """
        Stage 2
        Stock comparison.
        """

        self._validate_comparison_dataframe()

        self.stock_engine = self.executor.execute(
            "Stage 2 : Stock Comparison",
            compare_stocks,
            self.comparison_df,
            self.output_directory / self.config.stock_file,
        )

        return self

    # ========================================================

    def run_leaderboards(self):
        """
        Stage 3
        Leaderboards.
        """

        self._validate_comparison_dataframe()

        self.leaderboard_engine = self.executor.execute(
            "Stage 3 : Leaderboards",
            build_leaderboards,
            self.comparison_df,
            self.output_directory / self.config.leaderboard_file,
        )

        return self

    # ========================================================

    def run_robustness(self):
        """
        Stage 4
        Robustness analysis.
        """

        self._validate_comparison_dataframe()

        self.robustness_engine = self.executor.execute(
            "Stage 4 : Robustness Analysis",
            analyze_robustness,
            self.comparison_df,
            self.output_directory / self.config.robustness_file,
        )

        return self

    # ========================================================

    def run_correlation(self):
        """
        Stage 5
        Correlation analysis.
        """

        self._validate_comparison_dataframe()

        self.correlation_engine = self.executor.execute(
            "Stage 5 : Correlation Analysis",
            analyze_correlations,
            self.comparison_df,
            self.output_directory / self.config.correlation_file,
        )

        return self

    # ========================================================

    def run_portfolio(self):
        """
        Stage 6
        Portfolio construction.
        """

        self._validate_comparison_dataframe()

        self.portfolio_engine = self.executor.execute(
            "Stage 6 : Portfolio Builder",
            build_portfolio,
            self.comparison_df,
            capital=self.config.capital,
            top_n=self.config.top_n,
            max_weight=self.config.max_position_weight,
            output_file=(self.output_directory / self.config.portfolio_file),
        )

        logger.info(
            "Portfolio Positions : %d",
            len(self.portfolio_engine.portfolio),
        )

        return self

    # ========================================================

    def export_final_report(self):
        """
        Stage 7
        Export consolidated institutional report.
        """

        sheets = {
            "Strategy Comparison": self.strategy_engine.comparison_df,
            "Top Opportunities": self.strategy_engine.top_opportunities_df,
            "Strategy Summary": self.strategy_engine.summary_df,
            "Stock Comparison": self.stock_engine.stock_summary,
            "Stock Rankings": self.stock_engine.stock_rankings,
            "Overall Leaderboard": self.leaderboard_engine.overall,
            "Strategy Leaderboard": self.leaderboard_engine.strategy_board,
            "Stock Leaderboard": self.leaderboard_engine.stock_board,
            "Edge Leaderboard": self.leaderboard_engine.edge_board,
            "Robustness": self.robustness_engine.robustness,
            "Consistency": self.robustness_engine.consistency,
            "Correlation": self.correlation_engine.pearson,
            "Diversification": self.correlation_engine.diversification,
            "Portfolio": self.portfolio_engine.portfolio,
            "Portfolio Summary": self.portfolio_engine.summary,
            "Strategy Rankings": self.strategy_engine.strategy_ranking_df,
            "Strategy Recommendations": self.strategy_engine.recommendation_df,
        }

        self.executor.execute(
            "Stage 7 : Export Final Report",
            export_excel,
            self.output_directory / self.config.final_report_file,
            sheets,
        )

        logger.info(
            "Worksheets Exported : %d",
            len(sheets),
        )

        return self

    # ============================================================
    # Diagnostics
    # ============================================================

    def build_diagnostics(self):
        """
        Generate execution statistics.
        """

        self._validate_comparison_dataframe()

        self.diagnostics.strategies = self.comparison_df["Strategy"].nunique()

        self.diagnostics.stocks = self.comparison_df["Stock"].nunique()

        self.diagnostics.rows = len(self.comparison_df)

        self.diagnostics.portfolio_positions = len(self.portfolio_engine.portfolio)

        self.diagnostics.execution_time = round(
            self.execution_time,
            3,
        )

        banner(
            logger,
            "Pipeline Summary",
        )

        logger.info(
            "Strategies           : %d",
            self.diagnostics.strategies,
        )

        logger.info(
            "Stocks               : %d",
            self.diagnostics.stocks,
        )

        logger.info(
            "Rows                 : %d",
            self.diagnostics.rows,
        )

        logger.info(
            "Portfolio Positions  : %d",
            self.diagnostics.portfolio_positions,
        )

        logger.info(
            "Execution Time       : %.3f sec",
            self.diagnostics.execution_time,
        )

        logger.info("Stage Performance")

        for stage, elapsed in self.diagnostics.stage_times.items():
            logger.info(
                "  %-35s %.3f sec",
                stage,
                elapsed,
            )

        return self

    # ============================================================
    # Pipeline Execution
    # ============================================================

    def run(self):
        """
        Execute the complete institutional pipeline.
        """

        self.state = PipelineState.RUNNING

        start = time.perf_counter()

        pipeline = [
            self.run_derived_metrics,
            self.run_strategy_comparison,
            self.run_stock_comparison,
            self.run_leaderboards,
            self.run_robustness,
            self.run_correlation,
            self.run_portfolio,
            self.export_final_report,
        ]

        try:
            total = len(pipeline)

            for index, stage in enumerate(
                pipeline,
                start=1,
            ):
                logger.info(
                    "[%d/%d] %s",
                    index,
                    total,
                    stage.__name__,
                )

                stage()

            self.state = PipelineState.SUCCESS

        except Exception:
            self.state = PipelineState.FAILED

            logger.exception("Pipeline execution failed.")

            raise

        finally:
            self.execution_time = time.perf_counter() - start

            self.build_diagnostics()

            banner(
                logger,
                "Pipeline Completed",
            )

            logger.info(
                "Pipeline State : %s",
                self.state.name,
            )

            logger.info(
                "Execution Time : %.3f sec",
                self.execution_time,
            )

        return self

    # ============================================================
    # Pipeline Result
    # ============================================================

    def get_results(
        self,
    ) -> PipelineResult:
        """
        Return all generated outputs.
        """

        return PipelineResult(
            comparison_df=self.comparison_df,
            strategy_engine=self.strategy_engine,
            stock_engine=self.stock_engine,
            leaderboard_engine=self.leaderboard_engine,
            robustness_engine=self.robustness_engine,
            correlation_engine=self.correlation_engine,
            portfolio_engine=self.portfolio_engine,
            diagnostics=self.diagnostics,
            execution_time=self.execution_time,
        )


# ============================================================
# Convenience Function
# ============================================================


def run_strategy_comparison_pipeline(
    config: PipelineConfig | None = None,
) -> PipelineResult:
    """
    Execute the complete pipeline.

    Parameters
    ----------
    config
        Pipeline configuration.

    Returns
    -------
    PipelineResult
    """

    banner(
        logger,
        "Launching Institutional Strategy Comparison Platform",
    )

    engine = StrategyComparisonPlatform(
        config=config,
    )

    engine.run()

    logger.info("Pipeline finished successfully.")

    return engine.get_results()


# ============================================================
# Command Line Interface
# ============================================================


def parse_arguments():
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(
        prog="strategy_comparison",
        description=("Institutional Strategy Comparison Platform V4"),
    )

    parser.add_argument(
        "--input",
        default=INPUT_DIRECTORY,
        help="Input directory",
    )

    parser.add_argument(
        "--output",
        default=OUTPUT_DIRECTORY,
        help="Output directory",
    )

    parser.add_argument(
        "--capital",
        default=CAPITAL,
        type=float,
        help="Portfolio capital",
    )

    parser.add_argument(
        "--top",
        default=TOP_STOCKS,
        type=int,
        help="Top N stocks",
    )

    parser.add_argument(
        "--max-weight",
        default=MAX_POSITION_WEIGHT,
        type=float,
        help="Maximum position weight",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================


def main():
    """
    Application entry point.
    """

    args = parse_arguments()

    config = PipelineConfig(
        input_directory=Path(
            args.input,
        ),
        output_directory=Path(
            args.output,
        ),
        capital=args.capital,
        top_n=args.top,
        max_position_weight=args.max_weight,
    )

    result = run_strategy_comparison_pipeline(
        config=config,
    )

    banner(
        logger,
        "Execution Summary",
    )

    logger.info(
        "Strategies          : %d",
        result.diagnostics.strategies,
    )

    logger.info(
        "Stocks              : %d",
        result.diagnostics.stocks,
    )

    logger.info(
        "Rows                : %d",
        result.diagnostics.rows,
    )

    logger.info(
        "Portfolio Positions : %d",
        result.diagnostics.portfolio_positions,
    )

    logger.info(
        "Execution Time      : %.3f sec",
        result.execution_time,
    )

    logger.info(
        "Output Directory    : %s",
        config.output_directory,
    )


# ============================================================
# CLI Entry
# ============================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user.")

    except Exception:
        logger.exception("Unexpected fatal error.")

        raise
