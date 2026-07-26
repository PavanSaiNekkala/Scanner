"""
events.py
=========

Institutional Event Models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

import pandas as pd

# ==========================================================
# Event Types
# ==========================================================


class EventType(str, Enum):
    """
    Supported event types.
    """

    MARKET = "MARKET"

    SIGNAL = "SIGNAL"

    ORDER = "ORDER"

    FILL = "FILL"

    POSITION = "POSITION"

    PORTFOLIO = "PORTFOLIO"

    RISK = "RISK"

    REBALANCE = "REBALANCE"

    REPORT = "REPORT"

    SYSTEM = "SYSTEM"


# ==========================================================
# Base Event
# ==========================================================


@dataclass(slots=True)
class Event:
    """
    Base event.
    """

    event_type: EventType

    timestamp: pd.Timestamp = field(
        default_factory=pd.Timestamp.utcnow,
    )

    event_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    metadata: dict = field(
        default_factory=dict,
    )

@dataclass(slots=True)
class MarketEvent(Event):
    """
    Market data update.
    """

    symbol: str = ""

    open: float = 0.0

    high: float = 0.0

    low: float = 0.0

    close: float = 0.0

    volume: float = 0.0

    def __post_init__(
        self,
    ) -> None:

        self.event_type = EventType.MARKET

@dataclass(slots=True)
class SignalEvent(Event):
    """
    Strategy signal.
    """

    symbol: str = ""

    signal: str = ""

    strength: float = 1.0

    strategy: str = ""

    confidence: float = 1.0

    def __post_init__(
        self,
    ) -> None:

        self.event_type = EventType.SIGNAL

@dataclass(slots=True)
class OrderEvent(Event):
    """
    Order submission.
    """

    order_id: str = ""

    symbol: str = ""

    side: str = ""

    quantity: float = 0.0

    order_type: str = "MARKET"

    price: float | None = None

    def __post_init__(
        self,
    ) -> None:

        self.event_type = EventType.ORDER

@dataclass(slots=True)
class FillEvent(Event):
    """
    Trade execution.
    """

    order_id: str = ""

    symbol: str = ""

    quantity: float = 0.0

    fill_price: float = 0.0

    commission: float = 0.0

    slippage: float = 0.0

    def __post_init__(
        self,
    ) -> None:

        self.event_type = EventType.FILL


# ==========================================================
# Position Event
# ==========================================================


@dataclass(slots=True)
class PositionEvent(Event):
    """
    Position update event.
    """

    symbol: str = ""

    quantity: float = 0.0

    average_price: float = 0.0

    market_value: float = 0.0

    unrealized_pnl: float = 0.0

    realized_pnl: float = 0.0

    def __post_init__(
        self,
    ) -> None:

        self.event_type = (
            EventType.POSITION
        )


# ==========================================================
# Portfolio Event
# ==========================================================


@dataclass(slots=True)
class PortfolioEvent(Event):
    """
    Portfolio update.
    """

    equity: float = 0.0

    cash: float = 0.0

    invested: float = 0.0

    leverage: float = 0.0

    exposure: float = 0.0

    positions: int = 0

    def __post_init__(
        self,
    ) -> None:

        self.event_type = (
            EventType.PORTFOLIO
        )


# ==========================================================
# Risk Event
# ==========================================================


@dataclass(slots=True)
class RiskEvent(Event):
    """
    Risk monitoring event.
    """

    var: float = 0.0

    cvar: float = 0.0

    drawdown: float = 0.0

    volatility: float = 0.0

    beta: float = 0.0

    alert: str = ""

    def __post_init__(
        self,
    ) -> None:

        self.event_type = (
            EventType.RISK
        )


# ==========================================================
# Rebalance Event
# ==========================================================


@dataclass(slots=True)
class RebalanceEvent(Event):
    """
    Portfolio rebalance event.
    """

    turnover: float = 0.0

    trades: int = 0

    target_positions: int = 0

    reason: str = ""

    def __post_init__(
        self,
    ) -> None:

        self.event_type = (
            EventType.REBALANCE
        )


# ==========================================================
# Report Event
# ==========================================================


@dataclass(slots=True)
class ReportEvent(Event):
    """
    Report generation event.
    """

    report_name: str = ""

    report_type: str = ""

    location: str = ""

    success: bool = True

    def __post_init__(
        self,
    ) -> None:

        self.event_type = (
            EventType.REPORT
        )


# ==========================================================
# System Event
# ==========================================================


@dataclass(slots=True)
class SystemEvent(Event):
    """
    Internal framework event.
    """

    level: str = "INFO"

    component: str = ""

    message: str = ""

    def __post_init__(
        self,
    ) -> None:

        self.event_type = (
            EventType.SYSTEM
        )

# ==========================================================
# Event Queue
# ==========================================================

from collections import deque
from typing import Iterator


class EventQueue:
    """
    FIFO event queue.

    Acts as the communication backbone between
    strategy, broker, portfolio, risk and reporting
    components.
    """

    def __init__(
        self,
    ) -> None:

        self._queue: deque[Event] = deque()

    def put(
        self,
        event: Event,
    ) -> None:
        """
        Add an event.
        """

        self._queue.append(
            event,
        )

    def get(
        self,
    ) -> Event:
        """
        Pop the next event.
        """

        if self.empty():

            raise IndexError(
                "Event queue is empty."
            )

        return self._queue.popleft()

    def peek(
        self,
    ) -> Event | None:
        """
        Peek at the next event.
        """

        if self.empty():

            return None

        return self._queue[0]

    def empty(
        self,
    ) -> bool:
        """
        Return True if queue is empty.
        """

        return len(
            self._queue
        ) == 0

    def size(
        self,
    ) -> int:
        """
        Queue size.
        """

        return len(
            self._queue
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all events.
        """

        self._queue.clear()

    def extend(
        self,
        events: list[Event],
    ) -> None:
        """
        Add multiple events.
        """

        self._queue.extend(
            events,
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self._queue
        )

    def __bool__(
        self,
    ) -> bool:

        return not self.empty()

    def __iter__(
        self,
    ) -> Iterator[Event]:

        return iter(
            self._queue
        )

__all__ = [
    "EventType",
    "Event",
    "MarketEvent",
    "SignalEvent",
    "OrderEvent",
    "FillEvent",
    "PositionEvent",
    "PortfolioEvent",
    "RiskEvent",
    "RebalanceEvent",
    "ReportEvent",
    "SystemEvent",
    "EventQueue",
]