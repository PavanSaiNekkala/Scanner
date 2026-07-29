"""
ui.cards
========

Reusable Streamlit UI cards for the
Institutional Scanner Monitor.

Author
------
Nekkala Pavan Sai
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.theme import THEME

# =============================================================================
# CSS
# =============================================================================


def inject_card_css() -> None:
    """
    Inject reusable card styling.
    """

    st.markdown(
        f"""
<style>

.metric-card {{
    background:white;
    border:1px solid {THEME.BORDER};
    border-radius:14px;
    padding:18px;
    margin-bottom:12px;
    transition:0.2s;
}}

.metric-card:hover {{
    border-color:{THEME.PRIMARY};
    box-shadow:0 3px 12px rgba(0,0,0,0.08);
}}

.metric-title {{
    font-size:0.90rem;
    color:{THEME.MUTED};
    margin-bottom:8px;
}}

.metric-value {{
    font-size:1.8rem;
    font-weight:700;
    color:{THEME.TEXT};
}}

.metric-delta-positive {{
    color:{THEME.SUCCESS};
    font-weight:600;
}}

.metric-delta-negative {{
    color:{THEME.DANGER};
    font-weight:600;
}}

.info-card {{
    border-left:5px solid {THEME.INFO};
    background:#F8FCFF;
    padding:15px;
    border-radius:10px;
}}

.success-card {{
    border-left:5px solid {THEME.SUCCESS};
    background:#F6FFF8;
    padding:15px;
    border-radius:10px;
}}

.warning-card {{
    border-left:5px solid {THEME.WARNING};
    background:#FFFDF5;
    padding:15px;
    border-radius:10px;
}}

.error-card {{
    border-left:5px solid {THEME.DANGER};
    background:#FFF6F6;
    padding:15px;
    border-radius:10px;
}}

.empty-card {{
    border:2px dashed {THEME.BORDER};
    border-radius:10px;
    padding:35px;
    text-align:center;
    color:{THEME.MUTED};
}}

.section-title {{
    font-size:1.45rem;
    font-weight:700;
    color:{THEME.TEXT};
}}

.section-caption {{
    color:{THEME.MUTED};
    margin-bottom:15px;
}}

</style>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Section Header
# =============================================================================


def section(
    title: str,
    caption: str | None = None,
) -> None:
    """
    Render a section title.
    """

    st.markdown(
        f"""
<div class="section-title">
{title}
</div>
""",
        unsafe_allow_html=True,
    )

    if caption:

        st.markdown(
            f"""
<div class="section-caption">
{caption}
</div>
""",
            unsafe_allow_html=True,
        )


