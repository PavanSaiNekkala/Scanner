"""
Institutional Strategy Comparison Platform
==========================================

Home Dashboard

Author : Pavan Sai Nekkala
Version: 4.0
"""

from pathlib import Path

import pandas as pd
import streamlit as st
from components.cards import metric_card
from components.sidebar import render_sidebar

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
# Initialize Session State
# -------------------------------------------------------

DEFAULT_STATE = {
    "strategy_df": None,
    "stock_df": None,
    "leaderboard_df": None,
    "portfolio_df": None,
    "correlation_df": None,
    "robustness_df": None,
    "reports_loaded": False,
    "output_folder": None,
}

for key, value in DEFAULT_STATE.items():
    st.session_state.setdefault(key, value)

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
# Dashboard Metrics
# -------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card(
        "Strategies",
        (
            st.session_state.strategy_df["Strategy"].nunique()
            if st.session_state.strategy_df is not None
            else 0
        ),
    )

with c2:
    metric_card(
        "Stocks",
        (
            st.session_state.stock_df["Stock"].nunique()
            if st.session_state.stock_df is not None
            else 0
        ),
    )

with c3:
    metric_card(
        "Portfolio",
        (
            len(st.session_state.portfolio_df)
            if st.session_state.portfolio_df is not None
            else 0
        ),
    )

with c4:
    metric_card(
        "Reports",
        ("Loaded" if st.session_state.reports_loaded else "Not Loaded"),
    )

st.divider()

# -------------------------------------------------------
# Quick Summary
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

    if st.session_state.output_folder is None:
        st.info("No output folder selected.")

    else:
        st.success(str(st.session_state.output_folder))

st.divider()

# -------------------------------------------------------
# Recent Reports
# -------------------------------------------------------

st.subheader("Generated Reports")

output = st.session_state.output_folder

if output is not None:
    files = sorted(Path(output).glob("*.xlsx"))

    if files:
        report_df = pd.DataFrame(
            {
                "Report": [f.name for f in files],
                "Size (KB)": [round(f.stat().st_size / 1024, 2) for f in files],
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
    st.info("Load an output directory first.")
