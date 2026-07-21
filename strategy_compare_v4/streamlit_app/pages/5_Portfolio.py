"""
Portfolio Dashboard
===================

Institutional Portfolio Analytics
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from components.cards import (
    portfolio_summary_card,
)
from components.charts import (
    bar_chart,
    dataframe,
    histogram,
    pie_chart,
)
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Portfolio",
    page_icon="💼",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "💼 Institutional Portfolio"

PAGE_CAPTION = "Institutional Portfolio Construction and Allocation."

PORTFOLIO_SHEETS = {
    "portfolio": "Portfolio",
    "summary": "Portfolio Summary",
}

TOP_HOLDINGS = 10


# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render portfolio dashboard header.
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
def load_portfolio_data() -> dict[str, pd.DataFrame]:
    """
    Load portfolio worksheets.
    """

    workbook = st.session_state.portfolio_report

    return {
        key: get_sheet(
            workbook,
            sheet_name,
        )
        for key, sheet_name in PORTFOLIO_SHEETS.items()
    }


def validate_portfolio_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate portfolio datasets.
    """

    if not data:
        st.error("Portfolio report is unavailable.")

        st.stop()

    portfolio_df = data.get(
        "portfolio",
        pd.DataFrame(),
    )

    if portfolio_df.empty:
        st.error("Portfolio worksheet not found or empty.")

        st.stop()


# ============================================================
# Portfolio Summary Cards
# ============================================================