def divider() -> None:
    """
    Styled divider.
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
    Generic card.
    """

    st.markdown(
        f"""
<div class="metric-card">

<div class="metric-title">
{title}
</div>

{body}

</div>
""",
        unsafe_allow_html=True,
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
    KPI metric card.
    """

    delta_html = ""

    if delta:

        css = (
            "metric-delta-positive"
            if "-" not in delta
            else "metric-delta-negative"
        )

        delta_html = (
            f'<div class="{css}">{delta}</div>'
        )

    card(
        title,
        f"""
<div class="metric-value">
{value}
</div>

{delta_html}
""",
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
    Display KPI cards in a grid.
    """

    cols = st.columns(columns)

    for i, metric in enumerate(metrics):

        title, value, delta = metric

        with cols[i % columns]:

            kpi_card(
                title,
                value,
                delta,
            )


# =============================================================================
# Information Cards
# =============================================================================


def info_card(
    message: str,
) -> None:
    """
    Blue information card.
    """

    st.markdown(
        f"""
<div class="info-card">

{message}

</div>
""",
        unsafe_allow_html=True,
    )


def success_card(
    message: str,
) -> None:
    """
    Success card.
    """

    st.markdown(
        f"""
<div class="success-card">

{message}

</div>
""",
        unsafe_allow_html=True,
    )


def warning_card(
    message: str,
) -> None:
    """
    Warning card.
    """

    st.markdown(
        f"""
<div class="warning-card">

{message}

</div>
""",
        unsafe_allow_html=True,
    )


def error_card(
    message: str,
) -> None:
    """
    Error card.
    """

    st.markdown(
        f"""
<div class="error-card">

{message}

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Empty State
# =============================================================================


def empty_state(
    title: str,
    message: str,
) -> None:
    """
    Render an empty state.
    """

    st.markdown(
        f"""
<div class="empty-card">

<h3>{title}</h3>

<p>{message}</p>

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Dashboard Summary
# =============================================================================

def summary_row(
    metrics,
) -> None:
    """
    Render dashboard KPI row.

    Accepts either:

    - list[tuple(title, value, delta)]
    - dict[str, Any]
    """

    inject_card_css()

    if isinstance(metrics, dict):

        metrics = [

            (
                title,
                value,
                None,
            )

            for title, value in metrics.items()

        ]

    kpi_grid(
        metrics,
        columns=max(len(metrics), 1),
    )

# =============================================================================
# Status Badge
# =============================================================================

def status_badge(
    status: str,
) -> None:
    """
    Display a colored status badge.
    """

    colors = {

        "ACTIVE": THEME.INFO,

        "BUY": THEME.SUCCESS,

        "SELL": THEME.DANGER,

        "WATCH": THEME.WARNING,

        "TARGET HIT": THEME.SUCCESS,

        "STOP HIT": THEME.DANGER,

        "EXIT": THEME.WARNING,

        "EXIT DUE": THEME.WARNING,

    }

    color = colors.get(
        str(status).upper(),
        THEME.INFO,
    )

    st.markdown(
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
""",
        unsafe_allow_html=True,
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
    Compact statistic card.
    """

    subtitle_html = ""

    if subtitle:

        subtitle_html = (
            f"<small>{subtitle}</small>"
        )

    st.markdown(
        f"""
<div class="metric-card">

<div class="metric-title">
{title}
</div>

<div class="metric-value">
{value}
</div>

{subtitle_html}

</div>
""",
        unsafe_allow_html=True,
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
    Summary card for report files.
    """

    st.markdown(
        f"""
<div class="metric-card">

<h4>{report_name}</h4>

<p>
Records
</p>

<h2>{records}</h2>

<hr>

<small>

Updated

<br>

{updated}

</small>

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Download Card
# =============================================================================


def download_card(
    title: str,
    description: str,
) -> None:
    """
    Header displayed above download buttons.
    """

    st.markdown(
        f"""
<div class="metric-card">

<h3>
{title}
</h3>

<p>
{description}
</p>

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Progress Card
# =============================================================================


def progress_card(
    title: str,
    value: float,
) -> None:
    """
    Progress indicator.
    """

    st.subheader(title)

    st.progress(
        min(
            max(value / 100.0, 0.0),
            1.0,
        ),
        text=f"{value:.1f}%",
    )


# =============================================================================
# Hero Card
# =============================================================================


def hero_card(
    title: str,
    subtitle: str,
) -> None:
    """
    Dashboard hero banner.
    """

    st.markdown(
        f"""
<div
style="
padding:25px;
border-radius:18px;
background:{THEME.PRIMARY};
color:white;
margin-bottom:25px;
">

<h1>

{title}

</h1>

<p>

{subtitle}

</p>

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Loading Card
# =============================================================================


def loading_card(
    message: str = "Loading...",
) -> None:
    """
    Loading placeholder.
    """

    with st.spinner(message):

        st.empty()


# =============================================================================
# Action Card
# =============================================================================


def action_card(
    title: str,
    description: str,
) -> None:
    """
    Generic action card.
    """

    st.markdown(
        f"""
<div class="metric-card">

<h4>

{title}

</h4>

<p>

{description}

</p>

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# File Card
# =============================================================================


def file_card(
    filename: str,
    filesize: str,
) -> None:
    """
    File information card.
    """

    st.markdown(
        f"""
<div class="metric-card">

📄

<b>

{filename}

</b>

<br>

<small>

{filesize}

</small>

</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Report Statistics
# =============================================================================


def report_statistics_card(
    statistics: dict[str, Any],
) -> None:
    """
    Display report statistics.
    """

    cols = st.columns(
        len(statistics),
    )

    for column, item in zip(
        cols,
        statistics.items(),
    ):

        key, value = item

        with column:

            statistic_card(
                key,
                value,
            )


# =============================================================================
# Footer
# =============================================================================


def footer_card() -> None:
    """
    Application footer.
    """

    st.markdown("---")

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
    Dashboard legend.
    """

    st.markdown(
        """
### Legend

🟢 Positive

🔵 Active

🟡 Watch

🔴 Risk
"""
    )


# =============================================================================
# Dashboard Header
# =============================================================================


def dashboard_header() -> None:
    """
    Dashboard title.
    """

    hero_card(

        "Institutional Scanner Monitor",

        (
            "Portfolio • Risk • "
            "Execution • Performance"
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
    Dashboard KPI cards.
    """

    summary_row(

        [

            ("Holdings", holdings, None),

            ("Active Trades", trades, None),

            ("Risk Metrics", risks, None),

            (
                "Execution Metrics",
                executions,
                None,
            ),

        ],

    )