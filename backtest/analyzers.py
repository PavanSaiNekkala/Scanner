"""
analyzers.py
============

Institutional Analytics Orchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .attribution import AttributionEngine
from .benchmark import BenchmarkEngine
from .drawdown import DrawdownEngine
from .performance import PerformanceEngine
from .turnover import TurnoverEngine


# ==========================================================
# Configuration
# ==========================================================


@dataclass(slots=True)
class AnalyzerConfig:
    """
    Analyzer configuration.
    """

    annualization_factor: int = 252
    risk_free_rate: float = 0.0
    confidence_level: float = 0.95


# ==========================================================
# Analytics Engine
# ==========================================================


class AnalyzerEngine:
    """
    Institutional analytics orchestrator.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
    ) -> None:

        self.config = config or AnalyzerConfig()

        self.performance = PerformanceEngine()

        self.drawdown = DrawdownEngine()

        self.benchmark = BenchmarkEngine()

        self.turnover = TurnoverEngine()

        self.attribution = AttributionEngine()

        self.results: dict[str, Any] = {}


# ==========================================================
# Performance
# ==========================================================

    def performance_report(
        self,
        returns: pd.Series,
    ) -> dict[str, Any]:
        """
        Compute performance metrics.
        """

        report = self.performance.summary(
            returns=returns,
            annualization_factor=self.config.annualization_factor,
            risk_free_rate=self.config.risk_free_rate,
        )

        self.results["performance"] = report

        return report


# ==========================================================
# Drawdown
# ==========================================================

    def drawdown_report(
        self,
        equity_curve: pd.Series,
    ) -> dict[str, Any]:
        """
        Compute drawdown metrics.
        """

        report = self.drawdown.summary(
            equity_curve,
        )

        self.results["drawdown"] = report

        return report


# ==========================================================
# Benchmark
# ==========================================================

    def benchmark_report(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> dict[str, Any]:
        """
        Compute benchmark analytics.
        """

        report = self.benchmark.summary(
            portfolio_returns,
            benchmark_returns,
        )

        self.results["benchmark"] = report

        return report

# ==========================================================
# Turnover
# ==========================================================

    def turnover_report(
        self,
        trades: pd.DataFrame,
    ) -> dict[str, Any]:
        """
        Compute turnover analytics.
        """

        report = self.turnover.summary(
            trades,
        )

        self.results["turnover"] = report

        return report


# ==========================================================
# Attribution
# ==========================================================

    def attribution_report(
        self,
        positions: pd.DataFrame,
        returns: pd.Series,
    ) -> dict[str, Any]:
        """
        Compute attribution analytics.
        """

        report = self.attribution.summary(
            positions=positions,
            returns=returns,
        )

        self.results["attribution"] = report

        return report


# ==========================================================
# Complete Analytics
# ==========================================================

    def full_report(
        self,
        *,
        returns: pd.Series,
        equity_curve: pd.Series,
        benchmark_returns: pd.Series | None = None,
        trades: pd.DataFrame | None = None,
        positions: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """
        Run the complete analytics pipeline.
        """

        self.results.clear()

        self.performance_report(
            returns,
        )

        self.drawdown_report(
            equity_curve,
        )

        if benchmark_returns is not None:

            self.benchmark_report(
                returns,
                benchmark_returns,
            )

        if trades is not None:

            self.turnover_report(
                trades,
            )

        if positions is not None:

            self.attribution_report(
                positions,
                returns,
            )

        return self.results

# ==========================================================
# Export
# ==========================================================

    def export(
        self,
    ) -> dict[str, Any]:
        """
        Return all analytics.
        """

        return dict(
            self.results,
        )


# ==========================================================
# Utilities
# ==========================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Analytics summary.
        """

        return self.export()

    def reset(
        self,
    ) -> None:
        """
        Reset cached analytics.
        """

        self.results.clear()

    def __repr__(
        self,
    ) -> str:
        """
        String representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"reports={len(self.results)})"
        )


__all__ = [
    "AnalyzerConfig",
    "AnalyzerEngine",
]