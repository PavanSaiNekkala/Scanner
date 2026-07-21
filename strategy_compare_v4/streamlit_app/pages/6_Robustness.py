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

PAGE_CAPTION = "Evaluate the consistency and stability of strategy performance."


ROBUSTNESS_SHEETS = {
    "robustness": "Robustness",
    "consistency": "Consistency",
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

    st.title(PAGE_TITLE)

    st.caption(PAGE_CAPTION)

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
        st.warning("Please load reports from the Data Load page.")

        st.stop()


# ============================================================
# Data Loading
# ============================================================


@st.cache_data(show_spinner=False)
def load_robustness_data() -> dict[str, pd.DataFrame]:
    """
    Load robustness worksheets.
    """

    workbook = st.session_state.robustness_report

    return {
        key: get_sheet(
            workbook,
            sheet_name,
        )
        for key, sheet_name in ROBUSTNESS_SHEETS.items()
    }


# ============================================================
# Data Validation
# ============================================================


def validate_robustness_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate robustness datasets.
    """

    if not data:
        st.error("Robustness report is unavailable.")

        st.stop()

    robustness_df = data.get(
        "robustness",
        pd.DataFrame(),
    )

    if robustness_df.empty:
        st.error("Robustness worksheet not found or empty.")

        st.stop()


# ============================================================
# Summary
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
# Tables
# ============================================================


def render_tables(
    robustness_df: pd.DataFrame,
    summary_df: pd.DataFrame,
) -> None:
    """
    Render robustness tables.
    """

    if summary_df is not None and not summary_df.empty:
        st.subheader("Summary")

        dataframe(
            summary_df,
        )

        st.divider()

    st.subheader("Robustness Metrics")

    dataframe(
        robustness_df,
    )

    st.divider()


# ============================================================
# Charts
# ============================================================


def render_charts(
    df: pd.DataFrame,
) -> None:
    """
    Render robustness analytics charts.
    """

    if df.empty:
        return

    numeric_columns = df.select_dtypes(
        include="number",
    ).columns.tolist()

    if not numeric_columns:
        return

    st.subheader("Robustness Analytics")

    metric = st.selectbox(
        "Select Metric",
        numeric_columns,
    )

    left, right = st.columns(2)

    # --------------------------------------------------------
    # Ranking Chart
    # --------------------------------------------------------

    with left:
        label_column = "Strategy" if "Strategy" in df.columns else df.columns[0]

        ranked = df.sort_values(
            metric,
            ascending=False,
        ).head(20)

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

    # --------------------------------------------------------
    # Box Plot
    # --------------------------------------------------------

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
    Render consistency analysis table.
    """

    if df is None or df.empty:
        return

    st.subheader("Consistency Analysis")

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
    Display highest robustness performers.
    """

    if df.empty:
        return

    score_column = None

    for column in [
        "Composite Score",
        "Robustness Score",
        "Composite",
    ]:
        if column in df.columns:
            score_column = column

            break

    if score_column is None:
        return

    st.subheader("Top Robust Strategies")

    top = df.sort_values(
        score_column,
        ascending=False,
    ).head(TOP_STRATEGIES)

    dataframe(
        top,
    )

    st.divider()


# ============================================================
# Download
# ============================================================


def render_download(
    df: pd.DataFrame,
) -> None:
    """
    Export robustness report.
    """

    if df.empty:
        return

    st.subheader("Export")

    csv = df.to_csv(
        index=False,
    )

    st.download_button(
        label="📥 Download Robustness Analysis",
        data=csv,
        file_name="robustness.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Empty State
# ============================================================


def render_empty_state() -> None:
    """
    Render empty dashboard state.
    """

    st.info("""
### 🛡 Robustness Analysis

This dashboard evaluates strategy stability and consistency.

Features:

- Robustness Score Analysis
- Stability Ranking
- Metric Distribution
- Consistency Evaluation
- Top Robust Strategies
- CSV Export

Load reports from the **Data Load** page to begin.
""")


# ============================================================
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render application footer.
    """

    st.divider()

    left, right = st.columns(
        [3, 1],
    )

    with left:
        st.caption("Institutional Strategy Comparison Platform")

    with right:
        st.caption("Version 4.0")


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Render Robustness dashboard.
    """

    render_header()

    validate_session()

    robustness_data = load_robustness_data()

    validate_robustness_data(
        robustness_data,
    )

    robustness_df = robustness_data["robustness"]

    consistency_df = robustness_data.get(
        "consistency",
        pd.DataFrame(),
    )

    summary_df = robustness_data.get(
        "summary",
        pd.DataFrame(),
    )

    if robustness_df.empty:
        render_empty_state()

        render_footer()

        return

    render_summary(
        robustness_df,
    )

    render_tables(
        robustness_df,
        summary_df,
    )

    render_charts(
        robustness_df,
    )

    render_consistency(
        consistency_df,
    )

    render_top_strategies(
        robustness_df,
    )

    render_download(
        robustness_df,
    )

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
else:
    main()
