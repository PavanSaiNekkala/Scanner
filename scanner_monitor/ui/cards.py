"""
ui/cards.py
===========

Reusable UI components for the
Institutional Scanner Monitor.

This module provides standardized
dashboard components including:

- Hero banners
- KPI cards
- Status badges
- Report cards
- Empty states
- Section headers
- Dashboard summaries

Author
------
Nekkala Pavan Sai
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.theme import THEME

# =============================================================================
# Constants
# =============================================================================

CARD_RADIUS = "14px"

CARD_PADDING = "18px"

CARD_MARGIN = "12px"

CARD_BORDER = f"1px solid {THEME.BORDER}"

CARD_BACKGROUND = "white"

CARD_SHADOW = (
    "0 3px 12px "
    "rgba(0,0,0,0.08)"
)

TRANSITION = "0.20s"

# =============================================================================
# CSS Engine
# =============================================================================

_CARD_CSS = f"""
<style>

/* ==========================================================
   Generic Cards
========================================================== */

.metric-card {{

    background: {CARD_BACKGROUND};

    border: {CARD_BORDER};

    border-radius: {CARD_RADIUS};

    padding: {CARD_PADDING};

    margin-bottom: {CARD_MARGIN};

    transition: {TRANSITION};

}}

.metric-card:hover {{

    border-color: {THEME.PRIMARY};

    box-shadow: {CARD_SHADOW};

}}

/* ==========================================================
   Typography
========================================================== */

.metric-title {{

    font-size: 0.90rem;

    color: {THEME.MUTED};

    margin-bottom: 8px;

}}

.metric-value {{

    font-size: 1.80rem;

    font-weight: 700;

    color: {THEME.TEXT};

}}

.metric-subtitle {{

    color: {THEME.MUTED};

    font-size: 0.82rem;

    margin-top: 6px;

}}

.section-title {{

    font-size: 1.45rem;

    font-weight: 700;

    color: {THEME.TEXT};

}}

.section-caption {{

    color: {THEME.MUTED};

    margin-bottom: 16px;

}}

/* ==========================================================
   KPI Delta
========================================================== */

.metric-positive {{

    color: {THEME.SUCCESS};

    font-weight: 600;

}}

.metric-negative {{

    color: {THEME.DANGER};

    font-weight: 600;

}}

/* ==========================================================
   Message Cards
========================================================== */

.info-card {{

    border-left: 5px solid {THEME.INFO};

    background: #F8FCFF;

    border-radius: 10px;

    padding: 15px;

}}

.success-card {{

    border-left: 5px solid {THEME.SUCCESS};

    background: #F6FFF8;

    border-radius: 10px;

    padding: 15px;

}}

.warning-card {{

    border-left: 5px solid {THEME.WARNING};

    background: #FFFDF5;

    border-radius: 10px;

    padding: 15px;

}}

.error-card {{

    border-left: 5px solid {THEME.DANGER};

    background: #FFF6F6;

    border-radius: 10px;

    padding: 15px;

}}

.empty-card {{

    border: 2px dashed {THEME.BORDER};

    border-radius: 12px;

    padding: 36px;

    text-align: center;

    color: {THEME.MUTED};

}}

</style>
"""

# =============================================================================
# CSS Injection
# =============================================================================


def inject_card_css() -> None:
    """
    Inject reusable dashboard CSS.

    Safe to call multiple times.
    """

    st.markdown(

        _CARD_CSS,

        unsafe_allow_html=True,

    )

# =============================================================================
# Internal Rendering Engine
# =============================================================================


def _render_html(
    html: str,
) -> None:
    """
    Render raw HTML.

    All components use this helper
    instead of calling st.markdown()
    directly.
    """

    st.markdown(

        html,

        unsafe_allow_html=True,

    )

# =============================================================================
# Internal Card Renderer
# =============================================================================


def _render_card(
    body: str,
    css_class: str = "metric-card",
) -> None:
    """
    Render a generic card container.

    Parameters
    ----------
    body
        Inner HTML.

    css_class
        Card CSS class.
    """

    _render_html(

        f"""
<div class="{css_class}">

{body}

</div>
"""

    )

# =============================================================================
# Internal Section Renderer
# =============================================================================


def _render_section(
    title: str,
    caption: str | None = None,
) -> None:
    """
    Render a standardized section header.
    """

    body = f"""
<div class="section-title">

{title}

</div>
"""

    if caption:

        body += f"""

<div class="section-caption">

{caption}

</div>

"""

    _render_html(body)


# =============================================================================
# Internal Message Renderer
# =============================================================================


def _render_message_card(
    message: str,
    css_class: str,
) -> None:
    """
    Render a message card.

    Parameters
    ----------
    message
        Card message.

    css_class
        CSS class name.
    """

    _render_card(

        message,

        css_class,

    )


# =============================================================================
# Internal Metric Renderer
# =============================================================================


def _metric_body(
    title: str,
    value: Any,
    subtitle: str | None = None,
) -> str:
    """
    Build KPI body.
    """

    html = f"""
