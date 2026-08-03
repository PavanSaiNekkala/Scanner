"""
scanner_monitor.streamlit_app
=============================

Institutional Scanner Monitor

Main Streamlit application bootstrap.

Responsibilities
----------------
- Application startup
- Page configuration
- Theme initialization
- Report availability checks
- Logging lifecycle
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st
import pandas as pd

from core.config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_LAYOUT,
    DEFAULT_PAGE_ICON,
    LATEST_REPORTS_DIR,
    REPORTS_DIR,
)

from core.logger import get_logger

from core.theme import (
    apply_theme,
    hide_streamlit_style,
    inject_card_css,
    use_wide_layout,
)


LOGGER = get_logger(__name__)


# =============================================================================
# Application Configuration
# =============================================================================


@dataclass(
    slots=True,
    frozen=True,
)
class AppConfig:
    """
    Streamlit application metadata.
    """

    name: str = APP_NAME

    version: str = APP_VERSION

    icon: str = DEFAULT_PAGE_ICON

    layout: str = DEFAULT_LAYOUT

    subtitle: str = (
        "Production Portfolio "
        "Reporting Dashboard"
    )


CONFIG = AppConfig()


# =============================================================================
# Page Configuration
# =============================================================================


def configure_page() -> None:
    """
    Configure Streamlit page.
    """

    st.set_page_config(

        page_title=CONFIG.name,

        page_icon=CONFIG.icon,

        layout=CONFIG.layout,

        initial_sidebar_state="expanded",

    )


# =============================================================================
# Theme Bootstrap
# =============================================================================


def initialize_theme() -> None:
    """
    Initialize application theme.
    """

    apply_theme()

    inject_card_css()

    use_wide_layout()

    hide_streamlit_style()


# =============================================================================
# Report Health
# =============================================================================


@st.cache_data(
    show_spinner=False,
)
def reports_available() -> bool:
    """
    Validate report directories.
    """

    return (

        REPORTS_DIR.exists()

        and

        LATEST_REPORTS_DIR.exists()

    )


def report_health() -> dict[str, bool]:
    """
    Return report system health.
    """

    return {

        "reports_directory":

            REPORTS_DIR.exists(),

        "latest_directory":

            LATEST_REPORTS_DIR.exists(),

        "available":

            reports_available(),

    }


def ensure_reports_available() -> bool:
    """
    Validate reports before loading.
    """

    if reports_available():

        return True


    LOGGER.warning(
        "Reports directory unavailable."
    )


    st.error(
        "Reports directory not found."
    )


    return False

# =============================================================================
# UI Imports
# =============================================================================

from ui.loader import load_reports

from ui.sidebar import (
    enterprise_sidebar,
)

from ui.metrics import (
    metric_row,
)

from ui.components import (
    page_title,
    section,
    info_box,
    error_box,
)


# =============================================================================
# Dashboard Sidebar
# =============================================================================


def render_application_sidebar() -> None:
    """
    Render institutional sidebar.
    """

    enterprise_sidebar()


# =============================================================================
# Executive Summary
# =============================================================================


def render_summary() -> None:
    """
    Render executive dashboard KPIs.
    """

    reports = load_reports()


    latest = reports.latest


    metric_row(

        [

            (

                "Holdings",

                len(

                    latest.get(

                        "holdings",

                        pd.DataFrame(),

                    )

                ),

                "number",

            ),


            (

                "Daily Monitor",

                len(

                    latest.get(

                        "daily_monitor",

                        pd.DataFrame(),

                    )

                ),

                "number",

            ),


            (

                "Risk Metrics",

                len(

                    latest.get(

                        "risk_summary",

                        pd.DataFrame(),

                    )

                ),

                "number",

            ),


            (

                "Execution",

                len(

                    latest.get(

                        "execution_summary",

                        pd.DataFrame(),

                    )

                ),

                "number",

            ),

        ]

    )

# =============================================================================
# Dashboard Overview
# =============================================================================


def render_overview() -> None:
    """
    Render application overview.
    """

    section(

        "Dashboard Overview",

        (

            "Institutional portfolio monitoring "

            "and reporting system."

        ),

    )


    st.markdown(

        """
The dashboard provides monitoring for:

- Portfolio Summary
- Holdings
- Daily Monitor
- Risk Analytics
- Execution Summary
- Performance Analytics
- Historical Reports
- Report Downloads

Navigate using the Streamlit pages menu.
"""

    )


    info_box(

        "Additional pages are automatically loaded "
        "from the pages/ directory."

    )


# =============================================================================
# Report Failure Handler
# =============================================================================


def render_report_error() -> None:
    """
    Display report loading error.
    """

    error_box(

        "Unable to load report data."

    )

# =============================================================================
# Application Lifecycle
# =============================================================================


def initialize_application() -> None:
    """
    Initialize application services.
    """

    LOGGER.info(

        "Initializing %s",

        CONFIG.name,

    )

    configure_page()

    initialize_theme()



# =============================================================================
# Main Application
# =============================================================================


def main() -> None:
    """
    Streamlit application entry point.
    """

    try:

        initialize_application()


        render_application_sidebar()


        page_title(

            f"{CONFIG.icon} {CONFIG.name}",

            CONFIG.subtitle,

        )


        if not ensure_reports_available():

            return


        st.divider()


        render_summary()


        st.divider()


        render_overview()


        LOGGER.info(

            "%s started successfully",

            CONFIG.name,

        )


    except Exception as exc:

        LOGGER.exception(

            "Application startup failed.",

        )

        render_report_error()

        st.exception(

            exc,

        )



# =============================================================================
# Public API
# =============================================================================


__all__ = [

    "CONFIG",

    "configure_page",

    "initialize_theme",

    "reports_available",

    "report_health",

    "ensure_reports_available",

    "render_application_sidebar",

    "render_summary",

    "render_overview",

    "initialize_application",

    "main",

]


# =============================================================================
# Entry Point
# =============================================================================


if __name__ == "__main__":

    main()