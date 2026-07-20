"""
Portfolio Dashboard
===================

Institutional Portfolio Analytics
"""

from __future__ import annotations

import streamlit as st
from components.cards import (
    portfolio_summary_card,
)
from components.charts import (
    bar_chart,
    dataframe,
    histogram,
    pie_chart,
)
from services.loader import get_sheet

st.set_page_config(
    page_title="Portfolio",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Institutional Portfolio")

st.caption("Institutional Portfolio Construction and Allocation")

# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports first.")

    st.stop()

# ---------------------------------------------------------
# Load Portfolio
# ---------------------------------------------------------

portfolio_df = get_sheet(
    st.session_state.portfolio_report,
    "Portfolio",
)

summary_df = get_sheet(
    st.session_state.portfolio_report,
    "Portfolio Summary",
)

if portfolio_df.empty:
    st.error("Portfolio sheet not found.")

    st.stop()

# ---------------------------------------------------------
# Summary Cards
# ---------------------------------------------------------

portfolio_summary_card(portfolio_df)

st.divider()

# ---------------------------------------------------------
# Portfolio Summary
# ---------------------------------------------------------

if not summary_df.empty:
    st.subheader("Portfolio Summary")

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ---------------------------------------------------------
# Portfolio Table
# ---------------------------------------------------------

st.subheader("Portfolio Holdings")

dataframe(portfolio_df)

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

left, right = st.columns(2)

# ---------------------------------------------------------
# Allocation
# ---------------------------------------------------------

with left:
    if "Weight %" in portfolio_df.columns:
        pie_chart(
            portfolio_df,
            names="Stock",
            values="Weight %",
            title="Portfolio Allocation",
        )

# ---------------------------------------------------------
# Expected Return
# ---------------------------------------------------------

with right:
    if "Expected Return %" in portfolio_df.columns:
        bar_chart(
            portfolio_df,
            x="Stock",
            y="Expected Return %",
            color="Expected Return %",
            title="Expected Return",
        )

# ---------------------------------------------------------

left, right = st.columns(2)

with left:
    if "Weight %" in portfolio_df.columns:
        histogram(
            portfolio_df,
            "Weight %",
            "Weight Distribution",
        )

with right:
    score_column = None

    for col in [
        "Institutional Score",
        "Composite Score",
        "Edge Score",
    ]:
        if col in portfolio_df.columns:
            score_column = col
            break

    if score_column:
        bar_chart(
            portfolio_df,
            x="Stock",
            y=score_column,
            color=score_column,
            title=f"{score_column} by Holding",
        )

# ---------------------------------------------------------
# Top Holdings
# ---------------------------------------------------------

st.divider()

st.subheader("Top Holdings")

if "Weight %" in portfolio_df.columns:
    top = portfolio_df.sort_values(
        "Weight %",
        ascending=False,
    ).head(10)

    dataframe(top)

# ---------------------------------------------------------
# Portfolio Statistics
# ---------------------------------------------------------

st.divider()

st.subheader("Portfolio Statistics")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Holdings",
        len(portfolio_df),
    )

with c2:
    if "Weight %" in portfolio_df.columns:
        st.metric(
            "Total Weight",
            f"{portfolio_df['Weight %'].sum():.2f}%",
        )

with c3:
    if "Expected Return %" in portfolio_df.columns:
        st.metric(
            "Average Return",
            f"{portfolio_df['Expected Return %'].mean():.2f}%",
        )

with c4:
    if "Institutional Score" in portfolio_df.columns:
        st.metric(
            "Average Score",
            f"{portfolio_df['Institutional Score'].mean():.2f}",
        )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = portfolio_df.to_csv(index=False)

st.download_button(
    "📥 Download Portfolio",
    csv,
    "institutional_portfolio.csv",
    "text/csv",
)
