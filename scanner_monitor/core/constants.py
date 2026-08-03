"""
scanner_monitor.core.constants
==============================

Application-wide constants for the Institutional Scanner Monitor.

This module centralizes immutable values used across the application,
including recommendation signals, formatting, colors, thresholds,
portfolio defaults, and application metadata.

All existing constant names are preserved for backward compatibility.
"""

from __future__ import annotations

__all__ = [
    # Recommendation Signals
    "SIGNALS",
    # Theme
    "DEFAULT_THEME",
    # Date Formats
    "DATE_FORMAT",
    "DATETIME_FORMAT",
    # Number Formatting
    "PERCENT_COLUMNS",
    "CURRENCY_COLUMNS",
    "INTEGER_COLUMNS",
    # Colors
    "PRIMARY_COLOR",
    "SECONDARY_COLOR",
    "SUCCESS_COLOR",
    "WARNING_COLOR",
    "ERROR_COLOR",
    "INFO_COLOR",
    "BUY_COLOR",
    "WATCH_COLOR",
    "SELL_COLOR",
    # Risk Thresholds
    "LOW_RISK",
    "MEDIUM_RISK",
    "HIGH_RISK",
    # Dashboard Ratings
    "EXCELLENT",
    "GOOD",
    "AVERAGE",
    "POOR",
    # Tables
    "DEFAULT_PAGE_SIZE",
    "MAX_PREVIEW_ROWS",
    # File Types
    "SUPPORTED_DOWNLOADS",
    # Portfolio Defaults
    "DEFAULT_CASH",
    "DEFAULT_BENCHMARK",
    "DEFAULT_CURRENCY",
    # Application
    "APP_NAME",
    "APP_VERSION",
]

# =============================================================================
# Recommendation Signals
# =============================================================================

SIGNALS: tuple[str, ...] = (
    "STRONG BUY",
    "BUY",
    "WATCH",
    "AVOID",
    "SELL",
)

# =============================================================================
# Theme
# =============================================================================

DEFAULT_THEME: str = "light"

# =============================================================================
# Date Formats
# =============================================================================

DATE_FORMAT: str = "%d %b %Y"

DATETIME_FORMAT: str = "%d %b %Y %H:%M:%S"

# =============================================================================
# Number Formatting
# =============================================================================

PERCENT_COLUMNS: tuple[str, ...] = (
    "Return",
    "Daily Return",
    "Monthly Return",
    "Annual Return",
    "Weight",
    "Portfolio Weight",
    "Target",
    "Exposure",
    "Drawdown",
    "Risk",
    "Volatility",
)

CURRENCY_COLUMNS: tuple[str, ...] = (
    "Market Value",
    "Investment",
    "Portfolio Value",
    "Cash",
    "PnL",
    "Profit",
    "Loss",
)

INTEGER_COLUMNS: tuple[str, ...] = (
    "Quantity",
    "Shares",
    "Trades",
    "Orders",
)

# =============================================================================
# Dashboard Colors
# =============================================================================

PRIMARY_COLOR: str = "#2563EB"

SECONDARY_COLOR: str = "#6366F1"

SUCCESS_COLOR: str = "#16A34A"

WARNING_COLOR: str = "#F59E0B"

ERROR_COLOR: str = "#DC2626"

INFO_COLOR: str = "#0284C7"

# Recommendation Colors
BUY_COLOR: str = SUCCESS_COLOR

WATCH_COLOR: str = WARNING_COLOR

SELL_COLOR: str = ERROR_COLOR

# =============================================================================
# Risk Thresholds
# =============================================================================

LOW_RISK: int = 30

MEDIUM_RISK: int = 60

HIGH_RISK: int = 80

# =============================================================================
# Dashboard Ratings
# =============================================================================

EXCELLENT: int = 90

GOOD: int = 75

AVERAGE: int = 60

POOR: int = 40

# =============================================================================
# Table Defaults
# =============================================================================

DEFAULT_PAGE_SIZE: int = 20

MAX_PREVIEW_ROWS: int = 20

# =============================================================================
# Supported File Types
# =============================================================================

SUPPORTED_DOWNLOADS: tuple[str, ...] = (
    ".csv",
    ".xlsx",
    ".xls",
    ".parquet",
    ".json",
    ".txt",
    ".pdf",
)

# =============================================================================
# Portfolio Defaults
# =============================================================================

DEFAULT_CASH: int = 100_000

DEFAULT_BENCHMARK: str = "NIFTY 50"

DEFAULT_CURRENCY: str = "INR"

# =============================================================================
# Application Information
# =============================================================================

APP_NAME: str = "Institutional Scanner Monitor"

APP_VERSION: str = "1.0.0"