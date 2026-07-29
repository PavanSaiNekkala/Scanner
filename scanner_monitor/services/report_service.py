"""
report_service.py
=================

Institutional Portfolio Reporting Engine

Responsibilities
----------------
• Portfolio Summary
• Holdings Report
• Risk Report
• Execution Report
• Performance Report
• Sector Allocation
• Attribution Analysis
• Charts
• Excel Export
• PDF Export
• HTML Dashboard
• JSON Export

This module contains no Streamlit code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

import logging

import numpy as np
import pandas as pd

from .execution_service import ExecutionResult
from .portfolio_manager import PortfolioResult
from .risk_manager import RiskResult

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True)
class ReportConfig:
    """
    Institutional reporting configuration.
    """

    output_directory: Path = Path("scanner_monitor/reports")

    latest_directory: str = "latest"

    history_directory: str = "history"

    report_name: str = "Portfolio_Report"

    export_excel: bool = True

    export_csv: bool = True

    export_json: bool = True

    export_html: bool = False

    export_pdf: bool = False

    include_charts: bool = True

    overwrite: bool = False

    append_history: bool = True


# =============================================================================
# Statistics
# =============================================================================

@dataclass
class ReportStatistics:
    """
    Report generation statistics.
    """

    generated_reports: int = 0

    exported_files: int = 0

    total_size_bytes: int = 0

    total_size_mb: float = 0.0

    generated_at: datetime | None = None

    generation_time: float = 0.0

    warnings: list[str] = field(
        default_factory=list,
    )

# =============================================================================
# Report Model
# =============================================================================


@dataclass
class ReportResult:

    portfolio_summary: pd.DataFrame

    holdings: pd.DataFrame

    risk_summary: pd.DataFrame

    execution_summary: pd.DataFrame

    statistics: ReportStatistics

    exported_files: list[Path]

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# =============================================================================
# Report Service
# =============================================================================


class ReportService:
    """
    Institutional reporting engine.

    Workflow
    --------

    Portfolio
          │
          ▼
    Holdings Report
          │
          ▼
    Risk Report
          │
          ▼
    Execution Report
          │
          ▼
    Performance Report
          │
          ▼
    Export
    """

    def __init__(
        self,
        config: ReportConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else ReportConfig()
        )

        self.config.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "ReportService initialized."
        )


    def _remove_timezone(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove timezone information from datetime columns
        before exporting to Excel.
        """

        df = df.copy()

        for column in df.columns:

            if pd.api.types.is_datetime64tz_dtype(
                df[column]
            ):

                df[column] = (
                    df[column]
                    .dt.tz_localize(None)
                )

        return df
    

    def _prepare_directories(self):

        latest = (
            self.config.output_directory
            /
            self.config.latest_directory
        )


        history = (
            self.config.output_directory
            /
            self.config.history_directory
        )


        latest.mkdir(
            parents=True,
            exist_ok=True,
        )


        history.mkdir(
            parents=True,
            exist_ok=True,
        )


        return latest, history


    def _append_history(
        self,
        df: pd.DataFrame,
        filename: str,
        history_dir: Path,
    ):

        if df.empty:

            return

        file = (
            history_dir
            /
            filename
        )


        # ---------------------------------------
        # Add new history
        # ---------------------------------------

        if file.exists():

            old = pd.read_csv(
                file
            )


            combined = pd.concat(
                [
                    old,
                    df,
                ],
                ignore_index=True,
            )


        else:

            combined = df.copy()



        # ---------------------------------------
        # Remove duplicate executions
        # ---------------------------------------

        duplicate_keys = []


        if "timestamp" in combined.columns:

            combined["date"] = (
                pd.to_datetime(
                    combined["timestamp"]
                )
                .dt.date
            )


        if "date" in combined.columns:

            duplicate_keys.append(
                "date"
            )


        if "ticker" in combined.columns:

            duplicate_keys.append(
                "ticker"
            )


        # ---------------------------------------
        # Remove duplicates only when keys exist
        # ---------------------------------------

        if duplicate_keys:

            combined = (
                combined
                .drop_duplicates(
                    subset=duplicate_keys,
                    keep="last",
                )
            )


        # ---------------------------------------
        # Save
        # ---------------------------------------

        combined.to_csv(
            file,
            index=False,
        )

        if df.empty:

            return


        file = (
            history_dir
            /
            filename
        )


        if file.exists():

            old = pd.read_csv(
                file
            )


            df = pd.concat(
                [
                    old,
                    df,
                ],
                ignore_index=True,
            )


        df.to_csv(
            file,
            index=False,
        )
    

    # =========================================================
    # Public API
    # =========================================================

    def generate(
        self,
        portfolio: PortfolioResult,
        risk: RiskResult,
        execution: ExecutionResult,
    ) -> ReportResult:
        """
        Generate complete institutional reports.
        """

    
        run_time = datetime.now(ZoneInfo("Asia/Kolkata"))


        run_id = (
            run_time.strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        latest_dir, history_dir = (
            self._prepare_directories()
        )

        logger.info(
            "Generating portfolio reports."
        )

        start_time = datetime.now(ZoneInfo("Asia/Kolkata"))

        # -----------------------------------------------------
        # Portfolio
        # -----------------------------------------------------

        portfolio_summary = (
            self._portfolio_summary(
                portfolio,
            )
        )

        holdings = (
            portfolio.portfolio.copy()
        )

        holdings["run_id"] = run_id

        holdings["timestamp"] = run_time

        # -----------------------------------------------------
        # Signal History Snapshot
        # -----------------------------------------------------

        signal_history = holdings.copy()


        signal_columns = [

            "ticker",
            "signals_today",
            "confidence",
            "rank_score",
            "portfolio_rank",
            "regime_today",
            "run_id",
            "timestamp",

        ]


        signal_history = (
            signal_history[
                [
                    col
                    for col in signal_columns
                    if col in signal_history.columns
                ]
            ]
        )


        # -----------------------------------------------------
        # Performance History Snapshot
        # -----------------------------------------------------

        performance_history = holdings.copy()


        performance_columns = [

            "ticker",
            "expectancy",
            "win_rate",
            "cagr_%",
            "max_drawdown_%",
            "profit_factor",
            "reward_risk_ratio",
            "run_id",
            "timestamp",

        ]


        performance_history = (
            performance_history[
                [
                    col
                    for col in performance_columns
                    if col in performance_history.columns
                ]
            ]
        )

        # -----------------------------------------------------
        # Regime History Snapshot
        # -----------------------------------------------------

        regime_history = holdings.copy()


        regime_columns = [

            "ticker",
            "regime_today",
            "day_chg_%",
            "above_50dma",
            "run_id",
            "timestamp",

        ]


        regime_history = (
            regime_history[
                [
                    col
                    for col in regime_columns
                    if col in regime_history.columns
                ]
            ]
        )


        self._append_history(
            regime_history,
            "regime_history.csv",
            history_dir,
        )

        # -----------------------------------------------------
        # Risk
        # -----------------------------------------------------

        risk_summary = (
            self._risk_summary(
                risk,
            )
        )

        # -----------------------------------------------------
        # Execution
        # -----------------------------------------------------

        execution_summary = (
            self._execution_summary(
                execution,
            )
        )

        exported_files: list[Path] = []

        # -----------------------------------------------------
        # Create Result
        # -----------------------------------------------------

        result = ReportResult(
            portfolio_summary=portfolio_summary,
            holdings=holdings,
            risk_summary=risk_summary,
            execution_summary=execution_summary,
            statistics=ReportStatistics(),
            exported_files=[],
            metadata={
                "generated_at": datetime.now(ZoneInfo("Asia/Kolkata")),
            },
        )


        run_id = datetime.now(ZoneInfo("Asia/Kolkata")).strftime(
            "%Y%m%d_%H%M%S"
        )


        #run_directory = (
            #self.config.output_directory
            #/
            #"runs"
            #/
            #run_id
        #)


        #run_directory.mkdir(
            #parents=True,
            #exist_ok=True,
        #)

        # -----------------------------------------------------
        # Export Excel
        # -----------------------------------------------------

        if self.config.export_excel:

            exported_files.append(
                self._export_excel(
                    result,
                )
            )

        # -----------------------------------------------------
        # Export CSV
        # -----------------------------------------------------

        result.holdings["run_id"] = run_id

        result.holdings["timestamp"] = run_time

        if self.config.export_csv:

            exported_files.extend(
                self._export_csv(
                    result,
                )
            )

        # -----------------------------------------------------
        # Additional Historical Tracking
        # -----------------------------------------------------

        if self.config.append_history:


            self._append_history(
                signal_history,
                "signal_history.csv",
                history_dir,
            )


            self._append_history(
                performance_history,
                "performance_history.csv",
                history_dir,
            )


        # -----------------------------------------------------
        # Export JSON
        # -----------------------------------------------------

        if self.config.export_json:

            exported_files.append(
                self._export_json(
                    result,
                )
            )

        # -----------------------------------------------------
        # Export HTML
        # -----------------------------------------------------

        if self.config.export_html:

            exported_files.append(
                self._export_html(
                    result,
                )
            )

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        result.exported_files = exported_files

        result.statistics = (
            self._compute_statistics(
                exported_files,
            )
        )

        result.metadata.update(
            {
                "duration_seconds": (
                    datetime.now(ZoneInfo("Asia/Kolkata"))
                    - start_time
                ).total_seconds(),
                "report_directory": str(
                    latest_dir
                ),
            }
        )

        logger.info(
            "Generated %d report files.",
            len(exported_files),
        )

        return result
    
    # =========================================================
    # Internal Methods
    # =========================================================

    def _portfolio_summary(
        self,
        portfolio: PortfolioResult,
    ) -> pd.DataFrame:
        """
        Build portfolio summary report.
        """

        positions = portfolio.portfolio.copy()

        if positions.empty:

            return pd.DataFrame(
                columns=[
                    "Metric",
                    "Value",
                ]
            )

        summary = []

        # =====================================================
        # Basic Portfolio
        # =====================================================

        total_positions = len(positions)

        total_weight = float(
            positions["weight"].sum()
        )

        invested_weight = float(
            positions["weight"].sum()
        )

        cash_weight = max(
            0.0,
            1.0 - invested_weight,
        )

        largest_position = float(
            positions["weight"].max()
        )

        smallest_position = float(
            positions["weight"].min()
        )

        average_weight = float(
            positions["weight"].mean()
        )

        median_weight = float(
            positions["weight"].median()
        )

        # =====================================================
        # Sector Information
        # =====================================================

        if "sector" in positions.columns:

            sector_count = int(
                positions["sector"]
                .nunique()
            )

            largest_sector = (
                positions
                .groupby("sector")["weight"]
                .sum()
                .idxmax()
            )

            largest_sector_weight = float(
                positions
                .groupby("sector")["weight"]
                .sum()
                .max()
            )

        else:

            sector_count = 0

            largest_sector = "N/A"

            largest_sector_weight = 0.0

        # =====================================================
        # Expected Return
        # =====================================================

        if "expected_return" in positions.columns:

            expected_return = float(
                np.sum(
                    positions["weight"]
                    * positions["expected_return"]
                )
            )

        else:

            expected_return = np.nan

        # =====================================================
        # Expected Beta
        # =====================================================

        if "beta" in positions.columns:

            portfolio_beta = float(
                np.sum(
                    positions["weight"]
                    * positions["beta"]
                )
            )

        else:

            portfolio_beta = np.nan

        # =====================================================
        # Expected Volatility
        # =====================================================

        if "volatility" in positions.columns:

            portfolio_volatility = float(
                np.sum(
                    positions["weight"]
                    * positions["volatility"]
                )
            )

        else:

            portfolio_volatility = np.nan

        # =====================================================
        # Summary
        # =====================================================

        summary.extend(

            [

                ("Portfolio Holdings", total_positions),

                ("Total Weight", total_weight),

                ("Invested Weight", invested_weight),

                ("Cash Weight", cash_weight),

                ("Largest Position", largest_position),

                ("Smallest Position", smallest_position),

                ("Average Position", average_weight),

                ("Median Position", median_weight),

                ("Sector Count", sector_count),

                ("Largest Sector", largest_sector),

                ("Largest Sector Weight", largest_sector_weight),

                ("Expected Return", expected_return),

                ("Portfolio Beta", portfolio_beta),

                ("Portfolio Volatility", portfolio_volatility),

            ]

        )

        report = pd.DataFrame(
            summary,
            columns=[
                "Metric",
                "Value",
            ],
        )

        logger.info(
            "Portfolio summary generated."
        )

        return report
    

    def _risk_summary(
        self,
        risk: RiskResult,
    ) -> pd.DataFrame:
        """
        Build portfolio risk summary report.

        Returns
        -------
        pd.DataFrame
            Risk metrics report.
        """

        stats = risk.statistics

        summary: list[tuple[str, Any]] = [

            # =====================================================
            # Exposure
            # =====================================================

            (
                "Gross Exposure",
                stats.gross_exposure,
            ),

            (
                "Net Exposure",
                stats.net_exposure,
            ),

            # =====================================================
            # Portfolio Risk
            # =====================================================

            (
                "Portfolio Beta",
                stats.portfolio_beta,
            ),

            (
                "Portfolio Volatility",
                stats.volatility,
            ),

            (
                "Annualized Volatility",
                stats.annualized_volatility,
            ),

            # =====================================================
            # Diversification
            # =====================================================

            (
                "HHI",
                stats.hhi,
            ),

            (
                "Effective Positions",
                stats.effective_positions,
            ),

            (
                "Largest Position",
                stats.largest_position,
            ),

            (
                "Sector Count",
                stats.sector_count,
            ),

            # =====================================================
            # Tail Risk
            # =====================================================

            (
                "Value at Risk",
                stats.value_at_risk,
            ),

            (
                "Expected Shortfall",
                stats.expected_shortfall,
            ),

            (
                "Maximum Drawdown",
                stats.max_drawdown,
            ),

            # =====================================================
            # Violations
            # =====================================================

            (
                "Risk Violations",
                len(risk.violations),
            ),
        ]

        # ---------------------------------------------------------
        # Risk Score
        # ---------------------------------------------------------

        risk_score = risk.metadata.get(
            "risk_score",
            np.nan,
        )

        summary.append(

            (
                "Overall Risk Score",
                risk_score,
            )

        )

        report = pd.DataFrame(
            summary,
            columns=[
                "Metric",
                "Value",
            ],
        )

        # ---------------------------------------------------------
        # Risk Rating
        # ---------------------------------------------------------

        if not np.isnan(risk_score):

            if risk_score >= 90:
                rating = "Excellent"

            elif risk_score >= 75:
                rating = "Good"

            elif risk_score >= 60:
                rating = "Moderate"

            elif risk_score >= 40:
                rating = "High Risk"

            else:
                rating = "Critical"

            report.loc[
                len(report)
            ] = [
                "Risk Rating",
                rating,
            ]

        logger.info(
            "Risk summary generated."
        )

        return report

    
    def _execution_summary(
        self,
        execution: ExecutionResult,
    ) -> pd.DataFrame:
        """
        Build execution summary report.

        Returns
        -------
        pd.DataFrame
            Execution metrics.
        """

        stats = execution.statistics

        orders = execution.orders.copy()

        summary: list[tuple[str, Any]] = [

            # =====================================================
            # Order Counts
            # =====================================================

            (
                "Total Orders",
                stats.total_orders,
            ),

            (
                "Buy Orders",
                stats.buy_orders,
            ),

            (
                "Sell Orders",
                stats.sell_orders,
            ),

            # =====================================================
            # Execution
            # =====================================================

            (
                "Executed Value",
                stats.total_execution_value,
            ),

            (
                "Portfolio Turnover",
                stats.turnover,
            ),

            # =====================================================
            # Costs
            # =====================================================

            (
                "Estimated Cost",
                stats.estimated_cost,
            ),

            (
                "Slippage Cost",
                stats.slippage_cost,
            ),

        ]

        # =====================================================
        # Order Status
        # =====================================================

        if not orders.empty:

            valid_orders = (
                orders["validation_status"]
                == "VALID"
            ).sum()

            rejected_orders = (
                orders["validation_status"]
                == "REJECTED"
            ).sum()

            summary.extend(

                [

                    (
                        "Valid Orders",
                        int(valid_orders),
                    ),

                    (
                        "Rejected Orders",
                        int(rejected_orders),
                    ),

                ]

            )

        # =====================================================
        # Average Order Size
        # =====================================================

        if (
            not orders.empty
            and "executed_value" in orders.columns
        ):

            summary.append(

                (
                    "Average Order Value",
                    float(
                        orders[
                            "executed_value"
                        ].mean()
                    ),
                )

            )

        # =====================================================
        # Average Quantity
        # =====================================================

        if (
            not orders.empty
            and "quantity" in orders.columns
        ):

            summary.append(

                (
                    "Average Quantity",
                    float(
                        orders[
                            "quantity"
                        ].mean()
                    ),
                )

            )

        # =====================================================
        # Average Fill Price
        # =====================================================

        if (
            not orders.empty
            and "fill_price" in orders.columns
        ):

            summary.append(

                (
                    "Average Fill Price",
                    float(
                        orders[
                            "fill_price"
                        ].mean()
                    ),
                )

            )

        # =====================================================
        # Execution Efficiency
        # =====================================================

        if (
            not orders.empty
            and "execution_efficiency"
            in orders.columns
        ):

            summary.append(

                (
                    "Execution Efficiency",
                    float(
                        orders[
                            "execution_efficiency"
                        ].mean()
                    ),
                )

            )

        # =====================================================
        # Average Participation Rate
        # =====================================================

        if (
            not orders.empty
            and "participation_rate"
            in orders.columns
        ):

            summary.append(

                (
                    "Average Participation Rate",
                    float(
                        orders[
                            "participation_rate"
                        ]
                        .fillna(0)
                        .mean()
                    ),
                )

            )

        # =====================================================
        # Fill Rate
        # =====================================================

        if (
            not orders.empty
            and "fill_status"
            in orders.columns
        ):

            filled = (
                orders["fill_status"]
                == "FILLED"
            ).sum()

            fill_rate = (
                filled
                / len(orders)
            )

            summary.append(

                (
                    "Fill Rate",
                    float(fill_rate),
                )

            )

        report = pd.DataFrame(
            summary,
            columns=[
                "Metric",
                "Value",
            ],
        )

        logger.info(
            "Execution summary generated."
        )

        return report

    
    def _performance_summary(
        self,
        portfolio: PortfolioResult,
    ) -> pd.DataFrame:
        """
        Build portfolio performance summary.

        Returns
        -------
        pd.DataFrame
            Performance metrics report.
        """

        positions = portfolio.portfolio.copy()

        summary: list[tuple[str, Any]] = []

        if positions.empty:

            return pd.DataFrame(
                columns=[
                    "Metric",
                    "Value",
                ]
            )

        # =====================================================
        # Portfolio Return
        # =====================================================

        if (
            "expected_return" in positions.columns
        ):

            portfolio_return = float(
                np.sum(
                    positions["weight"]
                    * positions["expected_return"]
                )
            )

        else:

            portfolio_return = np.nan

        summary.append(

            (
                "Expected Portfolio Return",
                portfolio_return,
            )

        )

        # =====================================================
        # Benchmark Return
        # =====================================================

        benchmark_return = (
            portfolio.metadata.get(
                "benchmark_return",
                np.nan,
            )
        )

        summary.append(

            (
                "Benchmark Return",
                benchmark_return,
            )

        )

        # =====================================================
        # Alpha
        # =====================================================

        if (
            not np.isnan(portfolio_return)
            and not np.isnan(benchmark_return)
        ):

            alpha = (
                portfolio_return
                - benchmark_return
            )

        else:

            alpha = np.nan

        summary.append(

            (
                "Alpha",
                alpha,
            )

        )

        # =====================================================
        # Beta
        # =====================================================

        if "beta" in positions.columns:

            beta = float(

                np.sum(

                    positions["weight"]
                    * positions["beta"]

                )

            )

        else:

            beta = np.nan

        summary.append(

            (
                "Portfolio Beta",
                beta,
            )

        )

        # =====================================================
        # Volatility
        # =====================================================

        if "volatility" in positions.columns:

            volatility = float(

                np.sum(

                    positions["weight"]
                    * positions["volatility"]

                )

            )

        else:

            volatility = np.nan

        summary.append(

            (
                "Portfolio Volatility",
                volatility,
            )

        )

        # =====================================================
        # Sharpe Ratio
        # =====================================================

        if (
            not np.isnan(portfolio_return)
            and not np.isnan(volatility)
            and volatility > 0
        ):

            sharpe = (

                portfolio_return
                / volatility

            )

        else:

            sharpe = np.nan

        summary.append(

            (
                "Sharpe Ratio",
                sharpe,
            )

        )

        # =====================================================
        # Sortino Ratio
        # =====================================================

        if (
            "returns" in positions.columns
        ):

            downside = []

            for _, row in positions.iterrows():

                r = pd.Series(
                    row["returns"]
                ).dropna()

                negative = r[
                    r < 0
                ]

                if len(negative):

                    downside.extend(
                        negative.tolist()
                    )

            if downside:

                downside_std = np.std(
                    downside
                )

                if downside_std > 0:

                    sortino = (
                        portfolio_return
                        / downside_std
                    )

                else:

                    sortino = np.nan

            else:

                sortino = np.nan

        else:

            sortino = np.nan

        summary.append(

            (
                "Sortino Ratio",
                sortino,
            )

        )

        # =====================================================
        # Maximum Drawdown
        # =====================================================

        max_drawdown = portfolio.metadata.get(
            "max_drawdown",
            np.nan,
        )

        summary.append(

            (
                "Maximum Drawdown",
                max_drawdown,
            )

        )

        # =====================================================
        # CAGR
        # =====================================================

        cagr = portfolio.metadata.get(
            "cagr",
            np.nan,
        )

        summary.append(

            (
                "CAGR",
                cagr,
            )

        )

        # =====================================================
        # Win Rate
        # =====================================================

        win_rate = portfolio.metadata.get(
            "win_rate",
            np.nan,
        )

        summary.append(

            (
                "Win Rate",
                win_rate,
            )

        )

        # =====================================================
        # Profit Factor
        # =====================================================

        profit_factor = portfolio.metadata.get(
            "profit_factor",
            np.nan,
        )

        summary.append(

            (
                "Profit Factor",
                profit_factor,
            )

        )

        # =====================================================
        # Information Ratio
        # =====================================================

        information_ratio = portfolio.metadata.get(
            "information_ratio",
            np.nan,
        )

        summary.append(

            (
                "Information Ratio",
                information_ratio,
            )

        )

        report = pd.DataFrame(

            summary,

            columns=[
                "Metric",
                "Value",
            ],

        )

        logger.info(
            "Performance summary generated."
        )

        return report

    
    def _export_excel(
        self,
        result: ReportResult,
    ) -> Path:
        """
        Export institutional report to Excel.

        Returns
        -------
        Path
            Excel report path.
        """

        latest_dir, _ = (
            self._prepare_directories()
        )


        output_file = (
            latest_dir
            /
            f"{self.config.report_name}.xlsx"
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl",
        ) as writer:

            # =====================================================
            # Portfolio Summary
            # =====================================================

            self._remove_timezone(
                result.portfolio_summary,
            ).to_excel(
                writer,
                sheet_name="Portfolio Summary",
                index=False,
            )

            # =====================================================
            # Holdings
            # =====================================================

            self._remove_timezone(
                result.holdings,
            ).to_excel(
                writer,
                sheet_name="Holdings",
            )

            # =====================================================
            # Risk Summary
            # =====================================================

            self._remove_timezone(
                result.risk_summary,
            ).to_excel(
                writer,
                sheet_name="Risk Summary",
                index=False,
            )

            # =====================================================
            # Execution Summary
            # =====================================================

            self._remove_timezone(
                result.execution_summary,
            ).to_excel(
                writer,
                sheet_name="Execution Summary",
                index=False,
            )

            # =====================================================
            # Performance
            # =====================================================

            if (
                "performance_summary"
                in result.metadata
            ):

                self._remove_timezone(
                    result.metadata[
                        "performance_summary"
                    ],
                ).to_excel(
                    writer,
                    sheet_name="Performance",
                    index=False,
                )

            # =====================================================
            # Risk Violations
            # =====================================================

            violations = result.metadata.get(
                "risk_violations",
            )

            if isinstance(
                violations,
                pd.DataFrame,
            ):

                self._remove_timezone(
                    violations,
                ).to_excel(
                    writer,
                    sheet_name="Risk Violations",
                    index=False,
                )

            # =====================================================
            # Sector Exposure
            # =====================================================

            exposure = result.metadata.get(
                "sector_exposure",
            )

            if isinstance(
                exposure,
                pd.DataFrame,
            ):

                self._remove_timezone(
                    exposure,
                ).to_excel(
                    writer,
                    sheet_name="Sector Exposure",
                    index=False,
                )

            # =====================================================
            # Orders
            # =====================================================

            orders = result.metadata.get(
                "orders",
            )

            if isinstance(
                orders,
                pd.DataFrame,
            ):

                self._remove_timezone(
                    orders,
                ).to_excel(
                    writer,
                    sheet_name="Orders",
                    index=False,
                )

            # =====================================================
            # Metadata
            # =====================================================

            metadata = pd.DataFrame(
                {
                    "Key": list(
                        result.metadata.keys()
                    ),
                    "Value": [
                        str(v)
                        for v in result.metadata.values()
                    ],
                }
            )

            self._remove_timezone(
                metadata,
            ).to_excel(
                writer,
                sheet_name="Metadata",
                index=False,
            )

            # =====================================================
            # Auto Width
            # =====================================================

            for sheet in writer.sheets.values():

                for column_cells in sheet.columns:

                    length = max(
                        len(str(cell.value))
                        if cell.value is not None
                        else 0
                        for cell in column_cells
                    )

                    sheet.column_dimensions[
                        column_cells[0].column_letter
                    ].width = min(
                        max(length + 2, 12),
                        40,
                    )

        logger.info(
            "Excel report exported: %s",
            output_file,
        )

        return output_file

    
    def _export_csv(
        self,
        result: ReportResult,
    ) -> list[Path]:
        """
        Export all reports to CSV files.

        Returns
        -------
        list[Path]
            Exported CSV file paths.
        """

        exported: list[Path] = []

        reports = {

            "portfolio_summary.csv":
                result.portfolio_summary,

            "holdings.csv":
                result.holdings,

            "risk_summary.csv":
                result.risk_summary,

            "execution_summary.csv":
                result.execution_summary,

        }

        # -----------------------------------------------------
        # Optional Reports
        # -----------------------------------------------------

        if hasattr(result, "performance_summary"):

            reports[
                "performance_summary.csv"
            ] = result.performance_summary

        if hasattr(result, "risk_violations"):

            reports[
                "risk_violations.csv"
            ] = result.risk_violations

        if hasattr(result, "sector_exposure"):

            reports[
                "sector_exposure.csv"
            ] = result.sector_exposure

        if hasattr(result, "orders"):

            reports[
                "orders.csv"
            ] = result.orders

        # -----------------------------------------------------
        # Export
        # -----------------------------------------------------

        for filename, dataframe in reports.items():

            if (
                dataframe is None
                or dataframe.empty
            ):
                continue

            latest_dir, history_dir = (
                self._prepare_directories()
            )


            # -------------------------------
            # Latest snapshot
            # -------------------------------

            latest_file = (
                latest_dir
                /
                filename
            )


            dataframe.to_csv(
                latest_file,
                index=False,
            )


            exported.append(
                latest_file,
            )


            # -------------------------------
            # History append
            # -------------------------------

            history_map = {

                "portfolio_summary.csv":
                    "portfolio_history.csv",

                "holdings.csv":
                    "portfolio_history.csv",

                "risk_summary.csv":
                    "risk_history.csv",

                "execution_summary.csv":
                    "execution_history.csv",

                "performance_summary.csv":
                    "performance_history.csv",

                "orders.csv":
                    "execution_history.csv",

            }


            history_filename = (
                history_map.get(
                    filename,
                    filename.replace(
                        ".csv",
                        "_history.csv",
                    ),
                )
            )

            self._append_history(
                dataframe,
                history_filename,
                history_dir,
            )

        logger.info(
            "Exported %d CSV reports.",
            len(exported),
        )

        return exported

    
    def _export_json(
        self,
        result: ReportResult,
    ) -> Path:
        """
        Export institutional report as JSON.

        Returns
        -------
        Path
            JSON report path.
        """

        import json

        latest_dir, _ = (
            self._prepare_directories()
        )

        output_file = (
            latest_dir
            /
            f"{self.config.report_name}.json"
        )

        report = {

            # -----------------------------------------------------
            # Metadata
            # -----------------------------------------------------

            "metadata": {

                "report_name": self.config.report_name,

                "generated_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),

                "version": "1.0",

                **{
                    k: str(v)
                    for k, v in result.metadata.items()
                },

            },

            # -----------------------------------------------------
            # Core Reports
            # -----------------------------------------------------

            "portfolio_summary":
                result.portfolio_summary.to_dict(
                    orient="records",
                ),

            "holdings":
                result.holdings.to_dict(
                    orient="records",
                ),

            "risk_summary":
                result.risk_summary.to_dict(
                    orient="records",
                ),

            "execution_summary":
                result.execution_summary.to_dict(
                    orient="records",
                ),

        }

        # -----------------------------------------------------
        # Optional Reports
        # -----------------------------------------------------

        if hasattr(
            result,
            "performance_summary",
        ):

            report[
                "performance_summary"
            ] = result.performance_summary.to_dict(
                orient="records",
            )

        if hasattr(
            result,
            "risk_violations",
        ):

            report[
                "risk_violations"
            ] = result.risk_violations.to_dict(
                orient="records",
            )

        if hasattr(
            result,
            "sector_exposure",
        ):

            report[
                "sector_exposure"
            ] = result.sector_exposure.to_dict(
                orient="records",
            )

        if hasattr(
            result,
            "orders",
        ):

            report[
                "orders"
            ] = result.orders.to_dict(
                orient="records",
            )

        # -----------------------------------------------------
        # Write JSON
        # -----------------------------------------------------

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                default=str,
            )

        logger.info(
            "JSON report exported: %s",
            output_file,
        )

        return output_file

    
    def _export_html(
        self,
        result: ReportResult,
    ) -> Path:
        """
        Export institutional report as HTML.

        Returns
        -------
        Path
            HTML report path.
        """

        output_file = (
            self.config.output_directory
            / f"{self.config.report_name}.html"
        )

        html = []

        # =====================================================
        # Header
        # =====================================================

        html.append(
            """
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">

<title>Institutional Portfolio Report</title>

<style>

body{
    font-family:Arial,Helvetica,sans-serif;
    margin:30px;
    background:#fafafa;
}

h1{
    color:#1f2937;
}

h2{
    margin-top:40px;
    border-bottom:2px solid #cccccc;
    padding-bottom:6px;
}

table{
    border-collapse:collapse;
    width:100%;
    margin-top:10px;
}

th,td{
    border:1px solid #d0d0d0;
    padding:8px;
    text-align:left;
}

th{
    background:#f0f0f0;
}

.small{
    color:#666;
    font-size:13px;
}

</style>

</head>

<body>

<h1>Institutional Portfolio Report</h1>

<p class="small">
Generated:
"""
        )

        html.append(str(datetime.now(ZoneInfo("Asia/Kolkata"))))

        html.append("</p>")

        # =====================================================
        # Portfolio Summary
        # =====================================================

        html.append("<h2>Portfolio Summary</h2>")

        html.append(
            result.portfolio_summary.to_html(
                index=False,
                border=0,
            )
        )

        # =====================================================
        # Holdings
        # =====================================================

        html.append("<h2>Holdings</h2>")

        html.append(
            result.holdings.to_html(
                index=False,
                border=0,
            )
        )

        # =====================================================
        # Risk Summary
        # =====================================================

        html.append("<h2>Risk Summary</h2>")

        html.append(
            result.risk_summary.to_html(
                index=False,
                border=0,
            )
        )

        # =====================================================
        # Execution Summary
        # =====================================================

        html.append("<h2>Execution Summary</h2>")

        html.append(
            result.execution_summary.to_html(
                index=False,
                border=0,
            )
        )

        # =====================================================
        # Optional Sections
        # =====================================================

        if hasattr(result, "performance_summary"):

            html.append(
                "<h2>Performance Summary</h2>"
            )

            html.append(
                result.performance_summary.to_html(
                    index=False,
                    border=0,
                )
            )

        if hasattr(result, "sector_exposure"):

            html.append(
                "<h2>Sector Exposure</h2>"
            )

            html.append(
                result.sector_exposure.to_html(
                    index=False,
                    border=0,
                )
            )

        if hasattr(result, "risk_violations"):

            html.append(
                "<h2>Risk Violations</h2>"
            )

            html.append(
                result.risk_violations.to_html(
                    index=False,
                    border=0,
                )
            )

        if hasattr(result, "orders"):

            html.append(
                "<h2>Orders</h2>"
            )

            html.append(
                result.orders.to_html(
                    index=False,
                    border=0,
                )
            )

        # =====================================================
        # Metadata
        # =====================================================

        html.append("<h2>Metadata</h2>")

        metadata = pd.DataFrame(

            {

                "Key": list(
                    result.metadata.keys()
                ),

                "Value": [

                    str(v)

                    for v in result.metadata.values()

                ],

            }

        )

        html.append(
            metadata.to_html(
                index=False,
                border=0,
            )
        )

        # =====================================================
        # Footer
        # =====================================================

        html.append(
            """
</body>
</html>
"""
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "\n".join(html)
            )

        logger.info(
            "HTML report exported: %s",
            output_file,
        )

        return output_file


    def _compute_statistics(
        self,
        exported_files: list[Path],
    ) -> ReportStatistics:
        """
        Compute report generation statistics.

        Parameters
        ----------
        exported_files : list[Path]
            List of exported report files.

        Returns
        -------
        ReportStatistics
            Report generation statistics.
        """

        total_size = 0

        warnings: list[str] = []

        for file in exported_files:

            try:

                if file.exists():

                    total_size += file.stat().st_size

                else:

                    warnings.append(
                        f"Missing file: {file.name}"
                    )

            except Exception as exc:

                warnings.append(
                    f"{file.name}: {exc}"
                )

        return ReportStatistics(

            generated_reports=len(exported_files),

            exported_files=len(exported_files),

            total_size_bytes=total_size,

            total_size_mb=round(
                total_size / (1024 * 1024),
                3,
            ),

            generated_at=datetime.now(ZoneInfo("Asia/Kolkata")),

            warnings=warnings,

        )
    

_REPORT_SERVICE = ReportService()


def generate_report(
    portfolio: PortfolioResult,
    risk: RiskResult,
    execution: ExecutionResult,
) -> ReportResult:
    """
    Generate institutional portfolio reports.
    """

    return _REPORT_SERVICE.generate(
        portfolio,
        risk,
        execution,
    )


__all__ = [
    "ReportConfig",
    "ReportStatistics",
    "ReportResult",
    "ReportService",
    "generate_report",
]