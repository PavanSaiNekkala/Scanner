"""
scanner_monitor.core.theme
==========================

Shared Streamlit theme utilities for the
Institutional Scanner Monitor.

This module centralizes application colors and reusable CSS helpers
used across the Streamlit interface.
"""

from __future__ import annotations

from typing import Final

import streamlit as st

__all__ = [
    # Colors
    "PRIMARY",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "INFO",
    "CARD_BACKGROUND",
    "CARD_BORDER",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    # Theme
    "apply_theme",
    "inject_card_css",
    "use_wide_layout",
    "hide_streamlit_style",
]

# =============================================================================
# Theme Colors
# =============================================================================

PRIMARY: Final[str] = "#2563EB"

SUCCESS: Final[str] = "#16A34A"

WARNING: Final[str] = "#D97706"

ERROR: Final[str] = "#DC2626"

INFO: Final[str] = "#0EA5E9"

CARD_BACKGROUND: Final[str] = "#FFFFFF"

CARD_BORDER: Final[str] = "#E5E7EB"

TEXT_PRIMARY: Final[str] = "#111827"

TEXT_SECONDARY: Final[str] = "#6B7280"

# =============================================================================
# Shared CSS
# =============================================================================

_THEME_CSS = f"""
<style>

/* -----------------------------------------------------
   Main Layout
----------------------------------------------------- */

.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 100%;
}}

/* -----------------------------------------------------
   Sidebar
----------------------------------------------------- */

section[data-testid="stSidebar"] {{
    border-right: 1px solid {CARD_BORDER};
}}

/* -----------------------------------------------------
   Metric Cards
----------------------------------------------------- */

div[data-testid="stMetric"] {{
    background: {CARD_BACKGROUND};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}}

/* -----------------------------------------------------
   Buttons
----------------------------------------------------- */

.stButton > button {{
    border-radius: 8px;
    font-weight: 600;
}}

/* -----------------------------------------------------
   Tables
----------------------------------------------------- */

div[data-testid="stDataFrame"] {{
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
}}

/* -----------------------------------------------------
   Expanders
----------------------------------------------------- */

details {{
    border-radius: 10px;
}}

/* -----------------------------------------------------
   Typography
----------------------------------------------------- */

.caption {{
    color: {TEXT_SECONDARY};
}}

h1,
h2,
h3,
h4 {{
    color: {TEXT_PRIMARY};
    font-weight: 700;
}}

</style>
"""

_CARD_CSS = f"""
<style>

.metric-card {{
    background: {CARD_BACKGROUND};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 16px;
}}

.metric-title {{
    font-size: 0.85rem;
    color: {TEXT_SECONDARY};
}}

.metric-value {{
    font-size: 1.60rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

</style>
"""

_WIDE_LAYOUT_CSS = """
<style>

.block-container{
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

</style>
"""

_HIDE_STREAMLIT_CSS = """
<style>

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

</style>
"""

# =============================================================================
# Theme
# =============================================================================


def apply_theme() -> None:
    """
    Apply the application's global theme.
    """

    st.markdown(
        _THEME_CSS,
        unsafe_allow_html=True,
    )


# =============================================================================
# Card Styling
# =============================================================================


def inject_card_css() -> None:
    """
    Apply custom metric card styling.
    """

    st.markdown(
        _CARD_CSS,
        unsafe_allow_html=True,
    )


# =============================================================================
# Layout
# =============================================================================


def use_wide_layout() -> None:
    """
    Apply a wide content layout with reduced padding.
    """

    st.markdown(
        _WIDE_LAYOUT_CSS,
        unsafe_allow_html=True,
    )


# =============================================================================
# Streamlit Branding
# =============================================================================


def hide_streamlit_style() -> None:
    """
    Hide Streamlit's default menu,
    header, and footer.
    """

    st.markdown(
        _HIDE_STREAMLIT_CSS,
        unsafe_allow_html=True,
    )