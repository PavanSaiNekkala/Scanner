"""
Executive Dashboard
===================

Institutional Overview Dashboard
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from components.charts import (
    correlation_heatmap,
    pie_chart,
    recommendation_chart,
)
from components.metrics import executive_dashboard
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "📊 Executive Dashboard"

PAGE_CAPTION = "Enterprise-level overview of the complete strategy ecosystem."


TOP_RECORDS = 10


DASHBOARD_SHEETS = {
    "strategy": "Strategy Ranking",
    "recommendations": "Recommendations",
    "stock": "Stock Rankings",
    "portfolio": "Portfolio",
    "correlation": "Heatmap",
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
    Validate loaded reports.
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
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    """
    Load executive dashboard datasets.
    """

    return {
        key: get_sheet(
            (
                st.session_state[f"{key}_report"]
                if key != "recommendations"
                else st.session_state.strategy_report
            ),
            sheet,
        )
        for key, sheet in DASHBOARD_SHEETS.items()
    }


# ============================================================
# Validation
# ============================================================


def validate_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Validate dashboard datasets.
    """

    if not data:
        st.error("Executive dashboard data unavailable.")

        st.stop()


# ============================================================
# KPI Section
# ============================================================


def render_kpis(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Render executive KPIs.
    """

    executive_dashboard(
        data["strategy"],
        data["stock"],
        data["portfolio"],
    )

    st.divider()


# ============================================================
# Recommendation Overview
# ============================================================


def render_recommendations(
    recommendation_df: pd.DataFrame,
    stock_df: pd.DataFrame,
) -> None:
    """
    Render recommendation analytics.
    """

    left, right = st.columns(2)

    with left:
        st.subheader("Recommendation Mix")

        if not recommendation_df.empty:
            recommendation_chart(
                recommendation_df,
            )

    with right:
        st.subheader("Stock Recommendation Mix")

        if "Recommendation" in stock_df.columns and "Stock" in stock_df.columns:
            allocation = (
                stock_df.groupby("Recommendation")
                .size()
                .reset_index(
                    name="Count",
                )
            )

            pie_chart(
                allocation,
                names="Recommendation",
                values="Count",
                title="Stock Recommendation Mix",
            )

    st.divider()


# ============================================================
# Correlation
# ============================================================


def render_correlation(
    correlation_df: pd.DataFrame,
) -> None:
    """
    Render diversification overview.
    """

    if correlation_df.empty:
        return

    st.subheader("Diversification Overview")

    correlation_heatmap(
        correlation_df,
        "Correlation Matrix",
    )

    st.divider()


# ============================================================
# Top Strategies
# ============================================================


def render_top_strategies(
    df: pd.DataFrame,
) -> None:
    """
    Display best strategies.
    """

    st.subheader("Top 10 Strategies")

    if "Composite Score" in df.columns:
        top = df.sort_values(
            "Composite Score",
            ascending=False,
        ).head(
            TOP_RECORDS,
        )

        st.dataframe(
            top,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()


# ============================================================
# Top Stocks
# ============================================================


def render_top_stocks(
    df: pd.DataFrame,
) -> None:
    """
    Display best stocks.
    """

    st.subheader("Top 10 Stocks")

    if "Institutional Score" in df.columns:
        top = df.sort_values(
            "Institutional Score",
            ascending=False,
        ).head(
            TOP_RECORDS,
        )

        st.dataframe(
            top,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()


# ============================================================
# Portfolio Snapshot
# ============================================================


def render_portfolio_snapshot(
    df: pd.DataFrame,
) -> None:
    """
    Display portfolio overview.
    """

    st.subheader("Portfolio Snapshot")

    if df.empty:
        st.info("Portfolio data unavailable.")

        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Render executive dashboard.
    """

    render_header()

    validate_session()

    data = load_dashboard_data()

    validate_data(
        data,
    )

    render_kpis(
        data,
    )

    render_recommendations(
        data["recommendations"],
        data["stock"],
    )

    render_correlation(
        data["correlation"],
    )

    render_top_strategies(
        data["strategy"],
    )

    render_top_stocks(
        data["stock"],
    )

    render_portfolio_snapshot(
        data["portfolio"],
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()

else:
    main()
