"""
ui/loader.py
============

Institutional Report Loader

Centralized loading engine for all
Scanner Monitor reports.

Features
--------
- Automatic report discovery
- Cached loading
- Repository metadata
- Validation
- CSV / Excel / JSON support
- History support
- Graceful fallback
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from core.logger import get_logger

LOGGER = get_logger(__name__)

# =============================================================================
# Repository
# =============================================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

LATEST_DIR = (
    REPORTS_DIR
    / "latest"
)

HISTORY_DIR = (
    REPORTS_DIR
    / "history"
)

# =============================================================================
# Report Definitions
# =============================================================================

LATEST_REPORTS = {

    "portfolio_summary":
        "portfolio_summary.csv",

    "holdings":
        "holdings.csv",

    "risk_summary":
        "risk_summary.csv",

    "execution_summary":
        "execution_summary.csv",

    "daily_monitor":
        "daily_monitor_latest.csv",

    "performance_summary":
        "performance_summary.csv",

    "orders":
        "orders.csv",

    "trade_list":
        "trade_list.csv",

    "rebalance_orders":
        "rebalance_orders.csv",

    "sector_exposure":
        "sector_exposure.csv",

    "risk_violations":
        "risk_violations.csv",

}

HISTORY_REPORTS = {

    "portfolio_history":
        "portfolio_history.csv",

    "performance_history":
        "performance_history.csv",

    "risk_history":
        "risk_history.csv",

    "execution_history":
        "execution_history.csv",

    "signal_history":
        "signal_history.csv",

    "regime_history":
        "regime_history.csv",

    "daily_monitor_history":
        "daily_monitor.csv",

    "scan_history":
        "scan_history.csv",

    "scan_history_metrics":
        "scan_history_metrics.csv",

}

JSON_REPORTS = {

    "report_json":
        "Portfolio_Report.json",

}

EXCEL_REPORTS = {

    "report_excel":
        "Portfolio_Report.xlsx",

}

# =============================================================================
# Metadata
# =============================================================================


@dataclass(slots=True, frozen=True)
class ReportMetadata:
    """
    Metadata describing a report.
    """

    name: str

    path: Path

    exists: bool

    rows: int

    columns: int

    size_mb: float

    modified: str


# =============================================================================
# Report Container
# =============================================================================


@dataclass(slots=True)
class ReportData:
    """
    Central report container.
    """

    latest: dict[str, pd.DataFrame]

    history: dict[str, pd.DataFrame]

    excel: dict[str, pd.DataFrame]

    json: dict[str, dict[str, Any]]

    metadata: dict[str, ReportMetadata]


# =============================================================================
# Empty Objects
# =============================================================================


def empty_dataframe() -> pd.DataFrame:
    """
    Empty DataFrame.
    """

    return pd.DataFrame()


def empty_json() -> dict[str, Any]:
    """
    Empty JSON.
    """

    return {}


# =============================================================================
# Metadata Builder
# =============================================================================


def build_metadata(
    path: Path,
    dataframe: pd.DataFrame | None = None,
) -> ReportMetadata:
    """
    Build report metadata.
    """

    exists = path.exists()

    if dataframe is None:

        dataframe = empty_dataframe()

    if exists:

        stat = path.stat()

        size_mb = (
            stat.st_size
            / 1024
            / 1024
        )

        modified = (
            pd.Timestamp(
                stat.st_mtime,
                unit="s",
            )

            .strftime(
                "%d %b %Y %H:%M"
            )
        )

    else:

        size_mb = 0.0

        modified = "-"

    return ReportMetadata(

        name=path.name,

        path=path,

        exists=exists,

        rows=len(dataframe),

        columns=len(
            dataframe.columns,
        ),

        size_mb=size_mb,

        modified=modified,

    )

# =============================================================================
# CSV Loader
# =============================================================================


@st.cache_data(show_spinner=False)
def load_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Load CSV safely.
    """

    if not path.exists():

        LOGGER.warning(
            "Missing CSV: %s",
            path.name,
        )

        return empty_dataframe()

    try:

        dataframe = pd.read_csv(
            path,
        )

        LOGGER.info(
            "Loaded %s (%d rows)",
            path.name,
            len(dataframe),
        )

        return dataframe

    except Exception:

        LOGGER.exception(
            "Unable to load %s",
            path.name,
        )

        return empty_dataframe()

