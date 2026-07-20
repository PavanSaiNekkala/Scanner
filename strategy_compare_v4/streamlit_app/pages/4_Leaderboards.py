"""
Leaderboards Dashboard
======================

Institutional Leaderboards
"""

from __future__ import annotations

import streamlit as st
from components.charts import (
    bar_chart,
    dataframe,
)
from services.loader import get_sheet

st.set_page_config(
    page_title="Leaderboards",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Institutional Leaderboards")

st.caption("Overall institutional rankings across strategies and stocks.")

# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports first.")

    st.stop()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

overall_df = get_sheet(
    st.session_state.leaderboard_report,
    "Overall Leaderboard",
)

strategy_df = get_sheet(
    st.session_state.leaderboard_report,
    "Strategy Leaderboard",
)

stock_df = get_sheet(
    st.session_state.leaderboard_report,
    "Stock Leaderboard",
)

edge_df = get_sheet(
    st.session_state.leaderboard_report,
    "Edge Leaderboard",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tabs = st.tabs(
    [
        "Overall",
        "Strategies",
        "Stocks",
        "Edge",
    ]
)

# =========================================================
# Overall
# =========================================================

with tabs[0]:
    st.subheader("Overall Leaderboard")

    dataframe(overall_df)

    if not overall_df.empty:
        score_column = (
            "Composite Score"
            if "Composite Score" in overall_df.columns
            else overall_df.columns[-1]
        )

        label_column = (
            "Strategy"
            if "Strategy" in overall_df.columns
            else ("Stock" if "Stock" in overall_df.columns else overall_df.columns[0])
        )

        bar_chart(
            overall_df.head(20),
            x=label_column,
            y=score_column,
            color=score_column,
            title="Top Overall Rankings",
        )

# =========================================================
# Strategy Leaderboard
# =========================================================

with tabs[1]:
    st.subheader("Strategy Leaderboard")

    dataframe(strategy_df)

    if not strategy_df.empty:
        score_column = (
            "Composite Score"
            if "Composite Score" in strategy_df.columns
            else strategy_df.columns[-1]
        )

        bar_chart(
            strategy_df.head(20),
            x="Strategy",
            y=score_column,
            color=score_column,
            title="Top Strategies",
        )

# =========================================================
# Stock Leaderboard
# =========================================================

with tabs[2]:
    st.subheader("Stock Leaderboard")

    dataframe(stock_df)

    if not stock_df.empty:
        score_column = (
            "Institutional Score"
            if "Institutional Score" in stock_df.columns
            else stock_df.columns[-1]
        )

        bar_chart(
            stock_df.head(20),
            x="Stock",
            y=score_column,
            color=score_column,
            title="Top Stocks",
        )

# =========================================================
# Edge Leaderboard
# =========================================================

with tabs[3]:
    st.subheader("Edge Leaderboard")

    dataframe(edge_df)

    if not edge_df.empty:
        label_column = (
            "Strategy"
            if "Strategy" in edge_df.columns
            else ("Stock" if "Stock" in edge_df.columns else edge_df.columns[0])
        )

        bar_chart(
            edge_df.head(20),
            x=label_column,
            y="Edge Score",
            color="Edge Score",
            title="Highest Edge Score",
        )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

if not overall_df.empty:
    csv = overall_df.to_csv(index=False)

    st.download_button(
        "📥 Download Overall Leaderboard",
        csv,
        "overall_leaderboard.csv",
        "text/csv",
    )
