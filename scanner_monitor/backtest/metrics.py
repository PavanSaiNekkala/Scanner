"""
metrics.py
==========

Institutional Portfolio Metrics Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .utils import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
    calmar_ratio,
    beta,
    alpha,
)


# ==========================================================
# Configuration
# ==========================================================


@dataclass(slots=True)
class MetricsConfig:
    """
    Metrics configuration.
    """

    annualization_factor: int = 252
    risk_free_rate: float = 0.0


# ==========================================================
# Metrics Engine
# ==========================================================


class MetricsEngine:
    """
    Institutional metrics engine.
    """

    def __init__(
        self,
        config: MetricsConfig | None = None,
    ) -> None:

        self.config = config or MetricsConfig()

        self.metrics: dict[str, Any] = {}

# ==========================================================
# Return Metrics
# ==========================================================

    def return_metrics(
        self,
        returns: pd.Series,
    ) -> dict[str, float]:
        """
        Compute return metrics.
        """

        report = {
            "Total Return": float(
                (1 + returns).prod() - 1
            ),
            "Annual Return": annualized_return(
                returns,
                self.config.annualization_factor,
            ),
            "Annual Volatility": annualized_volatility(
                returns,
                self.config.annualization_factor,
            ),
        }

        self.metrics["returns"] = report

        return report

# ==========================================================
# Risk Metrics
# ==========================================================

    def risk_metrics(
        self,
        returns: pd.Series,
        equity: pd.Series,
    ) -> dict[str, float]:
        """
        Compute risk metrics.
        """

        report = {
            "Sharpe": sharpe_ratio(
                returns,
                self.config.risk_free_rate,
                self.config.annualization_factor,
            ),
            "Sortino": sortino_ratio(
                returns,
                self.config.risk_free_rate,
                self.config.annualization_factor,
            ),
            "Calmar": calmar_ratio(
                returns,
                equity,
                self.config.annualization_factor,
            ),
            "Max Drawdown": max_drawdown(
                equity,
            ),
        }

        self.metrics["risk"] = report

        return report

# ==========================================================
# Benchmark Metrics
# ==========================================================

    def benchmark_metrics(
        self,
        portfolio: pd.Series,
        benchmark: pd.Series,
    ) -> dict[str, float]:
        """
        Benchmark comparison metrics.
        """

        report = {
            "Beta": beta(
                portfolio,
                benchmark,
            ),
            "Alpha": alpha(
                portfolio,
                benchmark,
                self.config.risk_free_rate,
                self.config.annualization_factor,
            ),
            "Correlation": float(
                portfolio.corr(
                    benchmark,
                )
            ),
        }

        self.metrics["benchmark"] = report

        return report


# ==========================================================
# Trade Metrics
# ==========================================================

    def trade_metrics(
        self,
        trades: pd.DataFrame,
        pnl_column: str = "PnL",
        win_column: str | None = None,
    ) -> dict[str, float]:
        """
        Compute trade statistics.
        """

        if trades.empty:

            report = {
                "Trades": 0,
                "Winning Trades": 0,
                "Losing Trades": 0,
                "Win Rate": 0.0,
                "Profit Factor": 0.0,
                "Expectancy": 0.0,
            }

            self.metrics["trades"] = report

            return report

        pnl = trades[pnl_column]

        wins = pnl[pnl > 0]

        losses = pnl[pnl < 0]

        total_trades = len(pnl)

        winning_trades = len(wins)

        losing_trades = len(losses)

        gross_profit = float(
            wins.sum()
        )

        gross_loss = abs(
            float(
                losses.sum()
            )
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else np.inf
        )

        expectancy = float(
            pnl.mean()
        )

        report = {
            "Trades": total_trades,
            "Winning Trades": winning_trades,
            "Losing Trades": losing_trades,
            "Win Rate": (
                winning_trades
                / total_trades
            )
            if total_trades
            else 0.0,
            "Gross Profit": gross_profit,
            "Gross Loss": gross_loss,
            "Profit Factor": profit_factor,
            "Expectancy": expectancy,
        }

        self.metrics["trades"] = report

        return report


# ==========================================================
# Portfolio Metrics
# ==========================================================

    def portfolio_metrics(
        self,
        portfolio: pd.DataFrame,
        weight_column: str = "Weight",
    ) -> dict[str, float]:
        """
        Compute portfolio statistics.
        """

        if portfolio.empty:

            report = {
                "Positions": 0,
                "Gross Exposure": 0.0,
                "Largest Position": 0.0,
                "Average Position": 0.0,
            }

            self.metrics["portfolio"] = report

            return report

        weights = portfolio[
            weight_column
        ]

        report = {
            "Positions": len(
                portfolio,
            ),
            "Gross Exposure": float(
                weights.abs().sum()
            ),
            "Net Exposure": float(
                weights.sum()
            ),
            "Largest Position": float(
                weights.abs().max()
            ),
            "Average Position": float(
                weights.abs().mean()
            ),
        }

        self.metrics["portfolio"] = report

        return report

# ==========================================================
# Rolling Metrics
# ==========================================================

    def rolling_metrics(
        self,
        returns: pd.Series,
        window: int = 252,
    ) -> pd.DataFrame:
        """
        Compute rolling performance metrics.
        """

        rolling_return = (
            (1 + returns)
            .rolling(window)
            .apply(
                np.prod,
                raw=True,
            )
            - 1
        )

        rolling_volatility = (
            returns
            .rolling(window)
            .std()
            * np.sqrt(
                self.config.annualization_factor
            )
        )

        rolling_sharpe = (
            returns
            .rolling(window)
            .mean()
            /
            returns
            .rolling(window)
            .std()
        ) * np.sqrt(
            self.config.annualization_factor
        )

        report = pd.DataFrame(
            {
                "Rolling Return": rolling_return,
                "Rolling Volatility": rolling_volatility,
                "Rolling Sharpe": rolling_sharpe,
            }
        )

        self.metrics["rolling"] = report

        return report


# ==========================================================
# Complete Metrics
# ==========================================================

    def full_report(
        self,
        *,
        returns: pd.Series,
        equity: pd.Series,
        portfolio: pd.DataFrame | None = None,
        trades: pd.DataFrame | None = None,
        benchmark: pd.Series | None = None,
    ) -> dict[str, Any]:
        """
        Compute all available metrics.
        """

        self.metrics.clear()

        self.return_metrics(
            returns,
        )

        self.risk_metrics(
            returns,
            equity,
        )

        self.rolling_metrics(
            returns,
        )

        if benchmark is not None:

            self.benchmark_metrics(
                returns,
                benchmark,
            )

        if trades is not None:

            self.trade_metrics(
                trades,
            )

        if portfolio is not None:

            self.portfolio_metrics(
                portfolio,
            )

        return self.metrics

# ==========================================================
# Reporting
# ==========================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return computed metrics.
        """

        return dict(
            self.metrics,
        )


# ==========================================================
# Utilities
# ==========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset cached metrics.
        """

        self.metrics.clear()

    def __repr__(
        self,
    ) -> str:
        """
        String representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"groups={len(self.metrics)})"
        )


__all__ = [
    "MetricsConfig",
    "MetricsEngine",
]