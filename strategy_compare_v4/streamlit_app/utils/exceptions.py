"""
exceptions.py
=============

Custom exceptions.
"""


class StrategyPlatformError(Exception):
    """Base exception."""


class ReportNotFoundError(StrategyPlatformError):
    """Workbook not found."""


class SheetNotFoundError(StrategyPlatformError):
    """Worksheet not found."""


class MissingColumnError(StrategyPlatformError):
    """Required columns missing."""


class EmptyDataFrameError(StrategyPlatformError):
    """DataFrame is empty."""


class InvalidConfigurationError(StrategyPlatformError):
    """Configuration error."""
