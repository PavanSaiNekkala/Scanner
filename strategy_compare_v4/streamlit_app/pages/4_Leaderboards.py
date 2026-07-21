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
from themes import apply_theme

st.set_page_config(
    page_title="Strategies",
    page_icon="📈",
    layout="wide",
)
apply_theme()

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
    "Overall",
)

strategy_df = get_sheet(
    st.session_state.leaderboard_report,
    "Strategies",
)

stock_df = get_sheet(
    st.session_state.leaderboard_report,
    "Stocks",
)

edge_df = get_sheet(
    st.session_state.leaderboard_report,
    "Edge",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
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

with tab1:
    st.subheader("Overall Leaderboard")

    dataframe(overall_df)

    if not overall_df.empty:
        x_col = (
            "Strategy"
            if "Strategy" in overall_df.columns
            else ("Stock" if "Stock" in overall_df.columns else overall_df.columns[0])
        )

        y_col = (
            "Composite Score"
            if "Composite Score" in overall_df.columns
            else (
                "Composite"
                if "Composite" in overall_df.columns
                else overall_df.columns[-1]
            )
        )

        bar_chart(
            overall_df.head(20),
            x=x_col,
            y=y_col,
            color=y_col,
            title="Top Overall Rankings",
        )

# =========================================================
# Strategy Leaderboard
# =========================================================

with tab2:
    st.subheader("Strategy Leaderboard")

    dataframe(strategy_df)

    if not strategy_df.empty:
        y_col = (
            "Composite"
            if "Composite" in strategy_df.columns
            else (
                "Composite Score"
                if "Composite Score" in strategy_df.columns
                else strategy_df.columns[-1]
            )
        )

        bar_chart(
            strategy_df.head(20),
            x="Strategy",
            y=y_col,
            color=y_col,
            title="Top Strategies",
        )

# =========================================================
# Stock Leaderboard
# =========================================================

with tab3:
    st.subheader("Stock Leaderboard")

    dataframe(stock_df)

    if not stock_df.empty:
        y_col = (
            "Composite Score"
            if "Composite Score" in stock_df.columns
            else (
                "Institutional Score"
                if "Institutional Score" in stock_df.columns
                else stock_df.columns[-1]
            )
        )

        bar_chart(
            stock_df.head(20),
            x="Stock",
            y=y_col,
            color=y_col,
            title="Top Stocks",
        )

# =========================================================
# Edge Leaderboard
# =========================================================

with tab4:
    st.subheader("Edge Leaderboard")

    dataframe(edge_df)

    if not edge_df.empty:
        x_col = (
            "Strategy"
            if "Strategy" in edge_df.columns
            else ("Stock" if "Stock" in edge_df.columns else edge_df.columns[0])
        )

        bar_chart(
            edge_df.head(20),
            x=x_col,
            y="Edge Score",
            color="Edge Score",
            title="Highest Edge Score",
        )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

if not overall_df.empty:
    st.download_button(
        "📥 Download Overall Leaderboard",
        overall_df.to_csv(index=False),
        "overall_leaderboard.csv",
        "text/csv",
    )
