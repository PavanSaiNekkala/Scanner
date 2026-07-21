"""
Sidebar Component
=================

Reusable sidebar for the Institutional Strategy Comparison Platform.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

# ============================================================
# Navigation Configuration
# ============================================================

NAVIGATION_ITEMS = [
    ("Home.py", "🏠 Home"),
    ("pages/1_Data_Load.py", "📂 Data Load"),
    ("pages/2_Strategies.py", "📈 Strategies"),
    ("pages/3_Stocks.py", "📊 Stocks"),
    ("pages/4_Leaderboards.py", "🏆 Leaderboards"),
    ("pages/5_Portfolio.py", "💼 Portfolio"),
    ("pages/6_Robustness.py", "🛡 Robustness"),
    ("pages/7_Correlation.py", "🔗 Correlation"),
    ("pages/8_Reports.py", "📄 Reports"),
    ("pages/9_Settings.py", "⚙ Settings"),
    ("pages/10_Executive_Dashboard.py", "📋 Executive Dashboard"),
]

PLATFORM_VERSION = "v4.0"


# ============================================================
# Navigation
# ============================================================


def render_navigation() -> None:
    """
    Render application navigation.
    """

    st.subheader("Navigation")

    for page, label in NAVIGATION_ITEMS:
        st.page_link(
            page,
            label=label,
        )


# ============================================================
# Status
# ============================================================


def render_status() -> None:
    """
    Render platform status.
    """

    st.divider()

    st.subheader("Platform Status")

    reports_loaded = st.session_state.get(
        "reports_loaded",
        False,
    )

    if reports_loaded:
        st.success("🟢 Reports Loaded")
    else:
        st.warning("🟡 Reports Not Loaded")

    output_folder = st.session_state.get("output_folder")

    if output_folder:
        folder = Path(output_folder)

        st.caption(f"📁 {folder.name}")

    reports = st.session_state.get(
        "reports_loaded",
        False,
    )

    st.caption(f"Reports : {'Loaded' if reports else 'Pending'}")


# ============================================================
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render sidebar footer.
    """

    st.divider()

    st.caption("Institutional Strategy Comparison Platform")

    st.caption(f"Version {PLATFORM_VERSION}")


# ============================================================
# Sidebar
# ============================================================


def render_sidebar() -> None:
    """
    Render application sidebar.
    """

    with st.sidebar:
        # ----------------------------------------------------
        # Branding
        # ----------------------------------------------------

        st.title("📊 Strategy Platform")

        st.caption("Institutional Strategy Comparison")

        st.divider()

        # ----------------------------------------------------
        # Navigation
        # ----------------------------------------------------

        render_navigation()

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        render_status()

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        render_footer()


# ============================================================
# Public API
# ============================================================

__all__ = [
    "render_sidebar",
]
