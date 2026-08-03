"""
core/config.py
==============

Central configuration for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

import os
from pathlib import Path

# =============================================================================
# Project
# =============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# Directories
# =============================================================================

DATA_DIR = ROOT_DIR / "data"

REPORTS_DIR = ROOT_DIR / "reports"

LATEST_REPORTS_DIR = REPORTS_DIR / "latest"

HISTORY_REPORTS_DIR = REPORTS_DIR / "history"

EXPORTS_DIR = ROOT_DIR / "exports"

BACKTESTS_DIR = ROOT_DIR / "backtests"

CACHE_DIR = ROOT_DIR / ".cache"

LOGS_DIR = ROOT_DIR / "logs"

TEMP_DIR = ROOT_DIR / "temp"

ASSETS_DIR = ROOT_DIR / "assets"

PAGES_DIR = ROOT_DIR / "pages"

UI_DIR = ROOT_DIR / "ui"

SERVICES_DIR = ROOT_DIR / "services"

# =============================================================================
# Application
# =============================================================================

APP_NAME = "Scanner Monitor"

APP_VERSION = "1.0.0"

APP_AUTHOR = "Pavan Sai"

APP_DESCRIPTION = (
    "Institutional Stock Scanner "
    "Monitoring Dashboard"
)

DEFAULT_LAYOUT = "wide"

DEFAULT_PAGE_ICON = "📈"

# =============================================================================
# Dashboard
# =============================================================================

REFRESH_INTERVAL_SECONDS = 60

DEFAULT_TABLE_HEIGHT = 500

DEFAULT_CHART_HEIGHT = 450

DEFAULT_PAGE_SIZE = 25

MAX_DOWNLOAD_ROWS = 1_000_000

# =============================================================================
# Cache
# =============================================================================

ENABLE_CACHE = True

CACHE_TTL = 300

# =============================================================================
# Environment
# =============================================================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development",
)

DEBUG = ENVIRONMENT.lower() == "development"

# =============================================================================
# Logging
# =============================================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
)

LOG_FILE = LOGS_DIR / "scanner_monitor.log"

# =============================================================================
# Theme
# =============================================================================

PRIMARY_COLOR = "#2563EB"

SUCCESS_COLOR = "#16A34A"

WARNING_COLOR = "#D97706"

ERROR_COLOR = "#DC2626"

BACKGROUND_COLOR = "#FFFFFF"

# =============================================================================
# Default Dataset Names
# =============================================================================

SCANNER_FILE = "scanner_monitor.csv"

SIGNALS_FILE = "signals.csv"

PORTFOLIO_FILE = "portfolio.csv"

HOLDINGS_FILE = "holdings.csv"

WATCHLIST_FILE = "watchlist.csv"

# =============================================================================
# Latest Reports
# =============================================================================

LATEST_DAILY_MONITOR = "daily_monitor_latest.csv"

LATEST_PORTFOLIO = "portfolio_summary.csv"

LATEST_HOLDINGS = "holdings.csv"

LATEST_RISK = "risk_summary.csv"

LATEST_EXECUTION = "execution_summary.csv"

LATEST_EXCEL_REPORT = "Portfolio_Report.xlsx"

LATEST_JSON_REPORT = "Portfolio_Report.json"

# =============================================================================
# Historical Reports
# =============================================================================

HISTORY_DAILY_MONITOR = "daily_monitor.csv"

HISTORY_PORTFOLIO = "portfolio_history.csv"

HISTORY_PERFORMANCE = "performance_history.csv"

HISTORY_RISK = "risk_history.csv"

HISTORY_EXECUTION = "execution_history.csv"

HISTORY_SIGNALS = "signal_history.csv"

HISTORY_REGIME = "regime_history.csv"

HISTORY_SCAN = "scan_history.csv"

HISTORY_SCAN_METRICS = "scan_history_metrics.csv"

# =============================================================================
# Create Required Directories
# =============================================================================

_REQUIRED_DIRECTORIES = (

    DATA_DIR,

    REPORTS_DIR,

    LATEST_REPORTS_DIR,

    HISTORY_REPORTS_DIR,

    EXPORTS_DIR,

    BACKTESTS_DIR,

    CACHE_DIR,

    LOGS_DIR,

    TEMP_DIR,

    ASSETS_DIR,

)

for directory in _REQUIRED_DIRECTORIES:

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

# =============================================================================
# Helper Functions
# =============================================================================


def project_path(*parts: str) -> Path:
    return ROOT_DIR.joinpath(*parts)


def data_path(filename: str) -> Path:
    return DATA_DIR / filename


def reports_path(filename: str) -> Path:
    return REPORTS_DIR / filename


def latest_report_path(filename: str) -> Path:
    return LATEST_REPORTS_DIR / filename


def history_report_path(filename: str) -> Path:
    return HISTORY_REPORTS_DIR / filename


def exports_path(filename: str) -> Path:
    return EXPORTS_DIR / filename

# =============================================================================
# Backward-Compatible Aliases
# =============================================================================

ROOT = ROOT_DIR

DATA = DATA_DIR

REPORTS = REPORTS_DIR

LATEST_REPORTS = LATEST_REPORTS_DIR

HISTORY_REPORTS = HISTORY_REPORTS_DIR

EXPORTS = EXPORTS_DIR

LOGS = LOGS_DIR