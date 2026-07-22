"""
Settings
========

Institutional Strategy Platform Settings
"""

from __future__ import annotations

import platform
from pathlib import Path

import pandas as pd
import streamlit as st

from services.loader import (
    DEFAULT_OUTPUT_FOLDER,
    clear_session,
    refresh_reports,
)

from themes import apply_theme


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "⚙️ Settings"

PAGE_CAPTION = (
    "Application configuration, diagnostics and maintenance."
)

APP_VERSION = "4.0"


REPORT_KEYS = {
    "Strategy": "strategy_report",
    "Stock": "stock_report",
    "Leaderboard": "leaderboard_report",
    "Portfolio": "portfolio_report",
    "Robustness": "robustness_report",
    "Correlation": "correlation_report",
    "Final Report": "final_report",
}


# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render settings header.
    """

    st.title(
        PAGE_TITLE,
    )

    st.caption(
        PAGE_CAPTION,
    )

    st.divider()


# ============================================================
# Session Overview
# ============================================================


def render_session_overview() -> None:
    """
    Display session information.
    """

    loaded = st.session_state.get(
        "reports_loaded",
        False,
    )


    output_folder = Path(
        st.session_state.get(
            "output_folder",
            DEFAULT_OUTPUT_FOLDER,
        )
    )


    loaded_reports = sum(
        key in st.session_state
        for key in REPORT_KEYS.values()
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Reports Status",
            "Loaded" if loaded else "Not Loaded",
        )


    with c2:

        st.metric(
            "Reports Available",
            loaded_reports,
        )


    with c3:

        st.metric(
            "Output Folder",
            output_folder.name,
        )


    with c4:

        st.metric(
            "Version",
            f"v{APP_VERSION}",
        )


# ============================================================
# Output Directory
# ============================================================


def render_output_directory() -> None:
    """
    Display output folder configuration.
    """

    st.divider()

    st.subheader(
        "Output Directory",
    )


    folder = st.text_input(
        "Current Output Folder",
        value=str(
            st.session_state.get(
                "output_folder",
                DEFAULT_OUTPUT_FOLDER,
            )
        ),
    )


    path = Path(
        folder,
    )


    if path.exists():

        st.success(
            "Directory exists.",
        )

        files = list(
            path.glob(
                "*.xlsx"
            )
        )

        st.info(
            f"{len(files)} Excel reports found.",
        )


    else:

        st.warning(
            "Directory does not exist.",
        )


# ============================================================
# Maintenance
# ============================================================


def render_maintenance() -> None:
    """
    Render maintenance controls.
    """

    st.divider()

    st.subheader(
        "Maintenance",
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        if st.button(
            "🧹 Clear Cache",
            use_container_width=True,
        ):

            st.cache_data.clear()

            st.success(
                "Cache cleared.",
            )


    with c2:

        if st.button(
            "🔄 Refresh Reports",
            use_container_width=True,
        ):

            with st.spinner(
                "Reloading latest reports...",
            ):

                refresh_reports()


            st.success(
                "Reports refreshed.",
            )

            st.rerun()


    with c3:

        if st.button(
            "🗑 Reset Session",
            use_container_width=True,
        ):

            clear_session()

            st.success(
                "Session reset.",
            )

            st.rerun()


# ============================================================
# Environment Information
# ============================================================


def render_environment() -> None:
    """
    Display environment details.
    """

    st.divider()

    st.subheader(
        "Environment",
    )


    env = pd.DataFrame(
        {
            "Property": [
                "Application",
                "Version",
                "Framework",
                "Streamlit",
                "Python",
                "Platform",
            ],

            "Value": [
                "Institutional Strategy Platform",
                APP_VERSION,
                "Streamlit",
                st.__version__,
                platform.python_version(),
                platform.platform(),
            ],
        }
    )


    st.dataframe(
        env,
        hide_index=True,
        use_container_width=True,
    )


# ============================================================
# Report Status
# ============================================================


def render_report_status() -> None:
    """
    Display report loading status.
    """

    st.divider()

    st.subheader(
        "Loaded Reports",
    )


    rows = []


    for name, key in REPORT_KEYS.items():

        loaded = key in st.session_state


        rows.append(
            {
                "Report": name,
                "Session Key": key,
                "Status": (
                    "Loaded"
                    if loaded
                    else
                    "Not Loaded"
                ),
            }
        )


    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# ============================================================
# About
# ============================================================


def render_about() -> None:
    """
    Display application information.
    """

    st.divider()


    with st.expander(
        "About Institutional Strategy Platform",
        expanded=False,
    ):

        st.markdown(
            f"""
## Institutional Strategy Comparison Platform

**Version:** {APP_VERSION}


### Analytics Modules

- Strategy Comparison
- Stock Analytics
- Institutional Leaderboards
- Portfolio Construction
- Correlation Analytics
- Robustness Evaluation
- Executive Dashboard
- Report Generation


### Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Excel Reporting Engine
"""
        )


# ============================================================
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render footer.
    """

    st.divider()

    st.caption(
        "Institutional Strategy Comparison Platform • Settings"
    )


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Render settings page.
    """

    render_header()

    render_session_overview()

    render_output_directory()

    render_maintenance()

    render_environment()

    render_report_status()

    render_about()

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()