# =============================================================================
# Excel Loader
# =============================================================================


@st.cache_data(show_spinner=False)
def load_excel(
    path: Path,
    sheet: int | str = 0,
) -> pd.DataFrame:
    """
    Load Excel safely.
    """

    if not path.exists():

        return empty_dataframe()

    try:

        return pd.read_excel(

            path,

            sheet_name=sheet,

        )

    except Exception:

        LOGGER.exception(
            "Unable to load Excel %s",
            path.name,
        )

        return empty_dataframe()

# =============================================================================
# JSON Loader
# =============================================================================


@st.cache_data(show_spinner=False)
def load_json(
    path: Path,
) -> dict[str, Any]:
    """
    Load JSON safely.
    """

    if not path.exists():

        return empty_json()

    try:

        with open(

            path,

            encoding="utf-8",

        ) as file:

            return json.load(
                file,
            )

    except Exception:

        LOGGER.exception(
            "Unable to load JSON %s",
            path.name,
        )

        return empty_json()


# =============================================================================
# Dynamic Loaders
# =============================================================================


@st.cache_data(show_spinner=False)
def load_latest_reports(
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, ReportMetadata],
]:
    """
    Load all latest reports.
    """

    reports: dict[
        str,
        pd.DataFrame,
    ] = {}

    metadata: dict[
        str,
        ReportMetadata,
    ] = {}

    LOGGER.info(
        "Loading latest reports..."
    )

    for key, filename in (

        LATEST_REPORTS.items()

    ):

        path = (
            LATEST_DIR
            / filename
        )

        dataframe = load_csv(
            path,
        )

        reports[key] = dataframe

        metadata[key] = build_metadata(

            path,

            dataframe,

        )

    return (

        reports,

        metadata,

    )


@st.cache_data(show_spinner=False)
def load_history_reports(
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, ReportMetadata],
]:
    """
    Load all historical reports.
    """

    reports: dict[
        str,
        pd.DataFrame,
    ] = {}

    metadata: dict[
        str,
        ReportMetadata,
    ] = {}

    LOGGER.info(
        "Loading history reports..."
    )

    for key, filename in (

        HISTORY_REPORTS.items()

    ):

        path = (
            HISTORY_DIR
            / filename
        )

        dataframe = load_csv(
            path,
        )

        reports[key] = dataframe

        metadata[key] = build_metadata(

            path,

            dataframe,

        )

    return (

        reports,

        metadata,

    )


@st.cache_data(show_spinner=False)
def load_excel_reports(
) -> dict[
    str,
    pd.DataFrame,
]:
    """
    Load Excel reports.
    """

    reports: dict[
        str,
        pd.DataFrame,
    ] = {}

    LOGGER.info(
        "Loading Excel reports..."
    )

    for key, filename in (

        EXCEL_REPORTS.items()

    ):

        reports[key] = load_excel(

            LATEST_DIR
            / filename,

        )

    return reports


@st.cache_data(show_spinner=False)
def load_json_reports(
) -> dict[
    str,
    dict[str, Any],
]:
    """
    Load JSON reports.
    """

    reports: dict[
        str,
        dict[str, Any],
    ] = {}

    LOGGER.info(
        "Loading JSON reports..."
    )

    for key, filename in (

        JSON_REPORTS.items()

    ):

        reports[key] = load_json(

            LATEST_DIR
            / filename,

        )

    return reports


# =============================================================================
# Validation
# =============================================================================


