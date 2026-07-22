"""
Institutional Strategy Comparison Platform
==========================================

Home Executive Dashboard
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components.cards import metric_card
from components.sidebar import render_sidebar

from services.loader import (
    DEFAULT_OUTPUT_FOLDER,
    get_sheet,
    load_excel,
    load_reports,
    refresh_reports,
)

from themes import apply_theme


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Institutional Strategy Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = (
    "📊 Institutional Strategy Comparison Platform"
)


PAGE_CAPTION = (
    "Institutional-grade strategy analytics, "
    "portfolio construction, robustness "
    "evaluation and reporting."
)

DASHBOARD_FILES = {
    "strategy": {
        "file": "Strategy_Comparison.xlsx",
        "sheet": "Strategy Ranking",
    },

    "stock": {
        "file": "Stock_Comparison.xlsx",
        "sheet": "Stock Rankings",
    },

    "portfolio": {
        "file": "Institutional_Portfolio.xlsx",
        "sheet": "Portfolio",
    },
}


# ============================================================
# Dashboard Data Loader
# ============================================================
@st.cache_data(
    show_spinner=False,
)
def load_dashboard_data(
    refresh_token: float,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load executive dashboard datasets.
    """


    output_folder = DEFAULT_OUTPUT_FOLDER


    if not output_folder.exists():

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )


    datasets = {}


    for name, config in DASHBOARD_FILES.items():

        file = (
            output_folder
            /
            config["file"]
        )


        if not file.exists():

            datasets[name] = pd.DataFrame()

            continue


        workbook = load_excel(
            file,
            file.stat().st_mtime,
        )


        datasets[name] = get_sheet(
            workbook,
            config["sheet"],
        )


    return (
        datasets.get(
            "strategy",
            pd.DataFrame(),
        ),

        datasets.get(
            "stock",
            pd.DataFrame(),
        ),

        datasets.get(
            "portfolio",
            pd.DataFrame(),
        ),
    )


# ============================================================
# Dashboard Validation
# ============================================================


def validate_dashboard_data(
    *datasets: pd.DataFrame,
) -> None:
    """
    Validate dashboard datasets.
    """

    if not any(
        not df.empty
        for df in datasets
    ):

        st.warning(
            "No dashboard data available. "
            "Please check generated reports."
        )

        st.stop()

# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render application header.
    """

    st.title(
        PAGE_TITLE,
    )

    st.caption(
        PAGE_CAPTION,
    )

    st.divider()


    if st.button(
        "🔄 Refresh Latest Reports",
        use_container_width=True,
    ):

        with st.spinner(
            "Refreshing latest reports..."
        ):

            refresh_reports()

            st.cache_data.clear()


        st.success(
            "Latest reports loaded.",
        )

        st.rerun()


# ============================================================
# Dashboard KPI Metrics
# ============================================================


def render_dashboard_metrics(
    strategy_df: pd.DataFrame,
    stock_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
) -> None:
    """
    Render executive KPI cards.
    """


    c1, c2, c3, c4 = st.columns(4)



    # --------------------------------------------------------
    # Strategies
    # --------------------------------------------------------

    with c1:

        if "Strategy" in strategy_df.columns:

            strategies = (
                strategy_df["Strategy"]
                .nunique()
            )

        else:

            strategies = len(
                strategy_df,
            )


        metric_card(
            "Strategies",
            f"{strategies:,}",
        )



    # --------------------------------------------------------
    # Stocks
    # --------------------------------------------------------

    with c2:

        if "Stock" in stock_df.columns:

            stocks = (
                stock_df["Stock"]
                .nunique()
            )

        else:

            stocks = len(
                stock_df,
            )


        metric_card(
            "Stocks",
            f"{stocks:,}",
        )



    # --------------------------------------------------------
    # Portfolio
    # --------------------------------------------------------

    with c3:

        metric_card(
            "Portfolio Positions",
            f"{len(portfolio_df):,}",
        )



    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------

    with c4:

        status = (
            "Loaded"
            if st.session_state.get(
                "reports_loaded",
                False,
            )
            else
            "Not Loaded"
        )


        metric_card(
            "Reports",
            status,
        )


    st.divider()



# ============================================================
# Platform Overview
# ============================================================


def render_platform_overview() -> None:
    """
    Render platform capabilities.
    """


    left, right = st.columns(
        [2, 1],
    )



    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    with left:

        st.subheader(
            "Platform Overview",
        )


        st.markdown(
            """
This platform provides institutional-grade
quantitative strategy analytics.

### Core Analytics

- Strategy Comparison
- Stock Ranking Engine
- Institutional Scoring
- Portfolio Construction
- Risk Analytics
- Correlation Analysis
- Robustness Evaluation
- Executive Reporting


### Workflow

