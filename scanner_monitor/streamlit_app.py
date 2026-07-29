"""
streamlit_app.py
================

Institutional Scanner Monitor

Main entry point for the reporting dashboard.

Author
------
Nekkala Pavan Sai

"""

from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from ui.loader import load_reports

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

LOGGER = logging.getLogger(__name__)

# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

REPORTS_DIR = PROJECT_ROOT / "reports"

LATEST_DIR = REPORTS_DIR / "latest"

HISTORY_DIR = REPORTS_DIR / "history"

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Scanner Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Helpers
# =============================================================================


@st.cache_data(show_spinner=False)
def reports_available() -> bool:
    """
    Check whether report directory exists.

    Returns
    -------
    bool
    """

    return (
        REPORTS_DIR.exists()
        and LATEST_DIR.exists()
    )


def report_status() -> None:
    """
    Display report status.
    """

    if reports_available():

        st.sidebar.success(
            "Reports Loaded",
            icon="✅",
        )

    else:

        st.sidebar.error(
            "Reports Not Found",
            icon="❌",
        )


def sidebar() -> None:
    """
    Sidebar.
    """

    st.sidebar.title(
        "Scanner Monitor"
    )

    st.sidebar.markdown("---")

    report_status()

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "Institutional Portfolio Reporting"
    )

    st.sidebar.caption(
        "Version 1.0"
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:

    sidebar()

    st.title("📊 Institutional Scanner Monitor")

    st.caption(
        "Production Portfolio Reporting Dashboard"
    )

    st.divider()

    if not reports_available():

        st.error(
            "Reports directory not found."
        )

        return

    reports = load_reports()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Holdings",
            len(reports.holdings),
        )

    with col2:

        st.metric(
            "Daily Monitor",
            len(reports.daily_monitor),
        )

    with col3:

        st.metric(
            "Risk Metrics",
            len(reports.risk_summary),
        )
        
    st.divider()

    st.subheader(
        "Dashboard Overview"
    )

    st.markdown(
        """
This dashboard provides institutional monitoring for:

- Portfolio Summary
- Holdings
- Daily Monitor
- Risk Analytics
- Execution Summary
- Performance Analytics
- Historical Reports
- Report Downloads

Use the navigation menu on the left to explore each section.
"""
    )

    st.info(
        "The remaining pages will appear automatically once created inside the pages/ directory."
    )


# =============================================================================

if __name__ == "__main__":

    main()