"""
Institutional Strategy Comparison Platform
==========================================

Home Dashboard
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

SHEET_STRATEGY = "Strategy Ranking"
SHEET_STOCK = "Stock Rankings"
SHEET_PORTFOLIO = "Portfolio"

# ============================================================
# Dashboard Data
# ============================================================


def load_dashboard_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load dashboard datasets.
    """

    output_folder = DEFAULT_OUTPUT_FOLDER

    if not output_folder.exists():
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

    strategy_report = (
        output_folder
        /
        "Strategy_Comparison.xlsx"
    )

    stock_report = (
        output_folder
        /
        "Stock_Comparison.xlsx"
    )

    portfolio_report = (
        output_folder
        /
        "Portfolio_Report.xlsx"
    )


    strategy_workbook = load_excel(
        strategy_report,
        strategy_report.stat().st_mtime,
    )

    stock_workbook = load_excel(
        stock_report,
        stock_report.stat().st_mtime,
    )

    portfolio_workbook = load_excel(
        portfolio_report,
        portfolio_report.stat().st_mtime,
    )


    strategy_df = get_sheet(
        strategy_workbook,
        SHEET_STRATEGY,
    )

    stock_df = get_sheet(
        stock_workbook,
        SHEET_STOCK,
    )

    portfolio_df = get_sheet(
        portfolio_workbook,
        SHEET_PORTFOLIO,
    )

    return (
        strategy_df,
        stock_df,
        portfolio_df,
    )


# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render the application header.
    """

    st.title("📊 Institutional Strategy Comparison Platform")

    st.caption(
        "Institutional-grade strategy analytics, "
        "portfolio construction, robustness "
        "evaluation and reporting."
    )

    st.divider()

    if st.button("🔄 Refresh Latest Reports"):

        refresh_reports()

        st.rerun()


# ============================================================
# Dashboard Metrics
# ============================================================


def render_dashboard_metrics(
    strategy_df: pd.DataFrame,
    stock_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
) -> None:
    """
    Render dashboard KPI cards.
    """

    c1, c2, c3, c4 = st.columns(4)

    # --------------------------------------------------------
    # Strategies
    # --------------------------------------------------------

    with c1:
        strategies = (
            strategy_df["Strategy"].nunique()
            if "Strategy" in strategy_df.columns
            else len(strategy_df)
        )

        metric_card(
            "Strategies",
            strategies,
        )

    # --------------------------------------------------------
    # Stocks
    # --------------------------------------------------------

    with c2:
        stocks = stock_df["Stock"].nunique() if "Stock" in stock_df.columns else 0

        metric_card(
            "Stocks",
            stocks,
        )

    # --------------------------------------------------------
    # Portfolio Positions
    # --------------------------------------------------------

    with c3:
        metric_card(
            "Portfolio Positions",
            len(portfolio_df),
        )

    # --------------------------------------------------------
    # Report Status
    # --------------------------------------------------------

    with c4:
        report_status = (
            "Loaded"
            if st.session_state.get(
                "reports_loaded",
                False,
            )
            else "Not Loaded"
        )

        metric_card(
            "Reports",
            report_status,
        )

    st.divider()


# ============================================================
# Platform Overview
# ============================================================


def render_platform_overview() -> None:
    """
    Render platform overview and output folder.
    """

    left, right = st.columns(
        [2, 1],
    )

    # --------------------------------------------------------
    # Platform Features
    # --------------------------------------------------------

    with left:
        st.subheader("Platform Overview")

        st.markdown("""
This platform provides institutional-grade analytics for
quantitative strategy evaluation.

### Core Modules

- Strategy Comparison
- Stock Comparison
- Institutional Rankings
- Portfolio Construction
- Correlation Analysis
- Robustness Analysis
- Excel Report Generation

Use the sidebar to navigate through the available modules.
""")

    # --------------------------------------------------------
    # Output Folder
    # --------------------------------------------------------

    with right:
        st.subheader("Output Folder")

        output_folder = st.session_state.get("output_folder")

        if output_folder:
            st.success("Reports Loaded")

            st.code(
                output_folder,
                language="text",
            )

        else:
            st.info(
                "No output folder selected.\n\nLoad reports from the Data Loader page."
            )

    st.divider()


# ============================================================
# Generated Reports
# ============================================================


def render_generated_reports() -> None:
    """
    Display generated Excel reports.
    """

    st.subheader("Generated Reports")

    output_folder = st.session_state.get("output_folder")

    if not output_folder:
        st.info("Load reports from the Data Loader page.")

        return

    output_path = Path(
        output_folder,
    )

    files = sorted(
        output_path.glob(
            "*.xlsx",
        )
    )

    if not files:
        st.warning("No Excel reports found in the selected output folder.")

        return

    report_df = pd.DataFrame(
        {
            "Report": [file.name for file in files],
            "Size (KB)": [
                round(
                    file.stat().st_size / 1024,
                    2,
                )
                for file in files
            ],
            "Modified": [
                pd.to_datetime(
                    file.stat().st_mtime,
                    unit="s",
                ).strftime("%Y-%m-%d %H:%M")
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
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render application footer.
    """

    st.divider()

    st.caption("Institutional Strategy Comparison Platform V4")

    st.caption("Production-ready Institutional Strategy Analytics Dashboard")


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
    # Header
    # --------------------------------------------------------

    render_header()

    # --------------------------------------------------------
    # Load Dashboard Data
    # --------------------------------------------------------

    (
        strategy_df,
        stock_df,
        portfolio_df,
    ) = load_dashboard_data()

    # --------------------------------------------------------
    # KPI Dashboard
    # --------------------------------------------------------

    render_dashboard_metrics(
        strategy_df,
        stock_df,
        portfolio_df,
    )

    # --------------------------------------------------------
    # Platform Overview
    # --------------------------------------------------------

    render_platform_overview()

    # --------------------------------------------------------
    # Generated Reports
    # --------------------------------------------------------

    render_generated_reports()

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
