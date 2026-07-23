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

PAGE_CAPTION = (
    "Enterprise-level overview of the complete strategy ecosystem."
)


TOP_RECORDS = 10


DASHBOARD_SHEETS = {
    "strategy": (
        "final_report",
        "Strategy Rankings",
    ),

    "recommendations": (
        "final_report",
        "Strategy Recommendations",
    ),

    "stock": (
        "final_report",
        "Stock Rankings",
    ),

    "portfolio": (
        "final_report",
        "Portfolio",
    ),

    "correlation": (
        "final_report",
        "Correlation",
    ),
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
    Validate loaded reports.
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

def load_dashboard_data() -> dict[str, pd.DataFrame]:
    """
    Load executive datasets.
    """

    data = {}


    for key, (
        session_key,
        sheet_name,
    ) in DASHBOARD_SHEETS.items():

        workbook = st.session_state.get(
            session_key,
        )


        if workbook is None:

            data[key] = pd.DataFrame()

            continue


        data[key] = get_sheet(
            workbook,
            sheet_name,
        )


    return data


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

        st.error(
            "Executive dashboard data unavailable.",
        )

        st.stop()


    if not any(
        not df.empty
        for df in data.values()
    ):

        st.error(
            "No executive dashboard data found.",
        )

        st.stop()


# ============================================================
# Executive KPIs
# ============================================================


def render_kpis(
    data: dict[str, pd.DataFrame],
) -> None:
    """
    Render executive KPI cards.
    """

    executive_dashboard(
        data.get(
            "strategy",
            pd.DataFrame(),
        ),

        data.get(
            "stock",
            pd.DataFrame(),
        ),

        data.get(
            "portfolio",
            pd.DataFrame(),
        ),
    )


    st.divider()


# ============================================================
# Recommendation Intelligence
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

        st.subheader(
            "Institutional Recommendation Mix",
        )


        if not recommendation_df.empty:

            recommendation_chart(
                recommendation_df,
            )


    with right:

        st.subheader(
            "Stock Recommendation Mix",
        )


        if (
            "Recommendation" in stock_df.columns
            and not stock_df.empty
        ):

            allocation = (
                stock_df
                .groupby(
                    "Recommendation",
                )
                .size()
                .reset_index(
                    name="Count",
                )
            )


            pie_chart(
                allocation,
                names="Recommendation",
                values="Count",
                title="Stock Recommendations",
            )


    st.divider()


# ============================================================
# Diversification
# ============================================================


def render_correlation(
    correlation_df: pd.DataFrame,
) -> None:
    """
    Render diversification overview.
    """

    if correlation_df.empty:

        return


    st.subheader(
        "Diversification Overview",
    )


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
    Display strongest strategies.
    """

    if df.empty:

        return


    st.subheader(
        "Top Strategies",
    )


    if "Composite Score" in df.columns:

        top = (
            df.sort_values(
                "Composite Score",
                ascending=False,
            )
            .head(
                TOP_RECORDS,
            )
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
    Display strongest stocks.
    """

    if df.empty:

        return


    st.subheader(
        "Top Stocks",
    )


    if "Institutional Score" in df.columns:

        top = (
            df.sort_values(
                "Institutional Score",
                ascending=False,
            )
            .head(
                TOP_RECORDS,
            )
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
    Render portfolio overview.
    """

    if df.empty:

        return


    st.subheader(
        "Portfolio Snapshot",
    )


    st.dataframe(
        df.head(
            TOP_RECORDS,
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render footer.
    """

    st.divider()

    st.caption(
        "Institutional Strategy Comparison Platform • Executive Dashboard"
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
        data.get(
            "recommendations",
            pd.DataFrame(),
        ),

        data.get(
            "stock",
            pd.DataFrame(),
        ),
    )


    render_correlation(
        data.get(
            "correlation",
            pd.DataFrame(),
        ),
    )


    render_top_strategies(
        data.get(
            "strategy",
            pd.DataFrame(),
        ),
    )


    render_top_stocks(
        data.get(
            "stock",
            pd.DataFrame(),
        ),
    )


    render_portfolio_snapshot(
        data.get(
            "portfolio",
            pd.DataFrame(),
        ),
    )


    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()