<div class="metric-title">

{title}

</div>

<div class="metric-value">

{value}

</div>
"""

    if subtitle:

        html += f"""

<div class="metric-subtitle">

{subtitle}

</div>

"""

    return html


# =============================================================================
# Internal Delta Renderer
# =============================================================================


def _delta_html(
    delta: str | None,
) -> str:
    """
    Build KPI delta.
    """

    if not delta:

        return ""

    css = (

        "metric-negative"

        if "-" in delta

        else "metric-positive"

    )

    return f"""
<div class="{css}">

{delta}

</div>
"""


# =============================================================================
# Public Section Components
# =============================================================================


def section(
    title: str,
    caption: str | None = None,
) -> None:
    """
    Display a section heading.
    """

    inject_card_css()

    _render_section(

        title,

        caption,

    )


def divider() -> None:
    """
    Standard divider.
    """

    st.divider()


# =============================================================================
# Base Card
# =============================================================================


def card(
    title: str,
    body: str,
) -> None:
    """
    Generic reusable card.
    """

    inject_card_css()

    _render_card(

        f"""

<div class="metric-title">

{title}

</div>

{body}

"""

    )

# =============================================================================
# KPI Card
# =============================================================================


def kpi_card(
    title: str,
    value: Any,
    delta: str | None = None,
) -> None:
    """
    Display a KPI card.
    """

    inject_card_css()

    body = (

        _metric_body(

            title,

            value,

        )

        +

        _delta_html(

            delta,

        )

    )

    _render_card(

        body,

    )


# =============================================================================
# KPI Grid
# =============================================================================


def kpi_grid(
    metrics: list[
        tuple[
            str,
            Any,
            str | None,
        ]
    ],
    columns: int = 4,
) -> None:
    """
    Display KPI cards
    in a responsive grid.
    """

    if not metrics:

        return

    columns = max(

        1,

        columns,

    )

    grid = st.columns(

        columns,

    )

    for index, metric in enumerate(

        metrics,

    ):

        title, value, delta = metric

        with grid[

            index % columns

        ]:

            kpi_card(

                title,

                value,

                delta,

            )


# =============================================================================
# Summary Row
# =============================================================================


def summary_row(
    metrics: (
        list[
            tuple[
                str,
                Any,
                str | None,
            ]
        ]
        |
        dict[
            str,
            Any,
        ]
    ),
) -> None:
    """
    Display dashboard
    summary metrics.
    """

    inject_card_css()

    if isinstance(

        metrics,

        dict,

    ):

        metrics = [

            (

                key,

                value,

                None,

            )

            for key, value

            in metrics.items()

        ]

    kpi_grid(

        metrics,

        columns=max(

            len(metrics),

            1,

        ),

    )


# =============================================================================
# Statistic Card
# =============================================================================


def statistic_card(
    title: str,
    value: Any,
    subtitle: str | None = None,
) -> None:
    """
    Compact metric card.
    """

    inject_card_css()

    _render_card(

        _metric_body(

            title,

            value,

            subtitle,

        )

    )


# =============================================================================
# Report Statistics
# =============================================================================


def report_statistics_card(
    statistics: dict[
        str,
        Any,
    ],
) -> None:
    """
    Display report statistics.
    """

    if not statistics:

        return

    columns = st.columns(

        len(

            statistics,

        )

    )

    for column, item in zip(

        columns,

        statistics.items(),

    ):

        key, value = item

        with column:

            statistic_card(

                key,

                value,

            )

# =============================================================================
# Message Cards
# =============================================================================


def info_card(
    message: str,
) -> None:
    """
    Display an information card.
    """

    inject_card_css()

    _render_message_card(

        message,

        "info-card",

    )


def success_card(
    message: str,
) -> None:
    """
    Display a success card.
    """

    inject_card_css()

    _render_message_card(

        message,

        "success-card",

    )


def warning_card(
    message: str,
) -> None:
    """
    Display a warning card.
    """

    inject_card_css()

    _render_message_card(

        message,

        "warning-card",

    )


def error_card(
    message: str,
) -> None:
    """
    Display an error card.
    """

    inject_card_css()

    _render_message_card(

        message,

        "error-card",

    )


# =============================================================================
# Empty State
# =============================================================================


def empty_state(
    title: str,
    message: str,
) -> None:
    """
    Display an empty-state card.
    """

    inject_card_css()

    body = f"""
<h3>

{title}

</h3>

<p>

{message}

