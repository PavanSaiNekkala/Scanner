"""
risk.py
=======

Institutional Risk Management Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


# ==========================================================
# Configuration
# ==========================================================


@dataclass(slots=True)
class RiskConfig:
    """
    Risk configuration.
    """

    max_position_weight: float = 0.10
    max_sector_weight: float = 0.30
    max_leverage: float = 2.0
    max_drawdown: float = 0.20
    max_turnover: float = 0.50
    confidence_level: float = 0.95

# ==========================================================
# Risk Engine
# ==========================================================


class RiskEngine:
    """
    Institutional portfolio risk engine.
    """

    def __init__(
        self,
        config: RiskConfig | None = None,
    ) -> None:

        self.config = config or RiskConfig()

        self.results: dict[str, Any] = {}


# ==========================================================
# Position Limits
# ==========================================================


    def check_position_limits(
        self,
        portfolio: pd.DataFrame,
        weight_column: str = "Weight",
    ) -> bool:
        """
        Validate position weights.
        """

        if portfolio.empty:
            return True

        maximum = portfolio[
            weight_column
        ].max()

        passed = (
            maximum
            <= self.config.max_position_weight
        )

        self.results[
            "position_limit"
        ] = {
            "passed": passed,
            "maximum": float(maximum),
            "limit": self.config.max_position_weight,
        }

        return passed

# ==========================================================
# Sector Limits
# ==========================================================


    def check_sector_limits(
        self,
        portfolio: pd.DataFrame,
        sector_column: str = "Sector",
        weight_column: str = "Weight",
    ) -> bool:
        """
        Validate sector exposure.
        """

        if portfolio.empty:
            return True

        sector_weights = (
            portfolio
            .groupby(
                sector_column,
            )[weight_column]
            .sum()
        )

        maximum = float(
            sector_weights.max()
        )

        passed = (
            maximum
            <= self.config.max_sector_weight
        )

        self.results[
            "sector_limit"
        ] = {
            "passed": passed,
            "maximum": maximum,
            "limit": self.config.max_sector_weight,
        }

        return passed


# ==========================================================
# Leverage
# ==========================================================


    def check_leverage(
        self,
        gross_exposure: float,
        equity: float,
    ) -> bool:
        """
        Validate portfolio leverage.
        """

        if equity <= 0:

            raise ValueError(
                "Equity must be positive."
            )

        leverage = (
            gross_exposure
            / equity
        )

        passed = (
            leverage
            <= self.config.max_leverage
        )

        self.results[
            "leverage"
        ] = {
            "passed": passed,
            "value": leverage,
            "limit": self.config.max_leverage,
        }

        return passed

# ==========================================================
# Drawdown
# ==========================================================


    def check_drawdown(
        self,
        equity_curve: pd.Series,
    ) -> bool:
        """
        Validate maximum drawdown.
        """

        if equity_curve.empty:
            return True

        running_peak = equity_curve.cummax()

        drawdown = (
            equity_curve
            / running_peak
            - 1.0
        )

        maximum_drawdown = abs(
            float(
                drawdown.min()
            )
        )

        passed = (
            maximum_drawdown
            <= self.config.max_drawdown
        )

        self.results[
            "drawdown"
        ] = {
            "passed": passed,
            "value": maximum_drawdown,
            "limit": self.config.max_drawdown,
        }

        return passed


# ==========================================================
# Turnover
# ==========================================================


    def check_turnover(
        self,
        turnover: float,
    ) -> bool:
        """
        Validate turnover.
        """

        passed = (
            turnover
            <= self.config.max_turnover
        )

        self.results[
            "turnover"
        ] = {
            "passed": passed,
            "value": turnover,
            "limit": self.config.max_turnover,
        }

        return passed


# ==========================================================
# Value at Risk
# ==========================================================


    def value_at_risk(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Historical Value at Risk (VaR).
        """

        confidence = (
            1.0
            - self.config.confidence_level
        )

        var = abs(
            float(
                returns.quantile(
                    confidence,
                )
            )
        )

        self.results[
            "value_at_risk"
        ] = {
            "confidence": self.config.confidence_level,
            "value": var,
        }

        return var


# ==========================================================
# Conditional Value at Risk
# ==========================================================


    def conditional_var(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Historical Conditional Value at Risk (CVaR).
        """

        confidence = (
            1.0
            - self.config.confidence_level
        )

        cutoff = returns.quantile(
            confidence,
        )

        tail = returns[
            returns <= cutoff
        ]

        cvar = abs(
            float(
                tail.mean()
            )
        )

        self.results[
            "conditional_var"
        ] = {
            "confidence": self.config.confidence_level,
            "value": cvar,
        }

        return cvar

# ==========================================================
# Stress Testing
# ==========================================================

    def stress_test(
        self,
        portfolio: pd.DataFrame,
        shock: float = -0.10,
        value_column: str = "MarketValue",
    ) -> dict[str, float]:
        """
        Apply a simple stress shock to the portfolio.
        """

        if portfolio.empty:

            return {
                "original_value": 0.0,
                "stressed_value": 0.0,
                "loss": 0.0,
            }

        original_value = float(
            portfolio[value_column].sum()
        )

        stressed_value = (
            original_value
            * (1.0 + shock)
        )

        loss = (
            original_value
            - stressed_value
        )

        result = {
            "original_value": original_value,
            "stressed_value": stressed_value,
            "loss": loss,
            "shock": shock,
        }

        self.results["stress_test"] = result

        return result


# ==========================================================
# Exposure Summary
# ==========================================================

    def exposure_summary(
        self,
        portfolio: pd.DataFrame,
        weight_column: str = "Weight",
    ) -> dict[str, float]:
        """
        Portfolio exposure summary.
        """

        if portfolio.empty:

            summary = {
                "positions": 0,
                "gross_exposure": 0.0,
                "largest_position": 0.0,
            }

            self.results["exposure"] = summary

            return summary

        gross = float(
            portfolio[weight_column]
            .abs()
            .sum()
        )

        largest = float(
            portfolio[weight_column]
            .abs()
            .max()
        )

        summary = {
            "positions": len(portfolio),
            "gross_exposure": gross,
            "largest_position": largest,
        }

        self.results["exposure"] = summary

        return summary


# ==========================================================
# Portfolio Validation
# ==========================================================

    def validate(
        self,
        portfolio: pd.DataFrame,
        *,
        equity_curve: pd.Series | None = None,
        gross_exposure: float | None = None,
        equity: float | None = None,
        turnover: float | None = None,
    ) -> bool:
        """
        Run all configured portfolio risk checks.
        """

        passed = True

        passed &= self.check_position_limits(
            portfolio,
        )

        passed &= self.check_sector_limits(
            portfolio,
        )

        if (
            gross_exposure is not None
            and equity is not None
        ):
            passed &= self.check_leverage(
                gross_exposure,
                equity,
            )

        if equity_curve is not None:
            passed &= self.check_drawdown(
                equity_curve,
            )

        if turnover is not None:
            passed &= self.check_turnover(
                turnover,
            )

        return bool(
            passed,
        )

# ==========================================================
# Reporting
# ==========================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Risk summary.
        """

        return dict(
            self.results,
        )


# ==========================================================
# Utilities
# ==========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset risk results.
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
            f"checks={len(self.results)})"
        )


__all__ = [
    "RiskConfig",
    "RiskEngine",
]