1. Generate strategy reports
2. Load Excel outputs
3. Analyze rankings and signals
4. Construct portfolio decisions
"""
        )

    # --------------------------------------------------------
    # Output Status
    # --------------------------------------------------------

    with right:

        st.subheader(
            "Output Status",
        )

        output_folder = (
            st.session_state.get(
                "output_folder",
                str(DEFAULT_OUTPUT_FOLDER),
            )
        )

        path = Path(
            output_folder,
        )

        if path.exists():

            files = list(
                path.glob(
                    "*.xlsx",
                )
            )

            st.success(
                "Reports Available",
            )

            st.metric(
                "Excel Reports",
                len(files),
            )

            st.code(
                str(path),
                language="text",
            )

        else:

            st.warning(
                "Output folder unavailable.",
            )

    st.divider()


# ============================================================
# Quick Statistics
# ============================================================

def render_quick_statistics(
    strategy_df: pd.DataFrame,
    stock_df: pd.DataFrame,
) -> None:
    """
    Render quick analytical summary.
    """

    st.subheader(
        "Quick Statistics",
    )

    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Strategy Dataset Rows",
            f"{len(strategy_df):,}",
        )


    with c2:

        st.metric(
            "Stock Dataset Rows",
            f"{len(stock_df):,}",
        )


    with c3:

        total_columns = (
            len(strategy_df.columns)
            +
            len(stock_df.columns)
        )


        st.metric(
            "Available Metrics",
            f"{total_columns:,}",
        )


    st.divider()

# ============================================================
# Generated Reports
# ============================================================

def render_generated_reports() -> None:
    """
    Display generated Excel reports.
    """

    st.subheader(
        "Generated Reports",
    )

    output_folder = st.session_state.get(
        "output_folder",
        str(DEFAULT_OUTPUT_FOLDER),
    )

    output_path = Path(
        output_folder,
    )

    if not output_path.exists():

        st.info(
            "Output folder not found.",
        )

        return


    files = sorted(
        output_path.glob(
            "*.xlsx",
        )
    )

    if not files:

        st.warning(
            "No Excel reports available.",
        )

        return


    report_df = pd.DataFrame(
        {
            "Report": [
                file.name
                for file in files
            ],

            "Size MB": [
                round(
                    file.stat().st_size
                    /
                    (1024 * 1024),
                    2,
                )
                for file in files
            ],

            "Modified": [
                pd.to_datetime(
                    file.stat().st_mtime,
                    unit="s",
                ).strftime(
                    "%Y-%m-%d %H:%M"
                )
                for file in files
            ],
        }
    )

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True,
    )


    st.divider()


# ============================================================
# Report Health
# ============================================================

def render_report_health() -> None:
    """
    Display report loading health.
    """

    st.subheader(
        "Report Health",
    )

    required_reports = [
        "Strategy_Comparison.xlsx",
        "Stock_Comparison.xlsx",
        "Leaderboards.xlsx",
        "Correlation.xlsx",
        "Robustness.xlsx",
        "Institutional_Portfolio.xlsx",
        "Institutional_Strategy_Report.xlsx",
    ]

    output = Path(
        DEFAULT_OUTPUT_FOLDER,
    )

    rows = []

    for report in required_reports:

        exists = (
            output
            /
            report
        ).exists()


        rows.append(
            {
                "Report": report,

                "Status":
                    "Available"
                    if exists
                    else
                    "Missing",
            }
        )


    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


    st.divider()


# ============================================================
# Footer
# ============================================================

def render_footer() -> None:
    """
    Render dashboard footer.
    """

    st.divider()

    left, right = st.columns(
        [3, 1],
    )

    with left:

        st.caption(
            "Institutional Strategy Comparison Platform V4"
        )

    with right:

        st.caption(
            "Production Analytics Dashboard"
        )


# ============================================================
# Main Application
# ============================================================

def main() -> None:
    """
    Application entry point.
    """

    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

    render_sidebar()

    # --------------------------------------------------------
    # Auto Load Reports
    # --------------------------------------------------------

    if not st.session_state.get(
        "reports_loaded",
        False,
    ):

        with st.spinner(
            "Loading latest reports..."
        ):

            try:

                load_reports(
                    DEFAULT_OUTPUT_FOLDER,
                )

            except Exception as exc:

                st.error(
                    f"Report loading failed: {exc}"
                )

                st.stop()

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    render_header()

    # --------------------------------------------------------
    # Load Data
    # --------------------------------------------------------

    refresh_token = Path(
        DEFAULT_OUTPUT_FOLDER
    ).stat().st_mtime

    (
        strategy_df,
        stock_df,
        portfolio_df,
    ) = load_dashboard_data(
        refresh_token,
    )

    validate_dashboard_data(
        strategy_df,
        stock_df,
        portfolio_df,
    )

    # --------------------------------------------------------
    # KPI Dashboard
    # --------------------------------------------------------

    render_dashboard_metrics(
        strategy_df,
        stock_df,
        portfolio_df,
    )

    # --------------------------------------------------------
    # Quick Analytics
    # --------------------------------------------------------

    render_quick_statistics(
        strategy_df,
        stock_df,
    )


    # --------------------------------------------------------
    # Platform Overview
    # --------------------------------------------------------

    render_platform_overview()

    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------

    render_generated_reports()

    # --------------------------------------------------------
    # Report Health
    # --------------------------------------------------------

    render_report_health()

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()

