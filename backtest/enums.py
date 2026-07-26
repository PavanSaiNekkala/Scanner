"""
enums.py
========

Institutional Backtesting Enumerations.
"""

from __future__ import annotations

from enum import Enum


# ==========================================================
# Order
# ==========================================================


class OrderSide(str, Enum):
    """
    Order side.
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

    MARKET_ON_OPEN = "MARKET_ON_OPEN"

    MARKET_ON_CLOSE = "MARKET_ON_CLOSE"


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
# Positions
# ==========================================================


class PositionSide(str, Enum):
    """
    Position direction.
    """

    LONG = "LONG"

    SHORT = "SHORT"

    FLAT = "FLAT"


# ==========================================================
# Trade
# ==========================================================


class TradeDirection(str, Enum):
    """
    Trade direction.
    """

    ENTRY = "ENTRY"

    EXIT = "EXIT"

    REVERSAL = "REVERSAL"


# ==========================================================
# Portfolio
# ==========================================================


class PortfolioStatus(str, Enum):
    """
    Portfolio status.
    """

    ACTIVE = "ACTIVE"

    CLOSED = "CLOSED"

    LIQUIDATED = "LIQUIDATED"


# ==========================================================
# Execution
# ==========================================================


class ExecutionModel(str, Enum):
    """
    Execution model.
    """

    MARKET = "MARKET"

    VWAP = "VWAP"

    TWAP = "TWAP"

    CLOSE = "CLOSE"

    OPEN = "OPEN"


class ExecutionStatus(str, Enum):
    """
    Execution status.
    """

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"


# ==========================================================
# Backtest
# ==========================================================


class BacktestStatus(str, Enum):
    """
    Backtest lifecycle.
    """

    CREATED = "CREATED"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"


# ==========================================================
# Benchmark
# ==========================================================


class BenchmarkType(str, Enum):
    """
    Benchmark type.
    """

    INDEX = "INDEX"

    ETF = "ETF"

    CUSTOM = "CUSTOM"


# ==========================================================
# Frequency
# ==========================================================


class Frequency(str, Enum):
    """
    Rebalancing frequency.
    """

    DAILY = "DAILY"

    WEEKLY = "WEEKLY"

    MONTHLY = "MONTHLY"

    QUARTERLY = "QUARTERLY"

    YEARLY = "YEARLY"

__all__ = [
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "TimeInForce",
    "PositionSide",
    "TradeDirection",
    "PortfolioStatus",
    "ExecutionModel",
    "ExecutionStatus",
    "BacktestStatus",
    "BenchmarkType",
    "Frequency",
]