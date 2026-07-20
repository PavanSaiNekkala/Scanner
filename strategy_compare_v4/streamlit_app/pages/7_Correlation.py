"""
Correlation Dashboard
=====================

Institutional Correlation & Diversification Analytics
"""

from __future__ import annotations

import streamlit as st
from components.charts import (
    correlation_heatmap,
    dataframe,
    histogram,
)
from services.loader import get_sheet

st.set_page_config(
    page_title="Correlation",
    page_icon="🔗",
    layout="wide",
)

st.title("🔗 Correlation & Diversification")

st.caption("Analyze strategy diversification and correlation.")

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports first.")

    st.stop()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

correlation_df = get_sheet(
    st.session_state.correlation_report,
    "Correlation",
)

diversification_df = get_sheet(
    st.session_state.correlation_report,
    "Diversification",
)

if correlation_df.empty:
    st.error("Correlation sheet not found.")

    st.stop()

# ---------------------------------------------------------
# Heatmap
# ---------------------------------------------------------

st.subheader("Correlation Matrix")

correlation_heatmap(
    correlation_df,
    "Strategy Correlation Matrix",
)

# ---------------------------------------------------------
# Correlation Table
# ---------------------------------------------------------

st.divider()

st.subheader("Correlation Matrix")

dataframe(correlation_df)

# ---------------------------------------------------------
# Diversification
# ---------------------------------------------------------

if not diversification_df.empty:
    st.divider()

    st.subheader("Diversification Analysis")

    dataframe(diversification_df)

# ---------------------------------------------------------
# Correlation Distribution
# ---------------------------------------------------------

numeric = correlation_df.select_dtypes(include="number").columns.tolist()

if numeric:
    st.divider()

    metric = st.selectbox(
        "Distribution Metric",
        numeric,
    )

    histogram(
        correlation_df,
        metric,
        f"{metric} Distribution",
    )

# ---------------------------------------------------------
# Most Correlated
# ---------------------------------------------------------

if not diversification_df.empty and "Correlation" in diversification_df.columns:
    st.divider()

    st.subheader("Most Correlated Pairs")

    top = diversification_df.sort_values(
        "Correlation",
        ascending=False,
    ).head(20)

    dataframe(top)

# ---------------------------------------------------------
# Least Correlated
# ---------------------------------------------------------

if not diversification_df.empty and "Correlation" in diversification_df.columns:
    st.divider()

    st.subheader("Least Correlated Pairs")

    bottom = diversification_df.sort_values(
        "Correlation",
        ascending=True,
    ).head(20)

    dataframe(bottom)

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = correlation_df.to_csv(index=False)

st.download_button(
    "📥 Download Correlation Matrix",
    csv,
    "correlation.csv",
    "text/csv",
)
