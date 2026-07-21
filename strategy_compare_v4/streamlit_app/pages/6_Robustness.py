"""
Robustness Dashboard
====================

Institutional Robustness Analysis
"""

from __future__ import annotations

import streamlit as st
from components.cards import robustness_card
from components.charts import (
    bar_chart,
    box_plot,
    dataframe,
    histogram,
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
    page_title="Robustness",
    page_icon="🛡",
    layout="wide",
)

st.title("🛡 Robustness Analysis")

st.caption("Evaluate the consistency and stability of strategy performance.")

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports from the Data Load page.")

    st.stop()

# ---------------------------------------------------------
# Load Reports
# ---------------------------------------------------------

robustness_df = get_sheet(
    st.session_state.robustness_report,
    "Robustness",
)

consistency_df = get_sheet(
    st.session_state.robustness_report,
    "Consistency",
)

summary_df = get_sheet(
    st.session_state.robustness_report,
    "Summary",
)

if robustness_df.empty:
    st.error("Robustness sheet not found.")

    st.stop()

# ---------------------------------------------------------
# KPI Summary
# ---------------------------------------------------------

robustness_card(robustness_df)

st.divider()

# ---------------------------------------------------------
# Summary Table
# ---------------------------------------------------------

if not summary_df.empty:
    st.subheader("Summary")

    dataframe(summary_df)

st.divider()

# ---------------------------------------------------------
# Robustness Table
# ---------------------------------------------------------

st.subheader("Robustness Metrics")

dataframe(robustness_df)

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

numeric = robustness_df.select_dtypes(include="number").columns.tolist()

if numeric:
    metric = st.selectbox(
        "Metric",
        numeric,
    )

    c1, c2 = st.columns(2)

    with c1:
        label = (
            "Strategy"
            if "Strategy" in robustness_df.columns
            else robustness_df.columns[0]
        )

        bar_chart(
            robustness_df.sort_values(
                metric,
                ascending=False,
            ).head(20),
            x=label,
            y=metric,
            color=metric,
            title=f"Top 20 by {metric}",
        )

    with c2:
        histogram(
            robustness_df,
            metric,
            f"{metric} Distribution",
        )

    st.divider()

    box_plot(
        robustness_df,
        metric,
        f"{metric} Box Plot",
    )

# ---------------------------------------------------------
# Consistency Analysis
# ---------------------------------------------------------

if not consistency_df.empty:
    st.divider()

    st.subheader("Consistency Analysis")

    dataframe(consistency_df)

# ---------------------------------------------------------
# Best Performers
# ---------------------------------------------------------

if "Composite Score" in robustness_df.columns:
    st.divider()

    st.subheader("Top Robust Strategies")

    top = robustness_df.sort_values(
        "Composite Score",
        ascending=False,
    ).head(10)

    dataframe(top)

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = robustness_df.to_csv(index=False)

st.download_button(
    "📥 Download Robustness Analysis",
    csv,
    "robustness.csv",
    "text/csv",
)
