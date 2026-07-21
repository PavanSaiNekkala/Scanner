"""
Correlation Dashboard
=====================

Institutional Correlation & Diversification Analytics
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from components.charts import (
    correlation_heatmap,
    dataframe,
    histogram,
)
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Correlation",
    page_icon="🔗",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "🔗 Correlation & Diversification"

PAGE_CAPTION = "Analyze strategy diversification and correlation."

CORRELATION_SHEETS = {
    "pearson": "Pearson",
    "spearman": "Spearman",
    "kendall": "Kendall",
    "heatmap": "Heatmap",
    "diversification": "Diversification",
    "pairs": "Correlation Pairs",
    "clusters": "Clusters",
    "summary": "Summary",
}


# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render dashboard header.
    """

    st.title(PAGE_TITLE)

    st.caption(PAGE_CAPTION)

    st.divider()


# ============================================================
# Validation
# ============================================================


def validate_session() -> None:
    """
    Validate report loading.
    """

    if not st.session_state.get(
        "reports_loaded",
        False,
    ):
        st.warning("Please load reports from the Data Load page.")

        st.stop()


# ============================================================
# Data Loading
# ============================================================


@st.cache_data(show_spinner=False)
def load_correlation_data() -> dict[str, pd.DataFrame]:
    """
    Load correlation workbook sheets.
    """

    workbook = st.session_state.correlation_report

    return {
        key: get_sheet(
            workbook,
            sheet_name,
        )
        for key, sheet_name in CORRELATION_SHEETS.items()
    }


def validate_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate correlation data.
    """

    if not data:
        st.error("Correlation report unavailable.")

        st.stop()


# ============================================================
# Correlation Matrix Renderer
# ============================================================


def render_matrix_tab(
    title: str,
    df: pd.DataFrame,
) -> None:
    """
    Render correlation matrix tab.
    """

    st.subheader(title)

    if df.empty:
        st.info(f"{title} data not available.")

        return

    correlation_heatmap(
        df,
        title,
    )

    dataframe(
        df,
    )


# ============================================================
# Diversification Renderer
# ============================================================


def render_diversification(
    diversification_df: pd.DataFrame,
    pairs_df: pd.DataFrame,
) -> None:
    """
    Render diversification analysis.
    """

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


# ============================================================
# Cluster Renderer
# ============================================================


def render_clusters(
    clusters_df: pd.DataFrame,
    summary_df: pd.DataFrame,
) -> None:
    """
    Render cluster analysis.
    """

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


# ============================================================
# Distribution
# ============================================================


def render_distribution(
    df: pd.DataFrame,
) -> None:
    """
    Render correlation distribution.
    """

    if df.empty:
        return

    numeric = df.select_dtypes(
        include="number",
    ).columns.tolist()

    if not numeric:
        return

    st.divider()

    st.subheader("Correlation Distribution")

    metric = st.selectbox(
        "Distribution Metric",
        numeric,
    )

    histogram(
        df,
        metric,
        f"{metric} Distribution",
    )


# ============================================================
# Download
# ============================================================


def render_download(
    df: pd.DataFrame,
) -> None:
    """
    Download correlation data.
    """

    if df.empty:
        return

    st.divider()

    st.download_button(
        label="📥 Download Pearson Correlation",
        data=df.to_csv(index=False),
        file_name="pearson_correlation.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Render correlation dashboard.
    """

    render_header()

    validate_session()

    data = load_correlation_data()

    validate_data(
        data,
    )

    pearson_df = data["pearson"]

    spearman_df = data["spearman"]

    kendall_df = data["kendall"]

    diversification_df = data["diversification"]

    pairs_df = data["pairs"]

    clusters_df = data["clusters"]

    summary_df = data["summary"]

    tabs = st.tabs(
        [
            "Pearson",
            "Spearman",
            "Kendall",
            "Diversification",
            "Clusters",
        ]
    )

    with tabs[0]:
        render_matrix_tab(
            "Pearson Correlation",
            pearson_df,
        )

    with tabs[1]:
        render_matrix_tab(
            "Spearman Correlation",
            spearman_df,
        )

    with tabs[2]:
        render_matrix_tab(
            "Kendall Correlation",
            kendall_df,
        )

    with tabs[3]:
        render_diversification(
            diversification_df,
            pairs_df,
        )

    with tabs[4]:
        render_clusters(
            clusters_df,
            summary_df,
        )

    active = pearson_df if not pearson_df.empty else spearman_df

    render_distribution(
        active,
    )

    render_download(
        pearson_df,
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()

else:
    main()
