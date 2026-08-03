"""
ui.theme
========

Institutional Theme Engine

Centralized visual theme for the
Scanner Monitor application.

Responsibilities
----------------
- Color palette
- Typography
- Layout
- CSS injection
- Plotly styling
- Formatting helpers
"""

from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# Theme Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class Theme:
    """
    Institutional design system.
    """

    # -------------------------------------------------------------------------
    # Brand Colors
    # -------------------------------------------------------------------------

    PRIMARY: str = "#2563EB"

    SECONDARY: str = "#1E293B"

    ACCENT: str = "#0EA5E9"

    # -------------------------------------------------------------------------
    # Semantic Colors
    # -------------------------------------------------------------------------

    SUCCESS: str = "#16A34A"

    WARNING: str = "#F59E0B"

    DANGER: str = "#DC2626"

    INFO: str = "#0284C7"

    # -------------------------------------------------------------------------
    # Neutral Palette
    # -------------------------------------------------------------------------

    BACKGROUND: str = "#F8FAFC"

    CARD: str = "#FFFFFF"

    BORDER: str = "#CBD5E1"

    GRID: str = "#E2E8F0"

    TEXT: str = "#1E293B"

    MUTED: str = "#64748B"

    DARK: str = "#0F172A"

    LIGHT: str = "#F8FAFC"

    # -------------------------------------------------------------------------
    # Typography
    # -------------------------------------------------------------------------

    FONT_FAMILY: str = (

        "Inter, "

        "Segoe UI, "

        "Arial, "

        "sans-serif"

    )

    TITLE_SIZE: int = 30

    HEADER_SIZE: int = 22

    BODY_SIZE: int = 14

    SMALL_SIZE: int = 12

    # -------------------------------------------------------------------------
    # Cards
    # -------------------------------------------------------------------------

    CARD_RADIUS: str = "14px"

    CARD_PADDING: str = "18px"

    CARD_SHADOW: str = (

        "0 3px 12px "

        "rgba(0,0,0,0.08)"

    )

    # -------------------------------------------------------------------------
    # Tables
    # -------------------------------------------------------------------------

    TABLE_RADIUS: str = "10px"

    TABLE_PADDING: str = "10px"


THEME = Theme()

# =============================================================================
# Layout Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class Layout:
    """
    Shared layout configuration.
    """

    page_padding_top: str = "1.20rem"

    page_padding_bottom: str = "2.00rem"

    metric_radius: str = "12px"

    metric_padding: str = "18px"

    sidebar_width: str = "320px"

    chart_height: int = 430

    animation_speed: str = "0.20s"


LAYOUT = Layout()

# =============================================================================
# Plotly Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class PlotlyTheme:
    """
    Shared Plotly configuration.
    """

    template: str = "plotly_white"

    font_family: str = THEME.FONT_FAMILY

    font_size: int = 13

    margin_left: int = 20

    margin_right: int = 20

    margin_top: int = 50

    margin_bottom: int = 20

    legend_orientation: str = "h"


PLOTLY = PlotlyTheme()

# =============================================================================
# CSS Engine
# =============================================================================

_THEME_CSS = f"""
<style>

/* ==========================================================
   Layout
========================================================== */

.block-container {{

    padding-top:{LAYOUT.page_padding_top};

    padding-bottom:{LAYOUT.page_padding_bottom};

}}

/* ==========================================================
   Typography
========================================================== */

html,
body,
[class*="css"] {{

    font-family:{THEME.FONT_FAMILY};

}}

h1,
h2,
h3,
h4 {{

    color:{THEME.TEXT};

}}

/* ==========================================================
   Metric Cards
========================================================== */

div[data-testid="metric-container"] {{

    background:{THEME.CARD};

    border:1px solid {THEME.BORDER};

    border-radius:{LAYOUT.metric_radius};

    padding:{LAYOUT.metric_padding};

    transition:{LAYOUT.animation_speed};

}}

div[data-testid="metric-container"]:hover {{

    border-color:{THEME.PRIMARY};

    box-shadow:{THEME.CARD_SHADOW};

}}

/* ==========================================================
   Tables
========================================================== */

thead tr th {{

    background:{THEME.LIGHT};

}}

tbody tr:hover {{

    background:#F8FAFC;

}}

/* ==========================================================
   Streamlit
========================================================== */

#MainMenu {{

    visibility:hidden;

}}

footer {{

    visibility:hidden;

}}

</style>
"""