def validate_reports(
    reports: ReportData,
) -> dict[
    str,
    list[str],
]:
    """
    Validate loaded reports.

    Returns
    -------
    dict
        Validation summary.
    """

    missing: list[str] = []

    empty: list[str] = []

    for name, meta in (

        reports.metadata.items()

    ):

        if not meta.exists:

            missing.append(
                name,
            )

            continue

        dataframe = (

            reports.latest.get(
                name,
            )

            or

            reports.history.get(
                name,
            )
        )

        if (

            dataframe is not None

            and

            dataframe.empty

        ):

            empty.append(
                name,
            )

    return {

        "missing": missing,

        "empty": empty,

        "loaded": [

            key

            for key, meta

            in reports.metadata.items()

            if meta.exists

        ],

    }


# =============================================================================
# Main Loader
# =============================================================================


@st.cache_data(show_spinner=False)
def load_reports(
) -> ReportData:
    """
    Load every institutional report.
    """

    LOGGER.info(
        "Loading Scanner Monitor repository..."
    )

    latest, latest_meta = (

        load_latest_reports()

    )

    history, history_meta = (

        load_history_reports()

    )

    metadata = {

        **latest_meta,

        **history_meta,

    }

    return ReportData(

        latest=latest,

        history=history,

        excel=load_excel_reports(),

        json=load_json_reports(),

        metadata=metadata,

    )

# =============================================================================
# Repository Discovery
# =============================================================================


def latest_files() -> list[Path]:
    """
    Return all latest report files.
    """

    if not LATEST_DIR.exists():

        return []

    return sorted(

        (

            file

            for file in LATEST_DIR.rglob("*")

            if file.is_file()

        ),

        key=lambda file: file.name.lower(),

    )


def history_files() -> list[Path]:
    """
    Return all history report files.
    """

    if not HISTORY_DIR.exists():

        return []

    return sorted(

        (

            file

            for file in HISTORY_DIR.rglob("*")

            if file.is_file()

        ),

        key=lambda file: file.name.lower(),

    )


def repository_files() -> list[Path]:
    """
    Return every report file.
    """

    return (

        latest_files()

        +

        history_files()

    )


# =============================================================================
# Report Lookup
# =============================================================================


def report_exists(
    filename: str,
) -> bool:
    """
    Check whether a report exists.
    """

    return (

        report_path(
            filename,
        )

        .exists()

    )


def report_path(
    filename: str,
) -> Path:
    """
    Return latest report path.
    """

    return (

        LATEST_DIR

        / filename

    )


def history_path(
    filename: str,
) -> Path:
    """
    Return history report path.
    """

    return (

        HISTORY_DIR

        / filename

    )


def metadata(
    report_name: str,
) -> ReportMetadata | None:
    """
    Return report metadata.
    """

    reports = load_reports()

    return reports.metadata.get(

        report_name,

    )


# =============================================================================
# Repository Summary
# =============================================================================


def repository_summary(
) -> pd.DataFrame:
    """
    Return repository summary.
    """

    reports = load_reports()

    summary = []

    for name, meta in (

        reports.metadata.items()

    ):

        summary.append(

            {

                "Report": name,

                "Exists": meta.exists,

                "Rows": meta.rows,

                "Columns": meta.columns,

                "Size (MB)": round(

                    meta.size_mb,

                    3,

                ),

                "Modified": meta.modified,

            }

        )

    return (

        pd.DataFrame(

            summary,

        )

        .sort_values(

            "Report",

        )

        .reset_index(

            drop=True,

        )

    )


# =============================================================================
# Cache
# =============================================================================


def clear_cache() -> None:
    """
    Clear Streamlit cache.
    """

    LOGGER.info(
        "Clearing report cache."
    )

    st.cache_data.clear()


def refresh_reports(
) -> ReportData:
    """
    Refresh report repository.
    """

    clear_cache()

    return load_reports()


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [

    "ReportData",

    "ReportMetadata",

    "load_reports",

    "load_latest_reports",

    "load_history_reports",

    "load_excel_reports",

    "load_json_reports",

    "load_csv",

    "load_excel",

    "load_json",

    "validate_reports",

    "repository_summary",

    "repository_files",

    "latest_files",

    "history_files",

    "report_exists",

    "report_path",

    "history_path",

    "metadata",

    "clear_cache",

    "refresh_reports",

]