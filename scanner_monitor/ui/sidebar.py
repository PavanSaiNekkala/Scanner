"""
ui.sidebar
==========

Reusable sidebar for the Institutional Scanner Monitor.

Features
--------
- Scanner status
- Report information
- Refresh button
- Auto refresh
- Report timestamps
- Navigation helpers
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from ui.loader import (
    HISTORY_DIR,
    LATEST_DIR,
    refresh_reports,
)

# =============================================================================
# Helpers
# =============================================================================


def _latest_modified() -> str:
    """
    Return latest modification timestamp.
    """

    files = list(LATEST_DIR.glob("*"))

    if not files:

        return "N/A"

    latest = max(
        files,
        key=lambda file: file.stat().st_mtime,
    )

    return datetime.fromtimestamp(
        latest.stat().st_mtime,
    ).strftime(
        "%Y-%m-%d %H:%M:%S",
    )


def _directory_size(
    directory: Path,
) -> float:
    """
    Directory size in MB.
    """

    if not directory.exists():

        return 0.0

    size = sum(
        file.stat().st_size
        for file in directory.rglob("*")
        if file.is_file()
    )

    return size / (1024 * 1024)


# =============================================================================
# Sidebar
# =============================================================================


def render_sidebar() -> None:
    """
    Render the application sidebar.
    """

    st.sidebar.title(
        "📊 Scanner Monitor",
    )

    st.sidebar.caption(
        "Institutional Reporting Dashboard",
    )

    st.sidebar.divider()

    scanner_status()

    st.sidebar.divider()

    report_information()

    st.sidebar.divider()

    refresh_section()

    st.sidebar.divider()

    storage_information()

    st.sidebar.divider()

    application_information()


# =============================================================================
# Scanner Status
# =============================================================================


def scanner_status() -> None:
    """
    Scanner health.
    """

    st.sidebar.subheader(
        "Scanner Status",
    )

    if not LATEST_DIR.exists():

        st.sidebar.error(
            "Reports Missing",
        )

        return

    count = len(
        list(
            LATEST_DIR.glob("*"),
        )
    )

    if count == 0:

        st.sidebar.warning(
            "No Reports Found",
        )

    else:

        st.sidebar.success(
            "Reports Available",
        )

    st.sidebar.metric(
        "Latest Files",
        count,
    )


# =============================================================================
# Report Information
# =============================================================================


def report_information() -> None:
    """
    Latest report information.
    """

    st.sidebar.subheader(
        "Reports",
    )

    st.sidebar.metric(

        "Latest Reports",

        len(
            list(
                LATEST_DIR.glob("*"),
            )
        ),

    )

    st.sidebar.metric(

        "History Files",

        len(
            list(
                HISTORY_DIR.glob("*"),
            )
        ),

    )

    st.sidebar.text(
        "Last Updated",
    )

    st.sidebar.caption(
        _latest_modified(),
    )


# =============================================================================
# Refresh
# =============================================================================


def refresh_section() -> None:
    """
    Cache refresh.
    """

    st.sidebar.subheader(
        "Refresh",
    )

    auto = st.sidebar.checkbox(

        "Auto Refresh",

        value=False,

    )

    if st.sidebar.button(

        "Refresh Reports",

        use_container_width=True,

    ):

        refresh_reports()

        st.rerun()

    if auto:

        st.sidebar.info(
            "Refresh page every minute.",
        )


# =============================================================================
# Storage
# =============================================================================


def storage_information() -> None:
    """
    Report storage metrics.
    """

    st.sidebar.subheader(
        "Storage",
    )

    st.sidebar.metric(

        "Latest Folder",

        f"{_directory_size(LATEST_DIR):.2f} MB",

    )

    st.sidebar.metric(

        "History Folder",

        f"{_directory_size(HISTORY_DIR):.2f} MB",

    )


# =============================================================================
# Footer
# =============================================================================


def application_information() -> None:
    """
    Application footer.
    """

    st.sidebar.subheader(
        "Application",
    )

    st.sidebar.caption(
        "Scanner Monitor",
    )

    st.sidebar.caption(
        "Version 1.0.0",
    )

    st.sidebar.caption(
        "Institutional Edition",
    )

    st.sidebar.caption(
        "© 2026",
    )