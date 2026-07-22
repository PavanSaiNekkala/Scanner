"""
Robustness Dashboard
====================

Institutional Robustness Analysis
"""

from __future__ import annotations

import pandas as pd
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


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Robustness",
    page_icon="🛡",
    layout="wide",
)


apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "🛡 Robustness Analysis"

PAGE_CAPTION = (
    "Evaluate strategy stability, consistency and durability."
)


ROBUSTNESS_SHEETS = {
    "robustness": "Robustness",
    "consistency": "Consistency",
    "volatility": "Volatility",
    "outliers": "Outliers",
    "summary": "Summary",
}


TOP_STRATEGIES = 10


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
    Validate report loading status.
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
def load_robustness_data() -> dict[str, pd.DataFrame]:
    """
    Load robustness worksheets.
    """

    workbook = (
        st.session_state.robustness_report
    )


    return {
        key: get_sheet(
            workbook,
            sheet_name,
        )
        for key, sheet_name in ROBUSTNESS_SHEETS.items()
    }


# ============================================================
# Validation
# ============================================================


def validate_robustness_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate robustness datasets.
    """

    if not data:

        st.error(
            "Robustness report unavailable.",
        )

        st.stop()


    robustness_df = data.get(
        "robustness",
        pd.DataFrame(),
    )


    if robustness_df.empty:

        st.error(
            "Robustness worksheet missing or empty.",
        )

        st.stop()


# ============================================================
# KPI Summary
# ============================================================


def render_summary(
    df: pd.DataFrame,
) -> None:
    """
    Render robustness KPI cards.
    """

    robustness_card(
        df,
    )


    st.divider()


# ============================================================
# Metric Resolver
# ============================================================


def resolve_metric_column(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return numeric metrics.
    """

    return (
        df.select_dtypes(
            include="number",
        )
        .columns
        .tolist()
    )


# ============================================================
# Dataset Selector
# ============================================================


def render_dataset_selector(
    data: dict[str, pd.DataFrame],
) -> tuple[str, pd.DataFrame]:
    """
    Select robustness dataset.
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
# Robustness Analytics
# ============================================================


def render_charts(
    df: pd.DataFrame,
) -> None:
    """
    Render robustness charts.
    """

    if df.empty:

        return


    metrics = resolve_metric_column(
        df,
    )


    if not metrics:

        return


    st.subheader(
        "Robustness Analytics",
    )


    metric = st.selectbox(
        "Select Metric",
        options=metrics,
    )


    left, right = st.columns(2)


    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    with left:

        label_column = (
            "Strategy"
            if "Strategy" in df.columns
            else df.columns[0]
        )


        ranked = (
            df.sort_values(
                metric,
                ascending=False,
            )
            .head(
                20,
            )
        )


        bar_chart(
            ranked,
            x=label_column,
            y=metric,
            color=metric,
            title=f"Top 20 by {metric}",
        )


    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    with right:

        histogram(
            df,
            metric,
            f"{metric} Distribution",
        )


    st.divider()


    box_plot(
        df,
        metric,
        f"{metric} Stability Analysis",
    )


    st.divider()


# ============================================================
# Consistency Analysis
# ============================================================


def render_consistency(
    df: pd.DataFrame,
) -> None:
    """
    Render consistency dataset.
    """

    if df.empty:

        return


    st.subheader(
        "Consistency Analysis",
    )


    dataframe(
        df,
    )


    st.divider()


# ============================================================
# Top Robust Strategies
# ============================================================


def render_top_strategies(
    df: pd.DataFrame,
) -> None:
    """
    Display strongest robustness performers.
    """

    if df.empty:

        return


    score_column = None


    for column in [
        "Robustness Score",
        "Composite Score",
        "Composite",
    ]:

        if column in df.columns:

            score_column = column

            break


    if score_column is None:

        return


    st.subheader(
        "Top Robust Strategies",
    )


    top = (
        df.sort_values(
            score_column,
            ascending=False,
        )
        .head(
            TOP_STRATEGIES,
        )
    )


    dataframe(
        top,
    )


    st.divider()


# ============================================================
# Stability Summary
# ============================================================


def render_stability_metrics(
    df: pd.DataFrame,
) -> None:
    """
    Render stability statistics.
    """

    if df.empty:

        return


    st.subheader(
        "Stability Metrics",
    )


    numeric = df.select_dtypes(
        include="number",
    )


    if numeric.empty:

        return


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Metrics Available",
            len(numeric.columns),
        )


    with c2:

        st.metric(
            "Strategies Analysed",
            len(df),
        )


    with c3:

        st.metric(
            "Average Score",
            round(
                numeric.mean().mean(),
                2,
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
    Export robustness dataset.
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
        label="📥 Download Robustness Analysis",
        data=csv,
        file_name=f"{name}_robustness.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Empty State
# ============================================================


def render_empty_state() -> None:
    """
    Render empty state.
    """

    st.info(
        """
### 🛡 Robustness Analysis

Evaluate strategy durability and stability.

Features:

- Robustness Score Ranking
- Consistency Analysis
- Volatility Analysis
- Outlier Detection
- Stability Metrics
- Strategy Comparison
- CSV Export

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
    Render robustness dashboard.
    """

    render_header()


    validate_session()


    robustness_data = load_robustness_data()


    validate_robustness_data(
        robustness_data,
    )


    if not any(
        not df.empty
        for df in robustness_data.values()
    ):

        render_empty_state()

        render_footer()

        return


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    robustness_df = robustness_data[
        "robustness"
    ]


    render_summary(
        robustness_df,
    )


    # --------------------------------------------------------
    # Dataset Selector
    # --------------------------------------------------------

    selected_name, selected_df = (
        render_dataset_selector(
            robustness_data,
        )
    )


    if selected_df.empty:

        st.warning(
            "Selected dataset is empty.",
        )

        render_footer()

        return


    # --------------------------------------------------------
    # Main Dataset
    # --------------------------------------------------------

    dataframe(
        selected_df,
    )


    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    render_charts(
        selected_df,
    )


    render_stability_metrics(
        selected_df,
    )


    # --------------------------------------------------------
    # Consistency
    # --------------------------------------------------------

    render_consistency(
        robustness_data.get(
            "consistency",
            pd.DataFrame(),
        )
    )


    # --------------------------------------------------------
    # Top Strategies
    # --------------------------------------------------------

    render_top_strategies(
        robustness_df,
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