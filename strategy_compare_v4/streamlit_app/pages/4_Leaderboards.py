"""
Leaderboards Dashboard
======================

Institutional Leaderboards
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from components.charts import (
    bar_chart,
    dataframe,
)
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Leaderboards",
    page_icon="🏆",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "🏆 Institutional Leaderboards"

PAGE_CAPTION = "Overall institutional rankings across strategies and stocks."

LEADERBOARD_SHEETS = {
    "overall": "Overall",
    "strategies": "Strategies",
    "stocks": "Stocks",
    "edge": "Edge",
}

TOP_ROWS = 20


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
def load_leaderboard_data() -> dict[str, pd.DataFrame]:
    """
    Load all leaderboard worksheets.
    """

    workbook = st.session_state.leaderboard_report

    return {
        key: get_sheet(
            workbook,
            sheet_name,
        )
        for key, sheet_name in LEADERBOARD_SHEETS.items()
    }


def validate_leaderboard_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate leaderboard datasets.
    """

    if not data:
        st.error("Leaderboard report is unavailable.")

        st.stop()

    available = any(not df.empty for df in data.values())

    if not available:
        st.error("No leaderboard data found.")

        st.stop()


# ============================================================
# Column Resolver
# ============================================================


def resolve_column(
    df: pd.DataFrame,
    candidates: list[str],
    fallback: str | None = None,
) -> str | None:
    """
    Return first available column from candidates.
    """

    for column in candidates:
        if column in df.columns:
            return column

    return fallback


# ============================================================
# Overall Leaderboard
# ============================================================


def render_overall_tab(
    df: pd.DataFrame,
) -> None:
    """
    Render overall leaderboard.
    """

    st.subheader("Overall Leaderboard")

    if df.empty:
        st.info("No overall leaderboard data available.")

        return

    dataframe(
        df,
    )

    x_col = resolve_column(
        df,
        [
            "Strategy",
            "Stock",
        ],
        df.columns[0],
    )

    y_col = resolve_column(
        df,
        [
            "Composite Score",
            "Composite",
        ],
        df.columns[-1],
    )

    if x_col and y_col:
        bar_chart(
            df.head(TOP_ROWS),
            x=x_col,
            y=y_col,
            color=y_col,
            title="Top Overall Rankings",
        )


# ============================================================
# Strategy Leaderboard
# ============================================================


def render_strategy_tab(
    df: pd.DataFrame,
) -> None:
    """
    Render strategy leaderboard.
    """

    st.subheader("Strategy Leaderboard")

    if df.empty:
        st.info("No strategy leaderboard data available.")

        return

    dataframe(
        df,
    )

    x_col = resolve_column(
        df,
        [
            "Strategy",
        ],
        df.columns[0],
    )

    y_col = resolve_column(
        df,
        [
            "Composite",
            "Composite Score",
        ],
        df.columns[-1],
    )

    if x_col and y_col:
        bar_chart(
            df.head(TOP_ROWS),
            x=x_col,
            y=y_col,
            color=y_col,
            title="Top Strategies",
        )


# ============================================================
# Stock Leaderboard
# ============================================================


def render_stock_tab(
    df: pd.DataFrame,
) -> None:
    """
    Render stock leaderboard.
    """

    st.subheader("Stock Leaderboard")

    if df.empty:
        st.info("No stock leaderboard data available.")

        return

    dataframe(
        df,
    )

    x_col = resolve_column(
        df,
        [
            "Stock",
        ],
        df.columns[0],
    )

    y_col = resolve_column(
        df,
        [
            "Composite Score",
            "Institutional Score",
        ],
        df.columns[-1],
    )

    if x_col and y_col:
        bar_chart(
            df.head(TOP_ROWS),
            x=x_col,
            y=y_col,
            color=y_col,
            title="Top Stocks",
        )


# ============================================================
# Edge Leaderboard
# ============================================================


def render_edge_tab(
    df: pd.DataFrame,
) -> None:
    """
    Render edge leaderboard.
    """

    st.subheader("Edge Leaderboard")

    if df.empty:
        st.info("No edge leaderboard data available.")

        return

    dataframe(
        df,
    )

    x_col = resolve_column(
        df,
        [
            "Strategy",
            "Stock",
        ],
        df.columns[0],
    )

    y_col = resolve_column(
        df,
        [
            "Edge Score",
        ],
        None,
    )

    if x_col and y_col:
        bar_chart(
            df.head(TOP_ROWS),
            x=x_col,
            y=y_col,
            color=y_col,
            title="Highest Edge Score",
        )


# ============================================================
# Download
# ============================================================


def render_download(
    df: pd.DataFrame,
) -> None:
    """
    Render leaderboard download.
    """

    if df.empty:
        return

    st.divider()

    st.subheader("Export")

    csv = df.to_csv(
        index=False,
    )

    st.download_button(
        label="📥 Download Leaderboard",
        data=csv,
        file_name="institutional_leaderboard.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Empty State
# ============================================================


def render_empty_state() -> None:
    """
    Render empty state message.
    """

    st.info("""
### 🏆 Institutional Leaderboards

This dashboard provides institutional ranking analysis.

Available views:

- Overall Rankings
- Strategy Rankings
- Stock Rankings
- Edge Rankings

Load generated reports from the **Data Load** page to begin.
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
    Render Leaderboards dashboard.
    """

    render_header()

    validate_session()

    leaderboard_data = load_leaderboard_data()

    validate_leaderboard_data(
        leaderboard_data,
    )

    if not any(not df.empty for df in leaderboard_data.values()):
        render_empty_state()

        render_footer()

        return

    # --------------------------------------------------------
    # Tabs
    # --------------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Overall",
            "Strategies",
            "Stocks",
            "Edge",
        ]
    )

    # --------------------------------------------------------
    # Overall
    # --------------------------------------------------------

    with tab1:
        render_overall_tab(
            leaderboard_data["overall"],
        )

    # --------------------------------------------------------
    # Strategies
    # --------------------------------------------------------

    with tab2:
        render_strategy_tab(
            leaderboard_data["strategies"],
        )

    # --------------------------------------------------------
    # Stocks
    # --------------------------------------------------------

    with tab3:
        render_stock_tab(
            leaderboard_data["stocks"],
        )

    # --------------------------------------------------------
    # Edge
    # --------------------------------------------------------

    with tab4:
        render_edge_tab(
            leaderboard_data["edge"],
        )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    render_download(
        leaderboard_data["overall"],
    )

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
else:
    main()