</p>
"""

    _render_card(

        body,

        "empty-card",

    )


# =============================================================================
# Status Badge
# =============================================================================


_STATUS_COLORS = {

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

}


def status_badge(
    status: str,
) -> None:
    """
    Display a colored status badge.
    """

    inject_card_css()

    color = _STATUS_COLORS.get(

        str(status).upper(),

        THEME.INFO,

    )

    _render_html(

        f"""
<div
style="
display:inline-block;
padding:6px 14px;
border-radius:16px;
background:{color};
color:white;
font-weight:600;
font-size:0.85rem;
">

{status}

</div>
"""

    )


# =============================================================================
# Progress Card
# =============================================================================


def progress_card(
    title: str,
    value: float,
) -> None:
    """
    Display progress.
    """

    value = max(

        0.0,

        min(

            value,

            100.0,

        ),

    )

    st.subheader(

        title,

    )

    st.progress(

        value / 100.0,

        text=f"{value:.1f}%",

    )


# =============================================================================
# Loading Card
# =============================================================================


def loading_card(
    message: str = "Loading...",
) -> None:
    """
    Display loading spinner.
    """

    with st.spinner(

        message,

    ):

        st.empty()

# =============================================================================
# Hero Card
# =============================================================================


def hero_card(
    title: str,
    subtitle: str,
) -> None:
    """
    Display dashboard hero banner.
    """

    inject_card_css()

    _render_html(

        f"""
<div
style="
padding:28px;
border-radius:18px;
background:{THEME.PRIMARY};
color:white;
margin-bottom:24px;
">

<h1>

{title}

</h1>

<p>

{subtitle}

</p>

</div>
"""

    )


# =============================================================================
# Report Card
# =============================================================================


def report_card(
    report_name: str,
    records: int,
    updated: str,
) -> None:
    """
    Display report summary.
    """

    inject_card_css()

    body = f"""

<h4>

{report_name}

</h4>

<p>

Records

</p>

<div class="metric-value">

{records:,}

</div>

<hr>

<small>

Updated

<br>

{updated}

</small>

"""

    _render_card(

        body,

    )


# =============================================================================
# Download Card
# =============================================================================


def download_card(
    title: str,
    description: str,
) -> None:
    """
    Display download section card.
    """

    inject_card_css()

    body = f"""

<h3>

{title}

</h3>

<p>

{description}

</p>

"""

    _render_card(

        body,

    )


# =============================================================================
# Action Card
# =============================================================================


def action_card(
    title: str,
    description: str,
) -> None:
    """
    Display generic action card.
    """

    inject_card_css()

    body = f"""

<h4>

{title}

</h4>

<p>

{description}

</p>

"""

    _render_card(

        body,

    )


# =============================================================================
# File Card
# =============================================================================


def file_card(
    filename: str,
    filesize: str,
) -> None:
    """
    Display file information.
    """

    inject_card_css()

    body = f"""

📄

<br><br>

<b>

{filename}

</b>

<br>

<small>

{filesize}

</small>

"""

    _render_card(

        body,

    )


# =============================================================================
# Dashboard Header
# =============================================================================


def dashboard_header() -> None:
    """
    Display dashboard banner.
    """

    hero_card(

        "Institutional Scanner Monitor",

        (
            "Portfolio • Risk • "
            "Performance • Execution"
        ),

    )


# =============================================================================
# Dashboard Overview
# =============================================================================


def overview_cards(
    holdings: int,
    trades: int,
    risks: int,
    executions: int,
) -> None:
    """
    Display executive KPI row.
    """

    summary_row(

        [

            (

                "Holdings",

                holdings,

                None,

            ),

            (

                "Active Trades",

                trades,

                None,

            ),

            (

                "Risk Metrics",

                risks,

                None,

            ),

            (

                "Execution",

                executions,

                None,

            ),

        ]

    )


# =============================================================================
# Footer
# =============================================================================


def footer_card() -> None:
    """
    Display dashboard footer.
    """

    st.divider()

    st.caption(

        "Institutional Scanner Monitor"

    )

    st.caption(

        "Production Reporting Dashboard"

    )


# =============================================================================
# Legend
# =============================================================================


def legend_card() -> None:
    """
    Display dashboard legend.
    """

    st.markdown(

        """
### Legend

🟢 Positive

🔵 Active

🟡 Watch

🔴 Risk

""",

    )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    "inject_card_css",

    "section",

    "divider",

    "card",

    "kpi_card",

    "kpi_grid",

    "summary_row",

    "statistic_card",

    "report_statistics_card",

    "info_card",

    "success_card",

    "warning_card",

    "error_card",

    "empty_state",

    "status_badge",

    "progress_card",

    "loading_card",

    "hero_card",

    "report_card",

    "download_card",

    "action_card",

    "file_card",

    "dashboard_header",

    "overview_cards",

    "footer_card",

    "legend_card",

]