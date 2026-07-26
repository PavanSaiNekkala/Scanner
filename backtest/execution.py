"""
execution.py
============

Institutional Execution Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .enums import ExecutionStatus
from .orders import Order


# ==========================================================
# Configuration
# ==========================================================


@dataclass(slots=True)
class ExecutionConfig:
    """
    Execution configuration.
    """

    participation_rate: float = 0.10
    max_order_size: int = 1_000_000
    allow_partial_fills: bool = True
    lot_size: int = 1
    latency_ms: int = 50


# ==========================================================
# Base Execution Algorithm
# ==========================================================


class ExecutionAlgorithm:
    """
    Base execution algorithm.
    """

    def execute(
        self,
        order: Order,
        market: pd.Series,
    ) -> dict[str, Any]:
        """
        Execute an order.
        """

        raise NotImplementedError

# ==========================================================
# Market Execution
# ==========================================================


class MarketExecution(
    ExecutionAlgorithm,
):
    """
    Execute immediately at market price.
    """

    def execute(
        self,
        order: Order,
        market: pd.Series,
    ) -> dict[str, Any]:

        return {
            "price": market["Close"],
            "quantity": order.quantity,
            "status": ExecutionStatus.FILLED,
        }

# ==========================================================
# Limit Execution
# ==========================================================


class LimitExecution(
    ExecutionAlgorithm,
):
    """
    Simple limit-order simulation.
    """

    def execute(
        self,
        order: Order,
        market: pd.Series,
    ) -> dict[str, Any]:

        filled = False

        price = market["Close"]

        if (
            order.limit_price is not None
            and price <= order.limit_price
        ):
            filled = True

        return {
            "price": price,
            "quantity": (
                order.quantity if filled else 0
            ),
            "status": (
                ExecutionStatus.FILLED
                if filled
                else ExecutionStatus.PENDING
            ),
        }

# ==========================================================
# Execution Engine
# ==========================================================


class ExecutionEngine:
    """
    Institutional execution engine.
    """

    def __init__(
        self,
        config: ExecutionConfig | None = None,
    ) -> None:

        self.config = config or ExecutionConfig()

        self.algorithms = {
            "market": MarketExecution(),
            "limit": LimitExecution(),
        }

        self.history: list[dict[str, Any]] = []


# ==========================================================
# TWAP Execution
# ==========================================================


class TWAPExecution(
    ExecutionAlgorithm,
):
    """
    Time-Weighted Average Price execution.
    """

    def execute(
        self,
        order: Order,
        market: pd.DataFrame,
    ) -> dict[str, Any]:

        average_price = float(
            market["Close"].mean()
        )

        return {
            "price": average_price,
            "quantity": order.quantity,
            "status": ExecutionStatus.FILLED,
            "algorithm": "TWAP",
        }


# ==========================================================
# VWAP Execution
# ==========================================================


class VWAPExecution(
    ExecutionAlgorithm,
):
    """
    Volume-Weighted Average Price execution.
    """

    def execute(
        self,
        order: Order,
        market: pd.DataFrame,
    ) -> dict[str, Any]:

        if "Volume" not in market.columns:

            raise ValueError(
                "Market data requires Volume column."
            )

        vwap = (
            (
                market["Close"]
                * market["Volume"]
            ).sum()
            / market["Volume"].sum()
        )

        return {
            "price": float(vwap),
            "quantity": order.quantity,
            "status": ExecutionStatus.FILLED,
            "algorithm": "VWAP",
        }


# ==========================================================
# POV Execution
# ==========================================================


class POVExecution(
    ExecutionAlgorithm,
):
    """
    Percentage-of-Volume execution.
    """

    def __init__(
        self,
        participation_rate: float = 0.10,
    ) -> None:

        self.participation_rate = participation_rate

    def execute(
        self,
        order: Order,
        market: pd.DataFrame,
    ) -> dict[str, Any]:

        available_volume = int(
            market["Volume"].sum()
            * self.participation_rate
        )

        executed_quantity = min(
            order.quantity,
            available_volume,
        )

        status = (
            ExecutionStatus.FILLED
            if executed_quantity == order.quantity
            else ExecutionStatus.PARTIALLY_FILLED
        )

        return {
            "price": float(
                market["Close"].iloc[-1]
            ),
            "quantity": executed_quantity,
            "status": status,
            "algorithm": "POV",
        }


# ==========================================================
# Iceberg Execution
# ==========================================================


class IcebergExecution(
    ExecutionAlgorithm,
):
    """
    Iceberg order execution.
    """

    def __init__(
        self,
        display_quantity: int = 1_000,
    ) -> None:

        self.display_quantity = display_quantity

    def execute(
        self,
        order: Order,
        market: pd.DataFrame,
    ) -> dict[str, Any]:

        executed_quantity = min(
            order.quantity,
            self.display_quantity,
        )

        status = (
            ExecutionStatus.FILLED
            if executed_quantity == order.quantity
            else ExecutionStatus.PARTIALLY_FILLED
        )

        return {
            "price": float(
                market["Close"].iloc[-1]
            ),
            "quantity": executed_quantity,
            "remaining_quantity": (
                order.quantity
                - executed_quantity
            ),
            "status": status,
            "algorithm": "ICEBERG",
        }


# ==========================================================
# Execution Engine
# ==========================================================


    def execute(
        self,
        order: Order,
        market: pd.DataFrame | pd.Series,
        algorithm: str = "market",
    ) -> dict[str, Any]:
        """
        Execute an order using the selected algorithm.
        """

        algorithm = algorithm.lower()

        if algorithm not in self.algorithms:

            raise ValueError(
                f"Unknown execution algorithm: {algorithm}"
            )

        result = self.algorithms[
            algorithm
        ].execute(
            order,
            market,
        )

        self.history.append(
            {
                "order_id": order.order_id,
                "symbol": order.symbol,
                "algorithm": algorithm,
                **result,
            }
        )

        return result


# ==========================================================
# Algorithm Management
# ==========================================================


    def register_algorithm(
        self,
        name: str,
        algorithm: ExecutionAlgorithm,
    ) -> None:
        """
        Register a custom execution algorithm.
        """

        self.algorithms[
            name.lower()
        ] = algorithm

    def unregister_algorithm(
        self,
        name: str,
    ) -> None:
        """
        Remove an execution algorithm.
        """

        self.algorithms.pop(
            name.lower(),
            None,
        )

    def available_algorithms(
        self,
    ) -> list[str]:
        """
        Return registered execution algorithms.
        """

        return sorted(
            self.algorithms.keys(),
        )


# ==========================================================
# Reporting
# ==========================================================


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Execution summary.
        """

        return {
            "executions": len(
                self.history,
            ),
            "algorithms": self.available_algorithms(),
            "history": self.history,
        }


# ==========================================================
# Utilities
# ==========================================================


    def reset(
        self,
    ) -> None:
        """
        Reset execution history.
        """

        self.history.clear()

    def __repr__(
        self,
    ) -> str:
        """
        String representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"executions={len(self.history)}, "
            f"algorithms={len(self.algorithms)})"
        )


__all__ = [
    "ExecutionConfig",
    "ExecutionAlgorithm",
    "MarketExecution",
    "LimitExecution",
    "TWAPExecution",
    "VWAPExecution",
    "POVExecution",
    "IcebergExecution",
    "ExecutionEngine",
]