"""
orders.py
=========

Institutional Order Models.

This module defines all order-related models used by the
Institutional Backtesting Framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

import pandas as pd

# ==========================================================
# Enumerations
# ==========================================================


class OrderSide(str, Enum):
    """
    Buy / Sell.
    """

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """
    Supported order types.
    """

    MARKET = "MARKET"

    LIMIT = "LIMIT"

    STOP = "STOP"

    STOP_LIMIT = "STOP_LIMIT"

    MARKET_ON_CLOSE = "MARKET_ON_CLOSE"

    MARKET_ON_OPEN = "MARKET_ON_OPEN"


class OrderStatus(str, Enum):
    """
    Order lifecycle.
    """

    PENDING = "PENDING"

    ACCEPTED = "ACCEPTED"

    PARTIALLY_FILLED = "PARTIALLY_FILLED"

    FILLED = "FILLED"

    CANCELLED = "CANCELLED"

    REJECTED = "REJECTED"

    EXPIRED = "EXPIRED"


class TimeInForce(str, Enum):
    """
    Order validity.
    """

    DAY = "DAY"

    GTC = "GTC"

    IOC = "IOC"

    FOK = "FOK"

    GTD = "GTD"


# ==========================================================
# Fill
# ==========================================================


@dataclass(slots=True)
class Fill:
    """
    Represents one execution fill.
    """

    timestamp: pd.Timestamp

    price: float

    quantity: float

    commission: float = 0.0

    slippage: float = 0.0

    venue: str | None = None

@dataclass(slots=True)
class Order:
    """
    Institutional Order.
    """

    symbol: str

    side: OrderSide

    quantity: float

    order_type: OrderType = OrderType.MARKET

    limit_price: float | None = None

    stop_price: float | None = None

    time_in_force: TimeInForce = TimeInForce.DAY

    strategy: str | None = None

    portfolio: str | None = None

    notes: str | None = None

    created_at: pd.Timestamp = field(
        default_factory=pd.Timestamp.utcnow,
    )

    order_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    status: OrderStatus = OrderStatus.PENDING

    fills: list[Fill] = field(
        default_factory=list,
    )

    cancelled_at: pd.Timestamp | None = None

    rejected_reason: str | None = None

    def filled_quantity(
        self,
    ) -> float:
        """
        Total executed quantity.
        """

        return sum(
            fill.quantity
            for fill in self.fills
        )

    def remaining_quantity(
        self,
    ) -> float:
        """
        Remaining quantity to execute.
        """

        return max(
            self.quantity
            - self.filled_quantity(),
            0.0,
        )

    def average_fill_price(
        self,
    ) -> float | None:
        """
        Volume-weighted average fill price.
        """

        if not self.fills:
            return None

        total_value = sum(
            fill.price * fill.quantity
            for fill in self.fills
        )

        total_qty = self.filled_quantity()

        if total_qty == 0:
            return None

        return total_value / total_qty

    def total_commission(
        self,
    ) -> float:
        """
        Total commission paid.
        """

        return sum(
            fill.commission
            for fill in self.fills
        )

    def total_slippage(
        self,
    ) -> float:
        """
        Total slippage incurred.
        """

        return sum(
            fill.slippage
            for fill in self.fills
        )

    def executed_value(
        self,
    ) -> float:
        """
        Executed notional value.
        """

        return sum(
            fill.price * fill.quantity
            for fill in self.fills
        )

    def add_fill(
        self,
        fill: Fill,
    ) -> None:
        """
        Add an execution fill.
        """

        if self.status in (
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        ):
            raise ValueError(
                "Cannot fill a closed order."
            )

        self.fills.append(
            fill,
        )

        if (
            self.filled_quantity()
            >= self.quantity
        ):
            self.status = (
                OrderStatus.FILLED
            )

        else:
            self.status = (
                OrderStatus.PARTIALLY_FILLED
            )

    def cancel(
        self,
    ) -> None:
        """
        Cancel order.
        """

        if self.status == OrderStatus.FILLED:
            return

        self.status = (
            OrderStatus.CANCELLED
        )

        self.cancelled_at = (
            pd.Timestamp.utcnow()
        )

    def reject(
        self,
        reason: str,
    ) -> None:
        """
        Reject order.
        """

        self.status = (
            OrderStatus.REJECTED
        )

        self.rejected_reason = reason

    def accept(
        self,
    ) -> None:
        """
        Accept order for execution.
        """

        if self.status != OrderStatus.PENDING:
            return

        self.status = (
            OrderStatus.ACCEPTED
        )

    def is_open(
        self,
    ) -> bool:
        """
        Return True if the order can still receive fills.
        """

        return self.status in (
            OrderStatus.PENDING,
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIALLY_FILLED,
        )

    def is_closed(
        self,
    ) -> bool:
        """
        Return True if the order is no longer active.
        """

        return self.status in (
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        )

    def is_filled(
        self,
    ) -> bool:
        """
        Return True if the order is completely filled.
        """

        return (
            self.status
            == OrderStatus.FILLED
        )

    def is_partial(
        self,
    ) -> bool:
        """
        Return True if partially filled.
        """

        return (
            self.status
            == OrderStatus.PARTIALLY_FILLED
        )

    def fill_ratio(
        self,
    ) -> float:
        """
        Percentage of the order that has been filled.
        """

        if self.quantity <= 0:
            return 0.0

        return (
            self.filled_quantity()
            / self.quantity
        )

    def market_value(
        self,
    ) -> float:
        """
        Executed market value.
        """

        return (
            self.executed_value()
        )

    def copy(
        self,
    ) -> "Order":
        """
        Return a deep copy of the order.
        """

        return Order.from_dict(
            self.to_dict(),
        )

    def to_dict(
        self,
    ) -> dict:
        """
        Convert order to dictionary.
        """

        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "order_type": self.order_type.value,
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "time_in_force": self.time_in_force.value,
            "strategy": self.strategy,
            "portfolio": self.portfolio,
            "notes": self.notes,
            "created_at": self.created_at,
            "status": self.status.value,
            "cancelled_at": self.cancelled_at,
            "rejected_reason": self.rejected_reason,
            "fills": [
                {
                    "timestamp": fill.timestamp,
                    "price": fill.price,
                    "quantity": fill.quantity,
                    "commission": fill.commission,
                    "slippage": fill.slippage,
                    "venue": fill.venue,
                }
                for fill in self.fills
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Order":
        """
        Create an Order from a dictionary.
        """

        order = cls(
            symbol=data["symbol"],
            side=OrderSide(
                data["side"],
            ),
            quantity=data["quantity"],
            order_type=OrderType(
                data["order_type"],
            ),
            limit_price=data.get(
                "limit_price",
            ),
            stop_price=data.get(
                "stop_price",
            ),
            time_in_force=TimeInForce(
                data["time_in_force"],
            ),
            strategy=data.get(
                "strategy",
            ),
            portfolio=data.get(
                "portfolio",
            ),
            notes=data.get(
                "notes",
            ),
        )

        order.order_id = data[
            "order_id"
        ]

        order.created_at = data[
            "created_at"
        ]

        order.status = OrderStatus(
            data["status"]
        )

        order.cancelled_at = data.get(
            "cancelled_at",
        )

        order.rejected_reason = data.get(
            "rejected_reason",
        )

        order.fills = [
            Fill(
                timestamp=fill["timestamp"],
                price=fill["price"],
                quantity=fill["quantity"],
                commission=fill["commission"],
                slippage=fill["slippage"],
                venue=fill.get("venue"),
            )
            for fill in data.get(
                "fills",
                [],
            )
        ]

        return order

    def reset(
        self,
    ) -> None:
        """
        Reset the order to its initial state.
        """

        self.status = (
            OrderStatus.PENDING
        )

        self.fills.clear()

        self.cancelled_at = None

        self.rejected_reason = None

    def __repr__(
        self,
    ) -> str:
        """
        String representation.
        """

        return (
            f"Order("
            f"id={self.order_id}, "
            f"symbol='{self.symbol}', "
            f"side={self.side.value}, "
            f"qty={self.quantity}, "
            f"filled={self.filled_quantity()}, "
            f"status={self.status.value})"
        )

    def __hash__(
        self,
    ) -> int:
        """
        Hash using the immutable order ID.
        """

        return hash(
            self.order_id
        )