"""
Sidebar Component
=================

Reusable sidebar for the Institutional Strategy Comparison Platform.
"""

from pathlib import Path

import streamlit as st


def render_sidebar() -> None:
    """Render application sidebar."""

    with st.sidebar:
        # -----------------------------------------------------
        # Branding
        # -----------------------------------------------------

        st.title("📊 Strategy Platform")

        st.caption("Institutional Strategy Comparison v4")

        st.divider()

        # -----------------------------------------------------
        # Navigation
        # -----------------------------------------------------

        st.subheader("Navigation")

        st.page_link("Home.py", label="🏠 Home")

        st.page_link(
            "pages/1_Data_Load.py",
            label="📂 Data Load",
        )

        st.page_link(
            "pages/2_Strategies.py",
            label="📈 Strategies",
        )

        st.page_link(
            "pages/3_Stocks.py",
            label="📊 Stocks",
        )

        st.page_link(
            "pages/4_Leaderboards.py",
            label="🏆 Leaderboards",
        )

        st.page_link(
            "pages/5_Portfolio.py",
            label="💼 Portfolio",
        )

        st.page_link(
            "pages/6_Robustness.py",
            label="🛡 Robustness",
        )

        st.page_link(
            "pages/7_Correlation.py",
            label="🔗 Correlation",
        )

        st.page_link(
            "pages/8_Reports.py",
            label="📄 Reports",
        )

        st.page_link(
            "pages/9_Settings.py",
            label="⚙ Settings",
        )

        st.page_link(
            "pages/10_Executive_Dashboard.py",
            label="📋 Executive Dashboard",
        )

        st.divider()

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        reports_loaded = st.session_state.get(
            "reports_loaded",
            False,
        )

        if reports_loaded:
            st.success("🟢 Reports Loaded")
        else:
            st.warning("🟡 Reports Not Loaded")

        output = st.session_state.get(
            "output_folder",
        )

        if output:
            st.caption(f"📁 {Path(output).name}")

        st.caption("Version v4.0")
