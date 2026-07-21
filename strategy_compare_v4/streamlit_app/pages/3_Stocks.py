"""
Stocks Dashboard
================

Institutional Stock Analytics Dashboard
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from components.cards import (
    recommendation_badge,
    strategy_summary_card,
)
from components.charts import (
    bar_chart,
    dataframe,
    histogram,
    radar_chart,
    recommendation_chart,
    scatter_chart,
)
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Stock Analytics",
    page_icon="🏢",
    layout="wide",
)

apply_theme()

# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "🏢 Institutional Stock Analytics"

PAGE_CAPTION = "Institutional ranking and analysis of all stocks."

SHEET_NAME = "Stock Rankings"

DEFAULT_TOP_N = 25

# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render page header.
    """

    st.title(PAGE_TITLE)

    st.caption(PAGE_CAPTION)

    st.divider()


# ============================================================
# Validation
# ============================================================


def validate_session() -> None:
    """
    Ensure reports have been loaded.
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
def load_stock_data() -> pd.DataFrame:
    """
    Load the Stock Rankings worksheet.
    """

    return get_sheet(
        st.session_state.stock_report,
        SHEET_NAME,
    )


def validate_stock_data(
    df: pd.DataFrame,
) -> None:
    """
    Validate loaded stock data.
    """

    if df is None or df.empty:
        st.error(f"'{SHEET_NAME}' worksheet was not found or is empty.")

        st.stop()


# ============================================================
# Summary
# ============================================================


def render_summary(
    df: pd.DataFrame,
) -> None:
    """
    Render stock summary metrics.
    """

    strategy_summary_card(df)

    st.divider()


# ============================================================
# Filters
# ============================================================


def render_filters(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Render stock filters and return the filtered dataset.
    """

    st.subheader("Filters")

    left, center, right = st.columns(3)

    # --------------------------------------------------------
    # Recommendation Filter
    # --------------------------------------------------------

    with left:
        recommendations = ["All"]

        if "Recommendation" in df.columns:
            recommendations.extend(
                sorted(df["Recommendation"].dropna().astype(str).unique())
            )

        recommendation = st.selectbox(
            "Recommendation",
            recommendations,
        )

    # --------------------------------------------------------
    # Top N
    # --------------------------------------------------------

    with center:
        top_n = st.slider(
            "Top Stocks",
            min_value=1,
            max_value=len(df),
            value=min(
                DEFAULT_TOP_N,
                len(df),
            ),
            help="Display the highest ranked stocks.",
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    with right:
        search = st.text_input(
            "Search Stock",
            placeholder="Enter stock name...",
        )

    # --------------------------------------------------------
    # Apply Filters
    # --------------------------------------------------------

    filtered = df.copy()

    if recommendation != "All" and "Recommendation" in filtered.columns:
        filtered = filtered[filtered["Recommendation"] == recommendation]

    if search and "Stock" in filtered.columns:
        filtered = filtered[
            filtered["Stock"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False,
            )
        ]

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    if "Institutional Score" in filtered.columns:
        filtered = (
            filtered.sort_values(
                "Institutional Score",
                ascending=False,
            )
            .head(top_n)
            .reset_index(
                drop=True,
            )
        )

    st.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** stocks.")

    st.divider()

    return filtered


# ============================================================
# Stock Ranking Table
# ============================================================


def render_stock_table(
    df: pd.DataFrame,
) -> None:
    """
    Render stock ranking table.
    """

    st.subheader("Stock Rankings")

    dataframe(
        df,
    )

    st.divider()


# ============================================================
# Charts
# ============================================================


def render_charts(
    df: pd.DataFrame,
) -> None:
    """
    Render stock analytics charts.
    """

    if df.empty:
        return

    st.subheader("Stock Analytics")

    # --------------------------------------------------------
    # Score Charts
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:
        if "Stock" in df.columns and "Institutional Score" in df.columns:
            bar_chart(
                df,
                x="Stock",
                y="Institutional Score",
                color="Recommendation" if "Recommendation" in df.columns else None,
                title="Institutional Score",
            )

    with right:
        if "Stock" in df.columns and "Edge Score" in df.columns:
            bar_chart(
                df,
                x="Stock",
                y="Edge Score",
                color="Recommendation" if "Recommendation" in df.columns else None,
                title="Edge Score",
            )

    # --------------------------------------------------------
    # Relationship Analysis
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:
        if "Reliability Score" in df.columns and "Efficiency Score" in df.columns:
            scatter_chart(
                df,
                x="Reliability Score",
                y="Efficiency Score",
                color="Recommendation" if "Recommendation" in df.columns else None,
                hover="Stock" if "Stock" in df.columns else None,
                title="Reliability vs Efficiency",
            )

    with right:
        if "Institutional Score" in df.columns:
            histogram(
                df,
                "Institutional Score",
                "Institutional Score Distribution",
            )

    st.divider()


# ============================================================
# Recommendation Distribution
# ============================================================


def render_recommendation_distribution(
    df: pd.DataFrame,
) -> None:
    """
    Render recommendation distribution chart.
    """

    if df.empty or "Recommendation" not in df.columns:
        return

    st.subheader("Recommendation Distribution")

    recommendation_chart(
        df,
    )

    st.divider()


# ============================================================
# Stock Selector
# ============================================================


def select_stock(
    df: pd.DataFrame,
) -> pd.Series | None:
    """
    Select a stock and return its data row.
    """

    if df.empty or "Stock" not in df.columns:
        return None

    st.subheader("Stock Analysis")

    selected_stock = st.selectbox(
        "Select Stock",
        options=df["Stock"].tolist(),
    )

    row = df.loc[df["Stock"] == selected_stock]

    if row.empty:
        return None

    return row.iloc[0]


# ============================================================
# Stock Radar
# ============================================================


def render_stock_radar(
    row: pd.Series,
) -> None:
    """
    Render stock comparison radar.
    """

    if row is None:
        return

    required = [
        "Institutional Score",
        "Edge Score",
        "Reliability Score",
        "Efficiency Score",
    ]

    if not all(column in row.index for column in required):
        return

    st.subheader("Stock Radar")

    radar_chart(
        {
            "Institutional": row["Institutional Score"],
            "Edge": row["Edge Score"],
            "Reliability": row["Reliability Score"],
            "Efficiency": row["Efficiency Score"],
            "Risk": row.get(
                "Risk Score",
                0,
            ),
            "Return": row.get(
                "Return Score",
                0,
            ),
            "Opportunity": row.get(
                "Opportunity Score",
                0,
            ),
        },
        str(row["Stock"]),
    )

    st.divider()


# ============================================================
# Recommendation
# ============================================================


def render_recommendation(
    row: pd.Series,
) -> None:
    """
    Display institutional recommendation.
    """

    if row is None or "Recommendation" not in row.index:
        return

    st.subheader("Institutional Recommendation")

    recommendation_badge(
        row["Recommendation"],
    )

    st.divider()


# ============================================================
# Stock Details
# ============================================================


def render_stock_details(
    row: pd.Series,
) -> None:
    """
    Display selected stock details.
    """

    if row is None:
        return

    st.subheader("Selected Stock")

    st.dataframe(
        row.to_frame().T,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()


# ============================================================
# Key Metrics
# ============================================================


def render_key_metrics(
    row: pd.Series,
) -> None:
    """
    Render selected stock KPI metrics.
    """

    if row is None:
        return

    st.subheader("Key Metrics")

    metrics = [
        (
            "Institutional Score",
            "Institutional Score",
        ),
        (
            "Edge",
            "Edge Score",
        ),
        (
            "Reliability",
            "Reliability Score",
        ),
        (
            "Efficiency",
            "Efficiency Score",
        ),
    ]

    columns = st.columns(
        len(metrics),
    )

    for container, (label, column) in zip(
        columns,
        metrics,
        strict=False,
    ):
        with container:
            if column in row.index:
                st.metric(
                    label,
                    f"{row[column]:.2f}",
                )

    st.divider()


# ============================================================
# Download
# ============================================================


def render_download(
    df: pd.DataFrame,
) -> None:
    """
    Render stock ranking download button.
    """

    if df.empty:
        return

    st.subheader("Export")

    csv = df.to_csv(
        index=False,
    )

    st.download_button(
        label="📥 Download Stock Rankings",
        data=csv,
        file_name="stock_rankings.csv",
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
### 🏢 Institutional Stock Analytics

This dashboard provides institutional analysis of ranked stocks.

Features:

- Institutional Stock Ranking
- Recommendation Analysis
- Edge Score Evaluation
- Reliability Analysis
- Efficiency Analysis
- Stock Radar Comparison
- KPI Evaluation
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
    Render Stock Analytics dashboard.
    """

    render_header()

    validate_session()

    stock_df = load_stock_data()

    validate_stock_data(
        stock_df,
    )

    if stock_df.empty:
        render_empty_state()

        return

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    render_summary(
        stock_df,
    )

    # --------------------------------------------------------
    # Filtering
    # --------------------------------------------------------

    filtered_df = render_filters(
        stock_df,
    )

    if filtered_df.empty:
        st.warning("No stocks match the selected filters.")

        render_footer()

        return

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    render_stock_table(
        filtered_df,
    )

    # --------------------------------------------------------
    # Charts
    # --------------------------------------------------------

    render_charts(
        filtered_df,
    )

    render_recommendation_distribution(
        filtered_df,
    )

    # --------------------------------------------------------
    # Stock Analysis
    # --------------------------------------------------------

    selected_row = select_stock(
        filtered_df,
    )

    if selected_row is not None:
        render_stock_radar(
            selected_row,
        )

        render_recommendation(
            selected_row,
        )

        render_stock_details(
            selected_row,
        )

        render_key_metrics(
            selected_row,
        )

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    render_download(
        filtered_df,
    )

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
else:
    main()
