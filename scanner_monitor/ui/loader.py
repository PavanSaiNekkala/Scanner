"""
ui/loader.py
============

Institutional Report Loader

Centralized loader for all Scanner Monitor reports.

Features
--------
- Automatic report discovery
- Cached loading
- Robust error handling
- Empty DataFrame fallback
- JSON loading
- Excel loading
- CSV loading
- History loading
- Metadata
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR = PROJECT_ROOT / "reports"

LATEST_DIR = REPORTS_DIR / "latest"

HISTORY_DIR = REPORTS_DIR / "history"


# =============================================================================
# Data Container
# =============================================================================


@dataclass(slots=True)
class ReportData:
    """
    Container for all report datasets.
    """

    portfolio_summary: pd.DataFrame

    holdings: pd.DataFrame

    risk_summary: pd.DataFrame

    execution_summary: pd.DataFrame

    daily_monitor: pd.DataFrame

    performance_summary: pd.DataFrame

    orders: pd.DataFrame

    sector_exposure: pd.DataFrame

    risk_violations: pd.DataFrame

    portfolio_history: pd.DataFrame

    performance_history: pd.DataFrame

    risk_history: pd.DataFrame

    execution_history: pd.DataFrame

    regime_history: pd.DataFrame

    signal_history: pd.DataFrame

    daily_monitor_history: pd.DataFrame

    report_json: dict[str, Any]


# =============================================================================
# Helpers
# =============================================================================


def _empty() -> pd.DataFrame:
    """
    Empty dataframe fallback.
    """

    return pd.DataFrame()


def _read_csv(path: Path) -> pd.DataFrame:
    """
    Read CSV safely.
    """

    if not path.exists():

        LOGGER.warning(
            "Missing CSV: %s",
            path.name,
        )

        return _empty()

    try:

        return pd.read_csv(path)

    except Exception:

        LOGGER.exception(
            "Unable to read %s",
            path.name,
        )

        return _empty()


def _read_json(path: Path) -> dict[str, Any]:
    """
    Read JSON safely.
    """

    if not path.exists():

        return {}

    try:

        with open(
            path,
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except Exception:

        LOGGER.exception(
            "Unable to read JSON."
        )

        return {}

# =============================================================================
# Public Loaders
# =============================================================================


@st.cache_data(show_spinner=False)
def load_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Load a CSV file using the shared
    institutional loader.

    Parameters
    ----------
    path : Path
        CSV file path.

    Returns
    -------
    pd.DataFrame
    """

    return _read_csv(path)

@st.cache_data(show_spinner=False)
def load_first_available_csv(
    *paths: Path,
) -> pd.DataFrame:
    """
    Load the first available CSV from a
    sequence of candidate paths.

    Parameters
    ----------
    *paths : Path
        Candidate CSV paths in priority order.

    Returns
    -------
    pd.DataFrame
    """

    for path in paths:

        if path.exists():

            return _read_csv(path)

    LOGGER.warning(
        "No candidate CSV files were found."
    )

    return _empty()


@st.cache_data(show_spinner=False)
def load_excel(
    path: Path,
    sheet_name: str | int | None = 0,
) -> pd.DataFrame:
    """
    Load an Excel workbook safely.

    Parameters
    ----------
    path : Path
        Excel workbook.

    sheet_name : str | int | None
        Worksheet to load.

    Returns
    -------
    pd.DataFrame
    """

    if not path.exists():

        LOGGER.warning(
            "Missing Excel: %s",
            path.name,
        )

        return _empty()

    try:

        return pd.read_excel(
            path,
            sheet_name=sheet_name,
        )

    except Exception:

        LOGGER.exception(
            "Unable to read %s",
            path.name,
        )

        return _empty()


@st.cache_data(show_spinner=False)
def load_json(
    path: Path,
) -> dict[str, Any]:
    """
    Load a JSON document safely.

    Parameters
    ----------
    path : Path
        JSON file.

    Returns
    -------
    dict[str, Any]
    """

    return _read_json(path)


# =============================================================================
# Loader
# =============================================================================


@st.cache_data(show_spinner=False)
def load_reports() -> ReportData:
    """
    Load every report into memory.

    Returns
    -------
    ReportData
    """

    LOGGER.info(
        "Loading Scanner Monitor reports..."
    )

    return ReportData(

        portfolio_summary=_read_csv(
            LATEST_DIR / "portfolio_summary.csv"
        ),

        holdings=_read_csv(
            LATEST_DIR / "holdings.csv"
        ),

        risk_summary=_read_csv(
            LATEST_DIR / "risk_summary.csv"
        ),

        execution_summary=_read_csv(
            LATEST_DIR / "execution_summary.csv"
        ),

        daily_monitor=_read_csv(
            LATEST_DIR / "daily_monitor_latest.csv"
        ),

        performance_summary=_read_csv(
            LATEST_DIR / "performance_summary.csv"
        ),

        orders=_read_csv(
            LATEST_DIR / "orders.csv"
        ),

        sector_exposure=_read_csv(
            LATEST_DIR / "sector_exposure.csv"
        ),

        risk_violations=_read_csv(
            LATEST_DIR / "risk_violations.csv"
        ),

        portfolio_history=_read_csv(
            HISTORY_DIR / "portfolio_history.csv"
        ),

        performance_history=_read_csv(
            HISTORY_DIR / "performance_history.csv"
        ),

        risk_history=_read_csv(
            HISTORY_DIR / "risk_history.csv"
        ),

        execution_history=_read_csv(
            HISTORY_DIR / "execution_history.csv"
        ),

        regime_history=_read_csv(
            HISTORY_DIR / "regime_history.csv"
        ),

        signal_history=_read_csv(
            HISTORY_DIR / "signal_history.csv"
        ),

        daily_monitor_history=_read_csv(
            HISTORY_DIR / "daily_monitor.csv"
        ),

        report_json=_read_json(
            LATEST_DIR / "Portfolio_Report.json"
        ),

    )


# =============================================================================
# Utilities
# =============================================================================


def latest_files() -> list[Path]:
    """
    Return latest report files.
    """

    if not LATEST_DIR.exists():

        return []

    return sorted(
        LATEST_DIR.glob("*"),
    )


def history_files() -> list[Path]:
    """
    Return history files.
    """

    if not HISTORY_DIR.exists():

        return []

    return sorted(
        HISTORY_DIR.glob("*"),
    )


def file_exists(
    path: Path,
) -> bool:
    """
    Return True if the file exists.
    """

    return path.exists()


def report_exists(
    filename: str,
) -> bool:
    """
    Check report existence.
    """

    return (
        LATEST_DIR / filename
    ).exists()


def report_path(
    filename: str,
) -> Path:
    """
    Return report path.
    """

    return LATEST_DIR / filename


def history_path(
    filename: str,
) -> Path:
    """
    Return history file path.
    """

    return HISTORY_DIR / filename


def clear_cache() -> None:
    """
    Clear all cached report data.
    """

    st.cache_data.clear()


def refresh_reports() -> None:
    """
    Backward-compatible alias.
    """

    clear_cache()

__all__ = [

    "ReportData",

    "load_reports",

    "load_csv",

    "load_excel",

    "load_json",

    "latest_files",

    "history_files",

    "report_exists",

    "report_path",

    "history_path",

    "file_exists",

    "clear_cache",

    "refresh_reports",

]