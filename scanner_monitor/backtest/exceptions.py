"""
exceptions.py
=============

Institutional Backtesting Exceptions.
"""

from __future__ import annotations


# ==========================================================
# Base Exception
# ==========================================================


class BacktestError(Exception):
    """
    Base class for all backtesting exceptions.
    """

    pass


# ==========================================================
# Configuration
# ==========================================================


class ConfigurationError(BacktestError):
    """
    Raised when configuration is invalid.
    """

    pass


class ValidationError(BacktestError):
    """
    Raised when validation fails.
    """

    pass


# ==========================================================
# Data
# ==========================================================


class DataError(BacktestError):
    """
    Raised when market data is invalid.
    """

    pass


class MissingDataError(DataError):
    """
    Raised when required data is missing.
    """

    pass


class InvalidPriceError(DataError):
    """
    Raised when price data is invalid.
    """

    pass


class InvalidSymbolError(DataError):
    """
    Raised when an unknown symbol is encountered.
    """

    pass


# ==========================================================
# Orders
# ==========================================================


class OrderError(BacktestError):
    """
    Base order exception.
    """

    pass


class InvalidOrderError(OrderError):
    """
    Raised when an order is invalid.
    """

    pass


class OrderRejectedError(OrderError):
    """
    Raised when an order is rejected.
    """

    pass


class OrderExpiredError(OrderError):
    """
    Raised when an order expires.
    """

    pass


class OrderCancelledError(OrderError):
    """
    Raised when an order is cancelled.
    """

    pass


class DuplicateOrderError(OrderError):
    """
    Raised when a duplicate order ID exists.
    """

    pass


# ==========================================================
# Broker
# ==========================================================


class BrokerError(BacktestError):
    """
    Base broker exception.
    """

    pass


class InsufficientCashError(BrokerError):
    """
    Raised when available cash is insufficient.
    """

    pass


class MarginError(BrokerError):
    """
    Raised when margin requirements fail.
    """

    pass


class PositionLimitError(BrokerError):
    """
    Raised when position limits are exceeded.
    """

    pass


class LeverageLimitError(BrokerError):
    """
    Raised when leverage exceeds limits.
    """

    pass


# ==========================================================
# Portfolio
# ==========================================================


class PortfolioError(BacktestError):
    """
    Base portfolio exception.
    """

    pass


class PositionNotFoundError(PortfolioError):
    """
    Raised when a position does not exist.
    """

    pass


class DuplicatePositionError(PortfolioError):
    """
    Raised when attempting to create a duplicate position.
    """

    pass


class PortfolioConstraintError(PortfolioError):
    """
    Raised when a portfolio constraint is violated.
    """

    pass


# ==========================================================
# Performance
# ==========================================================


class PerformanceError(BacktestError):
    """
    Performance analytics error.
    """

    pass


class BenchmarkError(PerformanceError):
    """
    Benchmark calculation error.
    """

    pass


class AttributionError(PerformanceError):
    """
    Attribution calculation error.
    """

    pass


class DrawdownError(PerformanceError):
    """
    Drawdown calculation error.
    """

    pass


# ==========================================================
# Reports
# ==========================================================


class ReportError(BacktestError):
    """
    Report generation error.
    """

    pass


class ExportError(ReportError):
    """
    Report export error.
    """

    pass


# ==========================================================
# Simulator
# ==========================================================


class SimulationError(BacktestError):
    """
    Raised during simulation failures.
    """

    pass


class EngineError(BacktestError):
    """
    Raised when the engine encounters an unrecoverable error.
    """

    pass


__all__ = [
    "BacktestError",
    "ConfigurationError",
    "ValidationError",
    "DataError",
    "MissingDataError",
    "InvalidPriceError",
    "InvalidSymbolError",
    "OrderError",
    "InvalidOrderError",
    "OrderRejectedError",
    "OrderExpiredError",
    "OrderCancelledError",
    "DuplicateOrderError",
    "BrokerError",
    "InsufficientCashError",
    "MarginError",
    "PositionLimitError",
    "LeverageLimitError",
    "PortfolioError",
    "PositionNotFoundError",
    "DuplicatePositionError",
    "PortfolioConstraintError",
    "PerformanceError",
    "BenchmarkError",
    "AttributionError",
    "DrawdownError",
    "ReportError",
    "ExportError",
    "SimulationError",
    "EngineError",
]