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
from themes import apply_theme

st.set_page_config(
    page_title="Strategies",
    page_icon="📈",
    layout="wide",
)
apply_theme()

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

if not st.session_state.get(
    "reports_loaded",
    False,
):
    st.warning("Please load reports first.")
    st.stop()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

pearson_df = get_sheet(
    st.session_state.correlation_report,
    "Pearson",
)

spearman_df = get_sheet(
    st.session_state.correlation_report,
    "Spearman",
)

kendall_df = get_sheet(
    st.session_state.correlation_report,
    "Kendall",
)

heatmap_df = get_sheet(
    st.session_state.correlation_report,
    "Heatmap",
)

diversification_df = get_sheet(
    st.session_state.correlation_report,
    "Diversification",
)

pairs_df = get_sheet(
    st.session_state.correlation_report,
    "Correlation Pairs",
)

clusters_df = get_sheet(
    st.session_state.correlation_report,
    "Clusters",
)

summary_df = get_sheet(
    st.session_state.correlation_report,
    "Summary",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Pearson",
        "Spearman",
        "Kendall",
        "Diversification",
        "Clusters",
    ]
)

# =========================================================
# Pearson
# =========================================================

with tab1:
    st.subheader("Pearson Correlation")

    if pearson_df.empty:
        st.info("Pearson sheet not available.")
    else:
        correlation_heatmap(
            pearson_df,
            "Pearson Correlation",
        )

        dataframe(
            pearson_df,
        )

# =========================================================
# Spearman
# =========================================================

with tab2:
    st.subheader("Spearman Correlation")

    if spearman_df.empty:
        st.info("Spearman sheet not available.")
    else:
        correlation_heatmap(
            spearman_df,
            "Spearman Correlation",
        )

        dataframe(
            spearman_df,
        )

# =========================================================
# Kendall
# =========================================================

with tab3:
    st.subheader("Kendall Correlation")

    if kendall_df.empty:
        st.info("Kendall sheet not available.")
    else:
        correlation_heatmap(
            kendall_df,
            "Kendall Correlation",
        )

        dataframe(
            kendall_df,
        )

# =========================================================
# Diversification
# =========================================================

with tab4:
    st.subheader("Diversification")

    if not diversification_df.empty:
        dataframe(
            diversification_df,
        )

    if not pairs_df.empty:
        st.divider()

        st.subheader("Correlation Pairs")

        dataframe(
            pairs_df,
        )

# =========================================================
# Clusters
# =========================================================

with tab5:
    st.subheader("Correlation Clusters")

    if not clusters_df.empty:
        dataframe(
            clusters_df,
        )

    if not summary_df.empty:
        st.divider()

        st.subheader("Summary")

        dataframe(
            summary_df,
        )

# ---------------------------------------------------------
# Histogram
# ---------------------------------------------------------

active = pearson_df if not pearson_df.empty else spearman_df

if not active.empty:
    numeric = active.select_dtypes(
        include="number",
    ).columns.tolist()

    if numeric:
        st.divider()

        metric = st.selectbox(
            "Distribution Metric",
            numeric,
        )

        histogram(
            active,
            metric,
            f"{metric} Distribution",
        )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

if not pearson_df.empty:
    st.divider()

    st.download_button(
        "📥 Download Pearson Correlation",
        pearson_df.to_csv(
            index=False,
        ),
        "pearson_correlation.csv",
        "text/csv",
    )
