"""
pages/01_Dashboard.py
=====================

Institutional Scanner Monitor

Dashboard Page
"""

from __future__ import annotations

import streamlit as st

from ui.loader import load_reports

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Dashboard",
    page_icon="🏠",
    layout="wide",
)

# =============================================================================
# Load Reports
# =============================================================================


@st.cache_data(
    show_spinner=False,
)
def get_reports():

    return load_reports()


try:

    reports = get_reports()

except Exception as exc:

    st.error(
        "Unable to load reports.",
    )

    st.exception(
        exc,
    )

    st.stop()

# =============================================================================
# Title
# =============================================================================

st.title("🏠 Dashboard")

st.caption(
    "Institutional Portfolio Monitoring Dashboard"
)

st.divider()

# =============================================================================
# KPI Cards
# =============================================================================

holdings_count = len(
    reports.holdings,
)

active_trades = len(
    reports.daily_monitor,
)

risk_metrics = len(
    reports.risk_summary,
)

execution_metrics = len(
    reports.execution_summary,
)

universe_size = 0

if not reports.daily_monitor.empty:

    universe_size = len(
        reports.daily_monitor,
    )

target_hits = 0

stop_losses = 0

if (

    not reports.daily_monitor.empty

    and

    "trade_status"

    in reports.daily_monitor.columns

):

    target_hits = int(

        (

            reports.daily_monitor[
                "trade_status"
            ]

            ==

            "TARGET HIT"

        ).sum()

    )

    stop_losses = int(

        (

            reports.daily_monitor[
                "trade_status"
            ]

            ==

            "STOP LOSS"

        ).sum()

    )

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Portfolio",

        holdings_count,

    )

with col2:

    st.metric(

        "Active Trades",

        active_trades,

    )

with col3:

    st.metric(

        "Universe",

        universe_size,

    )

col4, col5, col6 = st.columns(3)

with col4:

    st.metric(

        "Risk Metrics",

        risk_metrics,

    )

with col5:

    st.metric(

        "Target Hits",

        target_hits,

    )

with col6:

    st.metric(

        "Stop Losses",

        stop_losses,

    )

st.divider()

# =============================================================================
# Portfolio Summary
# =============================================================================

st.subheader("Portfolio Summary")

if reports.portfolio_summary.empty:

    st.info("Portfolio summary not available.")

else:

    st.dataframe(
        reports.portfolio_summary,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# =============================================================================
# Holdings Preview
# =============================================================================

st.subheader("Current Holdings")

if reports.holdings.empty:

    st.info("No holdings available.")

else:

    st.dataframe(
        reports.holdings.head(20),
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# =============================================================================
# Daily Monitor
# =============================================================================

st.subheader("Daily Monitor")

if reports.daily_monitor.empty:

    st.info("Daily monitor not available.")

else:

    st.dataframe(

        reports.daily_monitor.head(
            20,
        ),

        use_container_width=True,
        hide_index=True,

    )

    if len(
        reports.daily_monitor,
    ) > 20:

        st.caption(

            f"Showing first 20 of "
            f"{len(reports.daily_monitor)} rows."

        )

st.divider()

# =============================================================================
# Risk Summary
# =============================================================================

st.subheader("Risk Summary")

if reports.risk_summary.empty:

    st.info("Risk summary not available.")

else:

    st.dataframe(
        reports.risk_summary,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# =============================================================================
# Execution Summary
# =============================================================================

st.subheader("Execution Summary")

if reports.execution_summary.empty:

    st.info("Execution summary not available.")

else:

    st.dataframe(
        reports.execution_summary,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# =============================================================================
# Footer
# =============================================================================

st.caption(
    "Scanner Monitor • Institutional Reporting Dashboard"
)