# =============================================================================
# Theme Application
# =============================================================================


def apply_theme() -> None:
    """
    Apply the institutional theme.

    Safe to call multiple times.
    """

    st.markdown(

        _THEME_CSS,

        unsafe_allow_html=True,

    )

# =============================================================================
# Formatting Engine
# =============================================================================


def safe_number(
    value: object,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value
    to float.
    """

    try:

        if value is None:

            return default

        return float(

            value,

        )

    except (

        TypeError,

        ValueError,

    ):

        return default


def format_number(
    value: object,
    digits: int = 2,
) -> str:
    """
    Format numeric values.
    """

    return (

        f"{safe_number(value):,.{digits}f}"

    )


def format_integer(
    value: object,
) -> str:
    """
    Format integer values.
    """

    return (

        f"{int(safe_number(value)):,.0f}"

    )


def format_currency(
    value: object,
    *,
    symbol: str = "₹",
    digits: int = 2,
) -> str:
    """
    Format currency.
    """

    return (

        f"{symbol}"

        f"{safe_number(value):,.{digits}f}"

    )


def format_percent(
    value: object,
    digits: int = 2,
) -> str:
    """
    Format percentage.
    """

    return (

        f"{safe_number(value):.{digits}f}%"

    )


def format_ratio(
    value: object,
    digits: int = 2,
) -> str:
    """
    Format ratios.
    """

    return (

        f"{safe_number(value):.{digits}f}"

    )


# =============================================================================
# Compact Formatting
# =============================================================================


def compact_number(
    value: object,
) -> str:
    """
    Convert large values into
    compact notation.

    Examples
    --------
    1250 -> 1.25K
    2500000 -> 2.50M
    """

    number = safe_number(

        value,

    )

    absolute = abs(

        number,

    )

    if absolute >= 1_000_000_000:

        return (

            f"{number / 1_000_000_000:.2f}B"

        )

    if absolute >= 1_000_000:

        return (

            f"{number / 1_000_000:.2f}M"

        )

    if absolute >= 1_000:

        return (

            f"{number / 1_000:.2f}K"

        )

    return format_number(

        number,

    )


def compact_currency(
    value: object,
    *,
    symbol: str = "₹",
) -> str:
    """
    Compact currency formatter.
    """

    return (

        symbol

        +

        compact_number(

            value,

        )

    )


# =============================================================================
# Delta Formatting
# =============================================================================


def format_delta(
    value: object,
    *,
    digits: int = 2,
    include_sign: bool = True,
    suffix: str = "%",
) -> str:
    """
    Format KPI deltas.
    """

    number = safe_number(

        value,

    )

    sign = ""

    if include_sign:

        if number > 0:

            sign = "+"

        elif number < 0:

            sign = "-"

    return (

        f"{sign}"

        f"{abs(number):.{digits}f}"

        f"{suffix}"

    )


# =============================================================================
# Text Formatting
# =============================================================================


def title_case(
    text: str,
) -> str:
    """
    Convert text into
    title case.
    """

    return (

        str(text)

        .replace(

            "_",

            " ",

        )

        .title()

    )


def sentence_case(
    text: str,
) -> str:
    """
    Convert text into
    sentence case.
    """

    text = str(

        text,

    ).strip()

    if not text:

        return ""

    return (

        text[0].upper()

        +

        text[1:]

    )


# =============================================================================
# Theme Information
# =============================================================================


def theme_colors() -> dict[str, str]:
    """
    Return the institutional
    color palette.
    """

    return {

        "Primary":

            THEME.PRIMARY,

        "Secondary":

            THEME.SECONDARY,

        "Success":

            THEME.SUCCESS,

        "Warning":

            THEME.WARNING,

        "Danger":

            THEME.DANGER,

        "Info":

            THEME.INFO,

        "Background":

            THEME.BACKGROUND,

        "Card":

            THEME.CARD,

        "Border":

            THEME.BORDER,

        "Text":

            THEME.TEXT,

        "Muted":

            THEME.MUTED,

    }

# =============================================================================
# Status Color Engine
# =============================================================================


STATUS_COLORS = {

    "ACTIVE":

        THEME.INFO,

    "BUY":

        THEME.SUCCESS,

    "SELL":

        THEME.DANGER,

    "WATCH":

        THEME.WARNING,

    "TARGET HIT":

        THEME.SUCCESS,

    "STOP HIT":

        THEME.DANGER,

    "EXIT":

        THEME.WARNING,

    "EXIT DUE":

        THEME.WARNING,

    "OPEN":

        THEME.INFO,

    "CLOSED":

        THEME.SECONDARY,

}


RISK_COLORS = {

    "LOW":

        THEME.SUCCESS,

    "MEDIUM":

        THEME.WARNING,

    "HIGH":

        THEME.DANGER,

    "CRITICAL":

        THEME.DANGER,

}


RETURN_COLORS = {

    "POSITIVE":

        THEME.SUCCESS,

    "NEGATIVE":

        THEME.DANGER,

    "NEUTRAL":

        THEME.INFO,

}

# =============================================================================
# Color Helpers
# =============================================================================


def status_color(
    status: object,
) -> str:
    """
    Return status color.
    """

    return STATUS_COLORS.get(

        str(

            status,

        ).upper(),

        THEME.INFO,

    )


def risk_color(
    risk: object,
) -> str:
    """
    Return risk color.
    """

    return RISK_COLORS.get(

        str(

            risk,

        ).upper(),

        THEME.INFO,

    )


def return_color(
    value: object,
) -> str:
    """
    Return performance color.
    """

    number = safe_number(

        value,

    )

    if number > 0:

        return THEME.SUCCESS

    if number < 0:

        return THEME.DANGER

    return THEME.INFO


def boolean_color(
    value: bool,
) -> str:
    """
    Boolean color helper.
    """

    return (

        THEME.SUCCESS

        if value

        else THEME.DANGER

    )


# =============================================================================
# Palette Helpers
# =============================================================================


def primary_palette() -> list[str]:
    """
    Institutional palette.
    """

    return [

        THEME.PRIMARY,

        THEME.INFO,

        THEME.SUCCESS,

        THEME.WARNING,

        THEME.DANGER,

    ]


def qualitative_palette() -> list[str]:
    """
    Qualitative colors.
    """

    return [

        THEME.PRIMARY,

        THEME.SECONDARY,

        THEME.INFO,

        THEME.SUCCESS,

        THEME.WARNING,

        THEME.DANGER,

    ]


def sequential_palette() -> list[str]:
    """
    Sequential colors.
    """

    return [

        THEME.LIGHT,

        "#DBEAFE",

        "#93C5FD",

        "#60A5FA",

        THEME.PRIMARY,

    ]


# =============================================================================
# Plotly Theme
# =============================================================================


def apply_plotly_theme(
    figure: go.Figure,
) -> go.Figure:
    """
    Apply institutional
    Plotly styling.
    """

    figure.update_layout(

        template=PLOTLY.template,

        colorway=primary_palette(),

        font=dict(

            family=PLOTLY.font_family,

            size=PLOTLY.font_size,

            color=THEME.TEXT,

        ),

        paper_bgcolor=THEME.CARD,

        plot_bgcolor=THEME.CARD,

        margin=dict(

            l=PLOTLY.margin_left,

            r=PLOTLY.margin_right,

            t=PLOTLY.margin_top,

            b=PLOTLY.margin_bottom,

        ),

        legend=dict(

            orientation=PLOTLY.legend_orientation,

            yanchor="bottom",

            y=1.02,

            xanchor="right",

            x=1,

        ),

    )

    figure.update_xaxes(

        showgrid=True,

        gridcolor=THEME.GRID,

        zeroline=False,

    )

    figure.update_yaxes(

        showgrid=True,

        gridcolor=THEME.GRID,

        zeroline=False,

    )

    return figure


# =============================================================================
# Figure Helpers
# =============================================================================


def styled_figure(
    figure: go.Figure,
) -> go.Figure:
    """
    Apply complete
    institutional styling.
    """

    return apply_plotly_theme(

        figure,

    )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    "THEME",

    "LAYOUT",

    "PLOTLY",

    "STATUS_COLORS",

    "RISK_COLORS",

    "RETURN_COLORS",

    "apply_theme",

    "safe_number",

    "format_number",

    "format_integer",

    "format_currency",

    "format_percent",

    "format_ratio",

    "compact_number",

    "compact_currency",

    "format_delta",

    "title_case",

    "sentence_case",

    "theme_colors",

    "status_color",

    "risk_color",

    "return_color",

    "boolean_color",

    "primary_palette",

    "qualitative_palette",

    "sequential_palette",

    "apply_plotly_theme",

    "styled_figure",

]