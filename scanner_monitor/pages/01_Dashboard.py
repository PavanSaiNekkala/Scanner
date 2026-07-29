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

reports = load_reports()

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

holdings_count = len(reports.holdings)

active_trades = len(reports.daily_monitor)

risk_metrics = len(reports.risk_summary)

execution_metrics = len(reports.execution_summary)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        label="Holdings",
        value=holdings_count,
    )

with col2:

    st.metric(
        label="Active Trades",
        value=active_trades,
    )

with col3:

    st.metric(
        label="Risk Metrics",
        value=risk_metrics,
    )

with col4:

    st.metric(
        label="Execution Metrics",
        value=execution_metrics,
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
        reports.daily_monitor,
        use_container_width=True,
        hide_index=True,
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