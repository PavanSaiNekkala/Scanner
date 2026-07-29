"""
core/config.py
==============

Central application configuration for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

import os
from pathlib import Path

# =============================================================================
# Project Root
# =============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# Directories
# =============================================================================

DATA_DIR = ROOT_DIR / "data"

REPORTS_DIR = ROOT_DIR / "reports"

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

CACHE_TTL = 300

ENABLE_CACHE = True

# =============================================================================
# Logging
# =============================================================================

LOG_LEVEL = os.getenv(

    "LOG_LEVEL",

    "INFO",

)

LOG_FILE = LOGS_DIR / "scanner_monitor.log"

# =============================================================================
# Environment
# =============================================================================

ENVIRONMENT = os.getenv(

    "ENVIRONMENT",

    "development",

)

DEBUG = ENVIRONMENT.lower() == "development"

# =============================================================================
# Theme
# =============================================================================

PRIMARY_COLOR = "#2563EB"

SUCCESS_COLOR = "#16A34A"

WARNING_COLOR = "#D97706"

ERROR_COLOR = "#DC2626"

BACKGROUND_COLOR = "#FFFFFF"

# =============================================================================
# Dataset Names
# =============================================================================

SCANNER_FILE = "scanner_monitor.csv"

SIGNALS_FILE = "signals.csv"

PORTFOLIO_FILE = "portfolio.csv"

HOLDINGS_FILE = "holdings.csv"

WATCHLIST_FILE = "watchlist.csv"

# =============================================================================
# Create Required Directories
# =============================================================================

_REQUIRED_DIRECTORIES = (

    DATA_DIR,

    REPORTS_DIR,

    EXPORTS_DIR,

    BACKTESTS_DIR,

    CACHE_DIR,

    LOGS_DIR,

    TEMP_DIR,

    ASSETS_DIR,

)

LATEST_REPORTS_DIR = REPORTS_DIR / "latest"

HISTORY_REPORTS_DIR = REPORTS_DIR / "history"


for directory in _REQUIRED_DIRECTORIES:

    directory.mkdir(

        parents=True,

        exist_ok=True,

    )

# =============================================================================
# Helpers
# =============================================================================


def project_path(

    *parts: str,

) -> Path:
    """
    Return a path relative to the
    project root.
    """

    return ROOT_DIR.joinpath(

        *parts,

    )


def data_path(

    filename: str,

) -> Path:
    """
    Return a file inside the
    data directory.
    """

    return DATA_DIR / filename


def reports_path(

    filename: str,

) -> Path:
    """
    Return a file inside the
    reports directory.
    """

    return REPORTS_DIR / filename


def exports_path(

    filename: str,

) -> Path:
    """
    Return a file inside the
    exports directory.
    """

    return EXPORTS_DIR / filename


"""
Shared project paths.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

REPORTS = ROOT / "reports"

EXPORTS = ROOT / "exports"

LOGS = ROOT / "logs"

# Backward-compatible aliases
DATA_DIR = DATA
REPORTS_DIR = REPORTS
EXPORTS_DIR = EXPORTS
LOGS_DIR = LOGS