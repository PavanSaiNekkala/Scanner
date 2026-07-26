"""
simulator.py
============

Institutional Backtest Simulator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import logging

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SimulatorConfig:
    """
    Backtest simulator configuration.
    """

    initial_cash: float = 100_000.0

    benchmark: str | None = None

    rebalance_frequency: str = "D"

    risk_free_rate: float = 0.0

    commission: float = 0.001

    slippage: float = 0.0005


class BacktestSimulator:
    """
    Institutional backtest simulator.
    """

    def __init__(
        self,
        config: SimulatorConfig,
    ) -> None:
        """
        Initialize simulator.
        """

        self.config = config

        self.results: dict[
            str,
            Any,
        ] = {}

        logger.info(
            "BacktestSimulator initialized."
        )


    def run(
        self,
        data: pd.DataFrame,
        strategy: Any,
    ) -> dict[str, Any]:
        """
        Run a complete backtest.
        """

        signals = self.generate_signals(
            data,
            strategy,
        )

        trades = self.execute(
            data,
            signals,
        )

        portfolio = self.build_portfolio(
            trades,
        )

        self.results = {
            "signals": signals,
            "trades": trades,
            "portfolio": portfolio,
        }

        return self.results

    def generate_signals(
        self,
        data: pd.DataFrame,
        strategy: Any,
    ) -> pd.DataFrame:
        """
        Generate trading signals.
        """

        return strategy.generate(
            data,
        )

    def execute(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Execute generated signals.
        """

        return signals.copy()

    def build_portfolio(
        self,
        trades: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build portfolio from executed trades.
        """

        return trades.copy()

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return simulation summary.
        """

        return self.results

    def analyze(
        self,
        performance_engine: Any,
        portfolio_returns: pd.Series,
    ) -> dict[str, Any]:
        """
        Analyze portfolio performance.
        """

        metrics = (
            performance_engine.evaluate(
                portfolio_returns,
            )
        )

        self.results[
            "performance"
        ] = metrics

        return metrics

    def report(
        self,
        report_engine: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Build the final backtest report.
        """

        report = (
            report_engine.build(
                **kwargs,
            )
        )

        self.results[
            "report"
        ] = report

        return report

    def export(
        self,
        report_engine: Any,
    ) -> dict[str, Any]:
        """
        Export generated reports.
        """

        exported: dict[
            str,
            Any,
        ] = {}

        if (
            report_engine.config.export_csv
        ):
            exported["csv"] = (
                report_engine.export_csv()
            )

        if (
            report_engine.config.export_excel
        ):
            exported["excel"] = (
                report_engine.export_excel()
            )

        if (
            report_engine.config.export_json
        ):
            exported["json"] = (
                report_engine.export_json()
            )

        self.results[
            "exports"
        ] = exported

        return exported

    def reset(
        self,
    ) -> None:
        """
        Reset simulator state.
        """

        self.results.clear()

        logger.info(
            "BacktestSimulator reset."
        )