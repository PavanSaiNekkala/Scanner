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

PAGE_CAPTION = (
    "Analyze correlation, diversification and clustering."
)


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

    st.title(
        PAGE_TITLE,
    )

    st.caption(
        PAGE_CAPTION,
    )

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

        st.warning(
            "Please load reports from the Data Load page.",
        )

        st.stop()


# ============================================================
# Data Loading
# ============================================================


@st.cache_data(
    show_spinner=False,
)
def load_correlation_data() -> dict[str, pd.DataFrame]:
    """
    Load correlation workbook sheets.
    """

    workbook = (
        st.session_state.correlation_report
    )


    return {
        key: get_sheet(
            workbook,
            sheet_name,
        )
        for key, sheet_name in CORRELATION_SHEETS.items()
    }


# ============================================================
# Validation
# ============================================================


def validate_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate correlation datasets.
    """

    if not data:

        st.error(
            "Correlation report unavailable.",
        )

        st.stop()


    if not any(
        not df.empty
        for df in data.values()
    ):

        st.error(
            "No correlation data available.",
        )

        st.stop()


# ============================================================
# KPI Summary
# ============================================================


def render_summary(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Render correlation summary cards.
    """

    total_sheets = len(data)

    available = sum(
        not df.empty
        for df in data.values()
    )


    records = sum(
        len(df)
        for df in data.values()
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Analytics Modules",
            total_sheets,
        )


    with c2:

        st.metric(
            "Available Sheets",
            available,
        )


    with c3:

        st.metric(
            "Total Records",
            f"{records:,}",
        )


    st.divider()


# ============================================================
# Matrix Renderer
# ============================================================


def render_matrix(
    title: str,
    df: pd.DataFrame,
) -> None:
    """
    Render correlation matrix.
    """

    st.subheader(
        title,
    )


    if df.empty:

        st.info(
            f"{title} unavailable.",
        )

        return


    correlation_heatmap(
        df,
        title,
    )


    dataframe(
        df,
    )


# ============================================================
# Dataset Selector
# ============================================================


def render_dataset_selector(
    data: dict[str, pd.DataFrame],
) -> tuple[str, pd.DataFrame]:
    """
    Select correlation dataset.
    """

    selected = st.selectbox(
        "Select Analysis",
        options=list(
            data.keys()
        ),
        format_func=lambda x: x.title(),
    )


    return (
        selected,
        data[selected],
    )

# ============================================================
# Diversification Renderer
# ============================================================


def render_diversification(
    diversification_df: pd.DataFrame,
    pairs_df: pd.DataFrame,
) -> None:
    """
    Render diversification analytics.
    """

    if not diversification_df.empty:

        st.subheader(
            "Diversification Analysis",
        )

        dataframe(
            diversification_df,
        )


    if not pairs_df.empty:

        st.divider()

        st.subheader(
            "Correlation Pairs",
        )

        dataframe(
            pairs_df,
        )


    st.divider()


# ============================================================
# Cluster Renderer
# ============================================================


def render_clusters(
    clusters_df: pd.DataFrame,
) -> None:
    """
    Render cluster analysis.
    """

    if clusters_df.empty:

        return


    st.subheader(
        "Correlation Clusters",
    )


    dataframe(
        clusters_df,
    )


    st.divider()


# ============================================================
# Summary Renderer
# ============================================================


def render_summary_sheet(
    summary_df: pd.DataFrame,
) -> None:
    """
    Render correlation summary.
    """

    if summary_df.empty:

        return


    st.subheader(
        "Correlation Summary",
    )


    dataframe(
        summary_df,
    )


    st.divider()


# ============================================================
# Distribution Analysis
# ============================================================


def render_distribution(
    df: pd.DataFrame,
) -> None:
    """
    Render correlation distribution.
    """

    if df.empty:

        return


    numeric_columns = (
        df.select_dtypes(
            include="number",
        )
        .columns
        .tolist()
    )


    if not numeric_columns:

        return


    st.subheader(
        "Correlation Distribution",
    )


    metric = st.selectbox(
        "Select Correlation Metric",
        options=numeric_columns,
    )


    histogram(
        df,
        metric,
        f"{metric} Distribution",
    )


    st.divider()


# ============================================================
# Correlation Statistics
# ============================================================


def render_statistics(
    df: pd.DataFrame,
) -> None:
    """
    Render correlation statistics.
    """

    if df.empty:

        return


    numeric = df.select_dtypes(
        include="number",
    )


    if numeric.empty:

        return


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Metrics",
            len(numeric.columns),
        )


    with c2:

        st.metric(
            "Average Correlation",
            round(
                numeric.mean()
                .mean(),
                3,
            ),
        )


    with c3:

        st.metric(
            "Maximum Correlation",
            round(
                numeric.max()
                .max(),
                3,
            ),
        )


    st.divider()


# ============================================================
# Download
# ============================================================


def render_download(
    df: pd.DataFrame,
    name: str,
) -> None:
    """
    Export correlation dataset.
    """

    if df.empty:

        return


    st.subheader(
        "Export",
    )


    csv = df.to_csv(
        index=False,
    )


    st.download_button(
        label="📥 Download Correlation Data",
        data=csv,
        file_name=f"{name}_correlation.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Empty State
# ============================================================


def render_empty_state() -> None:
    """
    Render empty dashboard.
    """

    st.info(
        """
### 🔗 Correlation & Diversification

Analyze portfolio and strategy relationships.

Features:

- Pearson Correlation
- Spearman Correlation
- Kendall Correlation
- Heatmaps
- Diversification Analysis
- Correlation Pairs
- Cluster Analysis
- Distribution Analysis

Load reports from the Data Load page.
"""
    )


# ============================================================
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render footer.
    """

    st.divider()


    left, right = st.columns(
        [3, 1],
    )


    with left:

        st.caption(
            "Institutional Strategy Comparison Platform",
        )


    with right:

        st.caption(
            "Version 4.0",
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


    render_summary(
        data,
    )


    selected_name, selected_df = (
        render_dataset_selector(
            data,
        )
    )


    if selected_df.empty:

        render_empty_state()

        render_footer()

        return


    # --------------------------------------------------------
    # Main Dataset
    # --------------------------------------------------------

    if selected_name in [
        "pearson",
        "spearman",
        "kendall",
        "heatmap",
    ]:

        render_matrix(
            selected_name.title(),
            selected_df,
        )


    elif selected_name == "diversification":

        render_diversification(
            selected_df,
            data.get(
                "pairs",
                pd.DataFrame(),
            ),
        )


    elif selected_name == "clusters":

        render_clusters(
            selected_df,
        )


    elif selected_name == "summary":

        render_summary_sheet(
            selected_df,
        )


    else:

        dataframe(
            selected_df,
        )


    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    render_statistics(
        selected_df,
    )


    render_distribution(
        selected_df,
    )


    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    render_download(
        selected_df,
        selected_name,
    )


    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()