def render_summary(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio KPI summary cards.
    """

    portfolio_summary_card(
        df,
    )

    st.divider()


# ============================================================
# Portfolio Summary Table
# ============================================================


def render_portfolio_summary(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio summary worksheet.
    """

    if df is None or df.empty:
        return

    st.subheader("Portfolio Summary")

    dataframe(
        df,
    )

    st.divider()


# ============================================================
# Portfolio Holdings Table
# ============================================================


def render_holdings_table(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio holdings table.
    """

    if df.empty:
        return

    st.subheader("Portfolio Holdings")

    dataframe(
        df,
    )

    st.divider()


# ============================================================
# Portfolio Filters
# ============================================================


def render_filters(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Filter portfolio holdings.
    """

    if df.empty:
        return df

    st.subheader("Filters")

    left, right = st.columns(2)

    # --------------------------------------------------------
    # Search Stock
    # --------------------------------------------------------

    with left:
        search = st.text_input(
            "Search Stock",
            placeholder="Enter stock name...",
        )

    # --------------------------------------------------------
    # Top Holdings
    # --------------------------------------------------------

    with right:
        top_n = st.slider(
            "Display Holdings",
            min_value=1,
            max_value=len(df),
            value=min(
                TOP_HOLDINGS,
                len(df),
            ),
        )

    filtered = df.copy()

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

    if "Weight %" in filtered.columns:
        filtered = (
            filtered.sort_values(
                "Weight %",
                ascending=False,
            )
            .head(top_n)
            .reset_index(
                drop=True,
            )
        )

    st.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** holdings.")

    st.divider()

    return filtered


# ============================================================
# Portfolio Charts
# ============================================================


def render_charts(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio analytics charts.
    """

    if df.empty:
        return

    st.subheader("Portfolio Analytics")

    # ========================================================
    # Allocation & Expected Return
    # ========================================================

    left, right = st.columns(2)

    # --------------------------------------------------------
    # Portfolio Allocation
    # --------------------------------------------------------

    with left:
        if "Weight %" in df.columns and "Stock" in df.columns:
            pie_chart(
                df,
                names="Stock",
                values="Weight %",
                title="Portfolio Allocation",
            )

    # --------------------------------------------------------
    # Expected Return
    # --------------------------------------------------------

    with right:
        if "Expected Return %" in df.columns and "Stock" in df.columns:
            bar_chart(
                df,
                x="Stock",
                y="Expected Return %",
                color="Expected Return %",
                title="Expected Return by Holding",
            )

    st.divider()

    # ========================================================
    # Distribution & Score Analysis
    # ========================================================

    left, right = st.columns(2)

    # --------------------------------------------------------
    # Weight Distribution
    # --------------------------------------------------------

    with left:
        if "Weight %" in df.columns:
            histogram(
                df,
                "Weight %",
                "Portfolio Weight Distribution",
            )

    # --------------------------------------------------------
    # Institutional Score
    # --------------------------------------------------------

    with right:
        score_column = resolve_score_column(
            df,
        )

        if score_column:
            bar_chart(
                df,
                x="Stock" if "Stock" in df.columns else df.columns[0],
                y=score_column,
                color=score_column,
                title=f"{score_column} by Holding",
            )

    st.divider()


# ============================================================
# Score Column Resolver
# ============================================================


def resolve_score_column(
    df: pd.DataFrame,
) -> str | None:
    """
    Find available portfolio scoring column.
    """

    score_columns = [
        "Institutional Score",
        "Composite Score",
        "Edge Score",
    ]

    for column in score_columns:
        if column in df.columns:
            return column

    return None


# ============================================================
# Top Holdings
# ============================================================


def render_top_holdings(
    df: pd.DataFrame,
) -> None:
    """
    Display highest weighted holdings.
    """

    if df.empty:
        return

    if "Weight %" not in df.columns:
        return

    st.subheader("Top Holdings")

    top_holdings = df.sort_values(
        "Weight %",
        ascending=False,
    ).head(TOP_HOLDINGS)

    dataframe(
        top_holdings,
    )

    st.divider()


# ============================================================
# Portfolio Statistics
# ============================================================


def render_statistics(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio statistics.
    """

    if df.empty:
        return

    st.subheader("Portfolio Statistics")

    c1, c2, c3, c4 = st.columns(4)

    # --------------------------------------------------------
    # Holdings Count
    # --------------------------------------------------------

    with c1:
        st.metric(
            "Holdings",
            f"{len(df):,}",
        )

    # --------------------------------------------------------
    # Total Weight
    # --------------------------------------------------------

    with c2:
        if "Weight %" in df.columns:
            st.metric(
                "Total Weight",
                f"{df['Weight %'].sum():.2f}%",
            )

    # --------------------------------------------------------
    # Average Return
    # --------------------------------------------------------

    with c3:
        if "Expected Return %" in df.columns:
            st.metric(
                "Average Return",
                f"{df['Expected Return %'].mean():.2f}%",
            )

    # --------------------------------------------------------
    # Average Score
    # --------------------------------------------------------

    with c4:
        score_column = resolve_score_column(
            df,
        )

        if score_column:
            st.metric(
                "Average Score",
                f"{df[score_column].mean():.2f}",
            )

    st.divider()


# ============================================================
# Risk & Concentration Analysis
# ============================================================


def render_risk_analysis(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio concentration metrics.
    """

    if df.empty:
        return

    if "Weight %" not in df.columns:
        return

    st.subheader("Portfolio Concentration")

    top_5_weight = (
        df.sort_values(
            "Weight %",
            ascending=False,
        )
        .head(5)["Weight %"]
        .sum()
    )

    max_position = df["Weight %"].max()

    average_position = df["Weight %"].mean()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Top 5 Weight",
            f"{top_5_weight:.2f}%",
        )

    with c2:
        st.metric(
            "Largest Position",
            f"{max_position:.2f}%",
        )

    with c3:
        st.metric(
            "Average Position",
            f"{average_position:.2f}%",
        )

    st.divider()


# ============================================================
# Download
# ============================================================


def render_download(
    df: pd.DataFrame,
) -> None:
    """
    Render portfolio export.
    """

    if df.empty:
        return

    st.subheader("Export")

    csv = df.to_csv(
        index=False,
    )

    st.download_button(
        label="📥 Download Institutional Portfolio",
        data=csv,
        file_name="institutional_portfolio.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Empty State
# ============================================================


def render_empty_state() -> None:
    """
    Render empty portfolio message.
    """

    st.info("""
### 💼 Institutional Portfolio

This dashboard provides portfolio construction and allocation analytics.

Features:

- Portfolio Holdings
- Allocation Analysis
- Expected Return Analysis
- Position Concentration
- Quality Score Evaluation
- Portfolio Statistics
- CSV Export

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
    Render Portfolio dashboard.
    """

    render_header()

    validate_session()

    portfolio_data = load_portfolio_data()

    validate_portfolio_data(
        portfolio_data,
    )

    portfolio_df = portfolio_data["portfolio"]

    summary_df = portfolio_data.get(
        "summary",
        pd.DataFrame(),
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    render_summary(
        portfolio_df,
    )

    # --------------------------------------------------------
    # Portfolio Summary
    # --------------------------------------------------------

    render_portfolio_summary(
        summary_df,
    )

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    filtered_df = render_filters(
        portfolio_df,
    )

    if filtered_df.empty:
        st.warning("No portfolio holdings match the selected filters.")

        render_footer()

        return

    # --------------------------------------------------------
    # Holdings
    # --------------------------------------------------------

    render_holdings_table(
        filtered_df,
    )

    # --------------------------------------------------------
    # Charts
    # --------------------------------------------------------

    render_charts(
        filtered_df,
    )

    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    render_top_holdings(
        filtered_df,
    )

    render_statistics(
        filtered_df,
    )

    render_risk_analysis(
        filtered_df,
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
