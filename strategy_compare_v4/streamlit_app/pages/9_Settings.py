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
from services.loader import clear_session
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Settings",
    page_icon="⚙",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "⚙ Settings"

PAGE_CAPTION = "Application configuration, diagnostics and maintenance."

APP_VERSION = "4.0"


REPORT_KEYS = {
    "Strategy": "strategy_report",
    "Stock": "stock_report",
    "Leaderboard": "leaderboard_report",
    "Portfolio": "portfolio_report",
    "Robustness": "robustness_report",
    "Correlation": "correlation_report",
    "Final": "final_report",
}


# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render settings header.
    """

    st.title(PAGE_TITLE)

    st.caption(PAGE_CAPTION)

    st.divider()


# ============================================================
# Session Overview
# ============================================================


def render_session_overview() -> None:
    """
    Display current session status.
    """

    reports_loaded = st.session_state.get(
        "reports_loaded",
        False,
    )

    output_folder = st.session_state.get(
        "output_folder",
        "output",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Reports",
            "Loaded" if reports_loaded else "Not Loaded",
        )

    with c2:
        st.metric(
            "Output Folder",
            Path(output_folder).name,
        )

    with c3:
        st.metric(
            "Version",
            f"v{APP_VERSION}",
        )


# ============================================================
# Output Directory
# ============================================================


def render_output_directory() -> None:
    """
    Render output folder settings.
    """

    st.divider()

    st.subheader("Output Directory")

    current = st.session_state.get(
        "output_folder",
        "output",
    )

    folder = st.text_input(
        "Output Folder",
        value=current,
    )

    if Path(folder).exists():
        st.success("Directory exists.")

    else:
        st.warning("Directory not found.")


# ============================================================
# Maintenance
# ============================================================


def render_maintenance() -> None:
    """
    Render maintenance controls.
    """

    st.divider()

    st.subheader("Maintenance")

    left, right = st.columns(2)

    with left:
        if st.button(
            "🧹 Clear Cache",
            use_container_width=True,
        ):
            st.cache_data.clear()

            st.success("Cache cleared.")

    with right:
        if st.button(
            "🔄 Reset Session",
            use_container_width=True,
        ):
            clear_session()

            st.success("Session reset.")


# ============================================================
# Environment Information
# ============================================================


def render_environment() -> None:
    """
    Display system environment.
    """

    st.divider()

    st.subheader("Environment")

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
                platform.system(),
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
    Display loaded report status.
    """

    st.divider()

    st.subheader("Loaded Reports")

    rows = []

    for name, key in REPORT_KEYS.items():
        rows.append(
            {
                "Report": name,
                "Status": "Loaded" if key in st.session_state else "Not Loaded",
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
        st.markdown(f"""
### Institutional Strategy Comparison Platform

**Version:** {APP_VERSION}

#### Modules

- Strategy Comparison
- Stock Comparison
- Institutional Leaderboards
- Portfolio Construction
- Correlation Analysis
- Robustness Analysis
- Executive Dashboard
- Excel Report Generation


#### Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
""")


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


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()

else:
    main()
