"""
Institutional Strategy Comparison Platform
==========================================

Home Dashboard
"""

from pathlib import Path

import pandas as pd
import streamlit as st
from components.cards import metric_card
from components.sidebar import render_sidebar
from services.loader import get_sheet
from themes import apply_theme

st.set_page_config(
    page_title="Strategies",
    page_icon="📈",
    layout="wide",
)
apply_theme()

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="Institutional Strategy Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

render_sidebar()

# -------------------------------------------------------
# Header
# -------------------------------------------------------

st.title("📊 Institutional Strategy Comparison Platform")

st.caption(
    "Institutional-grade strategy analytics, portfolio construction, "
    "robustness evaluation and reporting."
)

st.divider()

# -------------------------------------------------------
# Read Loaded Reports
# -------------------------------------------------------

strategy_df = (
    get_sheet(
        st.session_state.strategy_report,
        "Strategy Ranking",
    )
    if st.session_state.get("reports_loaded", False)
    else pd.DataFrame()
)

stock_df = (
    get_sheet(
        st.session_state.stock_report,
        "Stock Rankings",
    )
    if st.session_state.get("reports_loaded", False)
    else pd.DataFrame()
)

portfolio_df = (
    get_sheet(
        st.session_state.portfolio_report,
        "Portfolio",
    )
    if st.session_state.get("reports_loaded", False)
    else pd.DataFrame()
)

# -------------------------------------------------------
# Dashboard Metrics
# -------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

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

with c2:
    stocks = stock_df["Stock"].nunique() if "Stock" in stock_df.columns else 0

    metric_card(
        "Stocks",
        stocks,
    )

with c3:
    metric_card(
        "Portfolio",
        len(portfolio_df),
    )

with c4:
    metric_card(
        "Reports",
        (
            "Loaded"
            if st.session_state.get(
                "reports_loaded",
                False,
            )
            else "Not Loaded"
        ),
    )

st.divider()

# -------------------------------------------------------
# Platform Overview
# -------------------------------------------------------

left, right = st.columns([2, 1])

with left:
    st.subheader("Platform Overview")

    st.markdown("""
This platform provides:

- Strategy Comparison
- Stock Comparison
- Institutional Rankings
- Portfolio Construction
- Correlation Analysis
- Robustness Analysis
- Excel Report Generation

Use the sidebar to navigate through the analytics modules.
""")

with right:
    st.subheader("Output Folder")

    output_folder = st.session_state.get("output_folder")

    if output_folder:
        st.success(output_folder)

    else:
        st.info("No output folder selected.")

st.divider()

# -------------------------------------------------------
# Generated Reports
# -------------------------------------------------------

st.subheader("Generated Reports")

output = st.session_state.get("output_folder")

if output:
    files = sorted(Path(output).glob("*.xlsx"))

    if files:
        report_df = pd.DataFrame(
            {
                "Report": [f.name for f in files],
                "Size (KB)": [
                    round(
                        f.stat().st_size / 1024,
                        2,
                    )
                    for f in files
                ],
            }
        )

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.warning("No reports found.")

else:
    st.info("Load reports from the Data Load page.")
