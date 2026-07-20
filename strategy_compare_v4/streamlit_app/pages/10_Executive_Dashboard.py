"""
Executive Dashboard
===================

Institutional Overview Dashboard
"""

from __future__ import annotations

import streamlit as st
from components.charts import (
    correlation_heatmap,
    pie_chart,
    recommendation_chart,
)
from components.metrics import executive_dashboard
from services.loader import get_sheet

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Executive Dashboard")

st.caption("Enterprise-level overview of the complete strategy ecosystem.")

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports first.")

    st.stop()

# ---------------------------------------------------------
# Load Reports
# ---------------------------------------------------------

strategy_df = get_sheet(
    st.session_state.strategy_report,
    "Strategy Rankings",
)

stock_df = get_sheet(
    st.session_state.stock_report,
    "Stock Rankings",
)

portfolio_df = get_sheet(
    st.session_state.portfolio_report,
    "Portfolio",
)

correlation_df = get_sheet(
    st.session_state.correlation_report,
    "Correlation",
)

# ---------------------------------------------------------
# Executive KPIs
# ---------------------------------------------------------

executive_dashboard(
    strategy_df,
    stock_df,
    portfolio_df,
)

st.divider()

# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Recommendation Mix")

    recommendation_chart(
        strategy_df,
    )

with right:
    if "Recommendation" in stock_df.columns and "Stock" in stock_df.columns:
        allocation = stock_df.groupby("Recommendation").size().reset_index(name="Count")

        pie_chart(
            allocation,
            names="Recommendation",
            values="Count",
            title="Stock Recommendation Mix",
        )

st.divider()

# ---------------------------------------------------------
# Correlation
# ---------------------------------------------------------

st.subheader("Diversification Overview")

correlation_heatmap(
    correlation_df,
    "Correlation Matrix",
)

st.divider()

# ---------------------------------------------------------
# Top Strategies
# ---------------------------------------------------------

st.subheader("Top 10 Strategies")

st.dataframe(
    strategy_df.sort_values(
        "Composite Score",
        ascending=False,
    ).head(10),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ---------------------------------------------------------
# Top Stocks
# ---------------------------------------------------------

st.subheader("Top 10 Stocks")

st.dataframe(
    stock_df.sort_values(
        "Institutional Score",
        ascending=False,
    ).head(10),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ---------------------------------------------------------
# Portfolio Snapshot
# ---------------------------------------------------------

st.subheader("Portfolio Snapshot")

st.dataframe(
    portfolio_df,
    use_container_width=True,
    hide_index=True,
)
