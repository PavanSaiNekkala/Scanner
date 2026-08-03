"""
ui.sidebar
==========

Reusable sidebar components for the
Institutional Scanner Monitor.

Foundation Layer

Responsibilities
----------------
- Sidebar configuration
- File system helpers
- Report metadata
- Storage utilities
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import streamlit as st

from ui.loader import (
    HISTORY_DIR,
    LATEST_DIR,
    refresh_reports,
)


# =============================================================================
# Configuration
# =============================================================================


@dataclass(
    slots=True,
    frozen=True,
)
class SidebarConfig:
    """
    Sidebar application configuration.
    """

    title: str = (
        "📊 Scanner Monitor"
    )

    subtitle: str = (
        "Institutional Reporting Dashboard"
    )

    version: str = (
        "1.0.0"
    )

    edition: str = (
        "Institutional Edition"
    )

    copyright: str = (
        "© 2026"
    )

    timestamp_format: str = (
        "%Y-%m-%d %H:%M:%S"
    )


CONFIG = SidebarConfig()


# =============================================================================
# File System Helpers
# =============================================================================


def safe_file_count(
    directory: Path,
) -> int:
    """
    Return number of files
    inside a directory.
    """

    if not directory.exists():

        return 0

    return sum(

        1

        for file in directory.iterdir()

        if file.is_file()

    )


def safe_directory_size(
    directory: Path,
) -> float:
    """
    Calculate directory size
    in MB.
    """

    if not directory.exists():

        return 0.0

    total = 0

    for file in directory.rglob("*"):

        if file.is_file():

            total += file.stat().st_size

    return (

        total

        /

        (

            1024 * 1024

        )

    )


def latest_modified_time(
    directory: Path = LATEST_DIR,
) -> str:
    """
    Return latest modification
    timestamp.
    """

    if not directory.exists():

        return "N/A"


    files = [

        file

        for file in directory.iterdir()

        if file.is_file()

    ]


    if not files:

        return "N/A"


    latest = max(

        files,

        key=lambda item:

            item.stat().st_mtime,

    )


    return datetime.fromtimestamp(

        latest.stat().st_mtime,

    ).strftime(

        CONFIG.timestamp_format,

    )


# =============================================================================
# Report Metadata
# =============================================================================


def latest_report_count() -> int:
    """
    Count latest reports.
    """

    return safe_file_count(

        LATEST_DIR,

    )


def history_report_count() -> int:
    """
    Count historical reports.
    """

    return safe_file_count(

        HISTORY_DIR,

    )


def report_storage_summary() -> dict[str, float]:
    """
    Return report storage metrics.
    """

    return {

        "Latest":

            safe_directory_size(

                LATEST_DIR,

            ),

        "History":

            safe_directory_size(

                HISTORY_DIR,

            ),

    }


# =============================================================================
# Sidebar HTML Helper
# =============================================================================


def sidebar_metric(
    label: str,
    value: str | int | float,
) -> None:
    """
    Standard sidebar metric.
    """

    st.sidebar.metric(

        label,

        value,

    )

# =============================================================================
# Sidebar Header
# =============================================================================


def sidebar_header() -> None:
    """
    Render sidebar title.
    """

    st.sidebar.title(

        CONFIG.title,

    )

    st.sidebar.caption(

        CONFIG.subtitle,

    )


# =============================================================================
# Scanner Status
# =============================================================================


def scanner_status() -> None:
    """
    Display scanner health status.
    """

    st.sidebar.subheader(

        "Scanner Status",

    )

    latest_count = latest_report_count()


    if not LATEST_DIR.exists():

        st.sidebar.error(

            "Reports Directory Missing",

        )

        sidebar_metric(

            "Latest Files",

            0,

        )

        return


    if latest_count == 0:

        st.sidebar.warning(

            "No Reports Found",

        )

    else:

        st.sidebar.success(

            "Reports Available",

        )


    sidebar_metric(

        "Latest Files",

        latest_count,

    )


# =============================================================================
# Report Information
# =============================================================================


def report_information() -> None:
    """
    Display report metadata.
    """

    st.sidebar.subheader(

        "Reports",

    )


    sidebar_metric(

        "Latest Reports",

        latest_report_count(),

    )


    sidebar_metric(

        "History Files",

        history_report_count(),

    )


    st.sidebar.caption(

        "Last Updated",

    )


    st.sidebar.info(

        latest_modified_time(),

    )


# =============================================================================
# Storage Information
# =============================================================================


def storage_information() -> None:
    """
    Display report storage usage.
    """

    st.sidebar.subheader(

        "Storage",

    )


    storage = report_storage_summary()


    sidebar_metric(

        "Latest Folder",

        f"{storage['Latest']:.2f} MB",

    )


    sidebar_metric(

        "History Folder",

        f"{storage['History']:.2f} MB",

    )


# =============================================================================
# Application Information
# =============================================================================


def application_information() -> None:
    """
    Display application metadata.
    """

    st.sidebar.subheader(

        "Application",

    )


    st.sidebar.caption(

        "Scanner Monitor",

    )


    st.sidebar.caption(

        f"Version {CONFIG.version}",

    )


    st.sidebar.caption(

        CONFIG.edition,

    )


    st.sidebar.caption(

        CONFIG.copyright,

    )

# =============================================================================
# Refresh Controls
# =============================================================================


def refresh_section() -> None:
    """
    Render refresh controls.
    """

    st.sidebar.subheader(

        "Refresh",

    )


    auto_refresh = st.sidebar.checkbox(

        "Auto Refresh",

        value=False,

        key="sidebar_auto_refresh",

    )


    if st.sidebar.button(

        "Refresh Reports",

        use_container_width=True,

        key="refresh_reports_button",

    ):

        refresh_reports()

        st.rerun()


    if auto_refresh:

        st.sidebar.info(

            "Auto refresh enabled.",

        )



# =============================================================================
# Navigation Helpers
# =============================================================================


def navigation_information() -> None:
    """
    Display navigation help.
    """

    st.sidebar.subheader(

        "Navigation",

    )

    st.sidebar.caption(

        "Use the pages menu to access:",

    )


    items = [

        "Dashboard",

        "Portfolio",

        "Holdings",

        "Daily Monitor",

        "Risk",

        "Performance",

        "Execution",

        "History",

        "Downloads",

    ]


    for item in items:

        st.sidebar.write(

            f"• {item}",

        )



# =============================================================================
# Complete Sidebar Renderer
# =============================================================================


def render_sidebar() -> None:
    """
    Render complete application sidebar.
    """

    sidebar_header()


    st.sidebar.divider()


    scanner_status()


    st.sidebar.divider()


    report_information()


    st.sidebar.divider()


    refresh_section()


    st.sidebar.divider()


    storage_information()


    st.sidebar.divider()


    navigation_information()


    st.sidebar.divider()


    application_information()



# =============================================================================
# Sidebar Health Summary
# =============================================================================


def sidebar_health() -> dict[str, object]:
    """
    Return sidebar health information.
    """

    return {

        "reports_available":

            LATEST_DIR.exists(),

        "latest_reports":

            latest_report_count(),

        "history_reports":

            history_report_count(),

        "latest_modified":

            latest_modified_time(),

        "storage":

            report_storage_summary(),

    }

# =============================================================================
# Environment Information
# =============================================================================


def environment_information() -> None:
    """
    Display runtime information.
    """

    st.sidebar.subheader(

        "Environment",

    )


    st.sidebar.caption(

        "Streamlit Dashboard",

    )


    st.sidebar.caption(

        "Report Driven Architecture",

    )


    st.sidebar.caption(

        "Production Monitoring",

    )


# =============================================================================
# Diagnostic Panel
# =============================================================================


def diagnostic_panel() -> None:
    """
    Display sidebar diagnostics.
    """

    health = sidebar_health()


    st.sidebar.subheader(

        "Health",

    )


    if health["reports_available"]:

        st.sidebar.success(

            "Report System Healthy",

        )

    else:

        st.sidebar.error(

            "Report System Offline",

        )


    sidebar_metric(

        "Latest Reports",

        health["latest_reports"],

    )


    sidebar_metric(

        "History Reports",

        health["history_reports"],

    )



# =============================================================================
# Enhanced Application Panel
# =============================================================================


def application_panel() -> None:
    """
    Complete application information.
    """

    application_information()

    environment_information()



# =============================================================================
# Complete Enterprise Sidebar
# =============================================================================


def enterprise_sidebar() -> None:
    """
    Full institutional sidebar.

    Intended entry point for
    production dashboard.
    """

    sidebar_header()


    st.sidebar.divider()


    scanner_status()


    st.sidebar.divider()


    report_information()


    st.sidebar.divider()


    diagnostic_panel()


    st.sidebar.divider()


    refresh_section()


    st.sidebar.divider()


    storage_information()


    st.sidebar.divider()


    navigation_information()


    st.sidebar.divider()


    application_panel()



# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    # Configuration

    "CONFIG",


    # Helpers

    "safe_file_count",

    "safe_directory_size",

    "latest_modified_time",

    "latest_report_count",

    "history_report_count",

    "report_storage_summary",


    # Components

    "sidebar_metric",

    "sidebar_header",

    "scanner_status",

    "report_information",

    "storage_information",

    "application_information",

    "environment_information",

    "navigation_information",

    "refresh_section",


    # Health

    "sidebar_health",

    "diagnostic_panel",


    # Renderers

    "render_sidebar",

    "enterprise_sidebar",

]