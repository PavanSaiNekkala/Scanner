"""
core/theme.py
=============

Shared Streamlit theme utilities for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

import streamlit as st

# =============================================================================
# Colors
# =============================================================================

PRIMARY = "#2563EB"

SUCCESS = "#16A34A"

WARNING = "#D97706"

ERROR = "#DC2626"

INFO = "#0EA5E9"

CARD_BACKGROUND = "#FFFFFF"

CARD_BORDER = "#E5E7EB"

TEXT_PRIMARY = "#111827"

TEXT_SECONDARY = "#6B7280"

# =============================================================================
# Theme
# =============================================================================


def apply_theme() -> None:
    """
    Apply the global application theme.
    """

    st.markdown(
        f"""
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
   Cards
----------------------------------------------------- */

div[data-testid="stMetric"] {{
    background: {CARD_BACKGROUND};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
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
    border-radius: 10px;
    border: 1px solid {CARD_BORDER};
}}

/* -----------------------------------------------------
   Expanders
----------------------------------------------------- */

details {{
    border-radius: 10px;
}}

/* -----------------------------------------------------
   Captions
----------------------------------------------------- */

.caption {{
    color: {TEXT_SECONDARY};
}}

/* -----------------------------------------------------
   Headers
----------------------------------------------------- */

h1,
h2,
h3,
h4 {{
    color: {TEXT_PRIMARY};
    font-weight: 700;
}}

</style>
""",
        unsafe_allow_html=True,
    )

# =============================================================================
# Card CSS
# =============================================================================


def inject_card_css() -> None:
    """
    Additional styling for custom cards.
    """

    st.markdown(
        """
<style>

.metric-card{
    border-radius:12px;
    padding:16px;
    border:1px solid #E5E7EB;
    background:white;
}

.metric-title{
    font-size:.85rem;
    color:#6B7280;
}

.metric-value{
    font-size:1.6rem;
    font-weight:700;
}

</style>
""",
        unsafe_allow_html=True,
    )

# =============================================================================
# Wide Layout
# =============================================================================


def use_wide_layout() -> None:
    """
    Reduce default Streamlit padding.
    """

    st.markdown(
        """
<style>

.block-container{
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

</style>
""",
        unsafe_allow_html=True,
    )

# =============================================================================
# Hide Streamlit Branding
# =============================================================================


def hide_streamlit_style() -> None:
    """
    Hide Streamlit footer and menu.
    """

    st.markdown(
        """
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
""",
        unsafe_allow_html=True,
    )