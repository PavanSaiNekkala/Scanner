"""
ui/theme.py
===========

Institutional Theme Utilities

Provides a centralized theme configuration for the
Scanner Monitor Streamlit application.

Features
--------
- Institutional color palette
- Status colors
- Risk colors
- Plotly layout defaults
- CSS injection
- Metric formatting
- Number formatting

Author
------
Nekkala Pavan Sai
"""

from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# Theme Configuration
# =============================================================================


@dataclass(frozen=True)
class Theme:
    """
    Institutional color palette.
    """

    PRIMARY: str = "#2563EB"

    SECONDARY: str = "#1E293B"

    SUCCESS: str = "#16A34A"

    WARNING: str = "#F59E0B"

    DANGER: str = "#DC2626"

    INFO: str = "#0EA5E9"

    LIGHT: str = "#F8FAFC"

    DARK: str = "#0F172A"

    BORDER: str = "#CBD5E1"

    CARD: str = "#FFFFFF"

    TEXT: str = "#1E293B"

    MUTED: str = "#64748B"

    GRID: str = "#E2E8F0"


THEME = Theme()

# =============================================================================
# Status Colors
# =============================================================================

STATUS_COLORS = {

    "ACTIVE": THEME.INFO,

    "TARGET HIT": THEME.SUCCESS,

    "STOP HIT": THEME.DANGER,

    "EXIT": THEME.WARNING,

    "EXIT DUE": THEME.WARNING,

    "BUY": THEME.SUCCESS,

    "SELL": THEME.DANGER,

    "WATCH": THEME.WARNING,

}

# =============================================================================
# Risk Colors
# =============================================================================

RISK_COLORS = {

    "LOW": THEME.SUCCESS,

    "MEDIUM": THEME.WARNING,

    "HIGH": THEME.DANGER,

}

# =============================================================================
# Return Colors
# =============================================================================

RETURN_COLORS = {

    "POSITIVE": THEME.SUCCESS,

    "NEGATIVE": THEME.DANGER,

    "NEUTRAL": THEME.INFO,

}

# =============================================================================
# CSS
# =============================================================================


def apply_theme() -> None:
    """
    Apply application styling.
    """

    st.markdown(
        f"""
<style>

.block-container{{
    padding-top:1.2rem;
    padding-bottom:2rem;
}}

h1,h2,h3{{
    color:{THEME.TEXT};
}}

div[data-testid="metric-container"]{{
    border:1px solid {THEME.BORDER};
    border-radius:12px;
    padding:18px;
    background:white;
}}

div[data-testid="metric-container"]:hover{{
    border-color:{THEME.PRIMARY};
}}

thead tr th{{
    background:{THEME.LIGHT};
}}

footer{{
    visibility:hidden;
}}

#MainMenu{{
    visibility:hidden;
}}

</style>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Formatting Helpers
# =============================================================================


def format_currency(
    value: float,
) -> str:
    """
    Format currency.
    """

    return f"${value:,.2f}"


def format_percent(
    value: float,
    digits: int = 2,
) -> str:
    """
    Format percentage.
    """

    return f"{value:.{digits}f}%"


def format_number(
    value: float,
    digits: int = 2,
) -> str:
    """
    Format numeric values.
    """

    return f"{value:,.{digits}f}"


# =============================================================================
# Color Helpers
# =============================================================================


def status_color(
    status: str,
) -> str:
    """
    Return status color.
    """

    return STATUS_COLORS.get(
        str(status).upper(),
        THEME.INFO,
    )


def risk_color(
    risk: str,
) -> str:
    """
    Return risk color.
    """

    return RISK_COLORS.get(
        str(risk).upper(),
        THEME.INFO,
    )


def return_color(
    value: float,
) -> str:
    """
    Return color based on return.
    """

    if value > 0:

        return THEME.SUCCESS

    if value < 0:

        return THEME.DANGER

    return THEME.INFO


# =============================================================================
# Plotly Theme
# =============================================================================


def apply_plotly_theme(
    fig: go.Figure,
) -> go.Figure:
    """
    Apply institutional Plotly styling.
    """

    fig.update_layout(

        template="plotly_white",

        font=dict(

            family="Arial",

            size=13,

            color=THEME.TEXT,

        ),

        paper_bgcolor="white",

        plot_bgcolor="white",

        margin=dict(

            l=20,

            r=20,

            t=50,

            b=20,

        ),

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="right",

            x=1,

        ),

    )

    fig.update_xaxes(

        showgrid=True,

        gridcolor=THEME.GRID,

        zeroline=False,

    )

    fig.update_yaxes(

        showgrid=True,

        gridcolor=THEME.GRID,

        zeroline=False,

    )

    return fig


# =============================================================================
# Theme Information
# =============================================================================


def theme_summary() -> dict[str, str]:
    """
    Return theme colors.
    """

    return {

        "Primary": THEME.PRIMARY,

        "Success": THEME.SUCCESS,

        "Warning": THEME.WARNING,

        "Danger": THEME.DANGER,

        "Info": THEME.INFO,

        "Dark": THEME.DARK,

    }