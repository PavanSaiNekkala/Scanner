"""
reports.py
==========

Institutional Backtest Reporting Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ReportConfig:
    """
    Report generation configuration.
    """

    output_directory: Path = Path(
        "reports"
    )

    include_performance: bool = True

    include_benchmark: bool = True

    include_drawdown: bool = True

    include_turnover: bool = True

    include_attribution: bool = True

    export_csv: bool = True

    export_excel: bool = True

    export_json: bool = True


@dataclass(slots=True)
class BacktestReport:
    """
    Institutional backtest report.
    """

    performance: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    benchmark: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    drawdown: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    turnover: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    attribution: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    portfolio_history: pd.DataFrame = field(
        default_factory=pd.DataFrame,
    )

    trades: pd.DataFrame = field(
        default_factory=pd.DataFrame,
    )

    metadata: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )


class ReportEngine:
    """
    Institutional reporting engine.
    """

    def __init__(
        self,
        config: ReportConfig,
    ) -> None:
        """
        Initialize reporting engine.
        """

        self.config = config

        self.report: (
            BacktestReport
            | None
        ) = None

        logger.info(
            "ReportEngine initialized."
        )

    def build(
        self,
        performance: dict[
            str,
            Any,
        ],
        benchmark: dict[
            str,
            Any,
        ],
        drawdown: dict[
            str,
            Any,
        ],
        turnover: dict[
            str,
            Any,
        ],
        attribution: dict[
            str,
            Any,
        ],
        portfolio_history: pd.DataFrame,
        trades: pd.DataFrame,
        **metadata: Any,
    ) -> BacktestReport:
        """
        Build a backtest report.
        """

        self.report = BacktestReport(
            performance=performance,
            benchmark=benchmark,
            drawdown=drawdown,
            turnover=turnover,
            attribution=attribution,
            portfolio_history=portfolio_history,
            trades=trades,
            metadata=metadata,
        )

        return self.report

    def performance_summary(
        self,
    ) -> pd.Series:
        """
        Return performance summary.
        """

        if self.report is None:
            raise ValueError(
                "Report has not been built."
            )

        return pd.Series(
            self.report.performance
        )

    def benchmark_summary(
        self,
    ) -> pd.Series:
        """
        Return benchmark summary.
        """

        if self.report is None:
            raise ValueError(
                "Report has not been built."
            )

        return pd.Series(
            self.report.benchmark
        )

    def drawdown_summary(
        self,
    ) -> pd.Series:
        """
        Return drawdown summary.
        """

        if self.report is None:
            raise ValueError(
                "Report has not been built."
            )

        return pd.Series(
            self.report.drawdown
        )

    def turnover_summary(
        self,
    ) -> pd.Series:
        """
        Return turnover summary.
        """

        if self.report is None:
            raise ValueError(
                "Report has not been built."
            )

        return pd.Series(
            self.report.turnover
        )

    def attribution_summary(
        self,
    ) -> pd.Series:
        """
        Return attribution summary.
        """

        if self.report is None:
            raise ValueError(
                "Report has not been built."
            )

        return pd.Series(
            self.report.attribution
        )

    def export_csv(
        self,
        filename: str = "backtest_report.csv",
    ) -> Path:
        """
        Export report summary to CSV.
        """

        path = (
            self.config.output_directory
            / filename
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.summary().to_csv(
            path,
            header=False,
        )

        logger.info(
            "CSV report exported: %s",
            path,
        )

        return path

    def export_excel(
        self,
        filename: str = "backtest_report.xlsx",
    ) -> Path:
        """
        Export report to Excel.
        """

        path = (
            self.config.output_directory
            / filename
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with pd.ExcelWriter(
            path,
        ) as writer:

            self.performance_summary().to_excel(
                writer,
                sheet_name="Performance",
            )

            self.benchmark_summary().to_excel(
                writer,
                sheet_name="Benchmark",
            )

            self.drawdown_summary().to_excel(
                writer,
                sheet_name="Drawdown",
            )

            self.turnover_summary().to_excel(
                writer,
                sheet_name="Turnover",
            )

            self.attribution_summary().to_excel(
                writer,
                sheet_name="Attribution",
            )

            self.report.portfolio_history.to_excel(
                writer,
                sheet_name="Portfolio",
                index=False,
            )

            self.report.trades.to_excel(
                writer,
                sheet_name="Trades",
                index=False,
            )

        logger.info(
            "Excel report exported: %s",
            path,
        )

        return path

    def export_json(
        self,
        filename: str = "backtest_report.json",
    ) -> Path:
        """
        Export report to JSON.
        """

        path = (
            self.config.output_directory
            / filename
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.summary(),
                file,
                indent=4,
                default=str,
            )

        logger.info(
            "JSON report exported: %s",
            path,
        )

        return path

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return complete report summary.
        """

        if self.report is None:
            raise ValueError(
                "Report has not been built."
            )

        return {
            "performance":
            self.report.performance,
            "benchmark":
            self.report.benchmark,
            "drawdown":
            self.report.drawdown,
            "turnover":
            self.report.turnover,
            "attribution":
            self.report.attribution,
            "metadata":
            self.report.metadata,
        }

    def reset(
        self,
    ) -> None:
        """
        Reset reporting engine.
        """

        self.report = None

        logger.info(
            "ReportEngine reset."
        )