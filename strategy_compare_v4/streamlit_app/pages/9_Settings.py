"""
Settings
========

Institutional Strategy Platform Settings
"""

from __future__ import annotations

import platform
from pathlib import Path

import pandas as pd
import streamlit as st
from services.loader import clear_session
from themes import apply_theme

st.set_page_config(
    page_title="Strategies",
    page_icon="📈",
    layout="wide",
)
apply_theme()

st.set_page_config(
    page_title="Settings",
    page_icon="⚙",
    layout="wide",
)

st.title("⚙ Settings")

st.caption("Application configuration, diagnostics and maintenance.")

# ==========================================================
# Session Overview
# ==========================================================

reports_loaded = st.session_state.get(
    "reports_loaded",
    False,
)

output_folder = st.session_state.get(
    "output_folder",
    "output",
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Reports",
        "Loaded" if reports_loaded else "Not Loaded",
    )

with c2:
    st.metric(
        "Output Folder",
        Path(output_folder).name,
    )

with c3:
    st.metric(
        "Version",
        "v4.0",
    )

# ==========================================================
# Output Directory
# ==========================================================

st.divider()

st.subheader("Output Directory")

folder = st.text_input(
    "Output Folder",
    value=output_folder,
)

if Path(folder).exists():
    st.success("Directory exists.")

else:
    st.warning("Directory not found.")

# ==========================================================
# Maintenance
# ==========================================================

st.divider()

st.subheader("Maintenance")

left, right = st.columns(2)

with left:
    if st.button(
        "🧹 Clear Cache",
        use_container_width=True,
    ):
        st.cache_data.clear()

        st.success("Cache cleared.")

with right:
    if st.button(
        "🔄 Reset Session",
        use_container_width=True,
    ):
        clear_session()

        st.success("Session reset.")

# ==========================================================
# Environment
# ==========================================================

st.divider()

st.subheader("Environment")

env = pd.DataFrame(
    {
        "Property": [
            "Application",
            "Version",
            "Framework",
            "Streamlit",
            "Python",
            "Platform",
        ],
        "Value": [
            "Institutional Strategy Platform",
            "4.0",
            "Streamlit",
            st.__version__,
            platform.python_version(),
            platform.system(),
        ],
    }
)

st.dataframe(
    env,
    hide_index=True,
    use_container_width=True,
)

# ==========================================================
# Reports
# ==========================================================

st.divider()

st.subheader("Loaded Reports")

reports = pd.DataFrame(
    {
        "Report": [
            "Strategy",
            "Stock",
            "Leaderboard",
            "Portfolio",
            "Robustness",
            "Correlation",
            "Final",
        ],
        "Status": [
            "Loaded" if "strategy_report" in st.session_state else "Not Loaded",
            "Loaded" if "stock_report" in st.session_state else "Not Loaded",
            "Loaded" if "leaderboard_report" in st.session_state else "Not Loaded",
            "Loaded" if "portfolio_report" in st.session_state else "Not Loaded",
            "Loaded" if "robustness_report" in st.session_state else "Not Loaded",
            "Loaded" if "correlation_report" in st.session_state else "Not Loaded",
            "Loaded" if "final_report" in st.session_state else "Not Loaded",
        ],
    }
)

st.dataframe(
    reports,
    hide_index=True,
    use_container_width=True,
)

# ==========================================================
# About
# ==========================================================

st.divider()

with st.expander(
    "About Institutional Strategy Platform",
    expanded=False,
):
    st.markdown("""
### Institutional Strategy Comparison Platform

**Version:** 4.0

#### Modules

- Strategy Comparison
- Stock Comparison
- Institutional Leaderboards
- Portfolio Construction
- Correlation Analysis
- Robustness Analysis
- Executive Dashboard
- Excel Report Generation

#### Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
""")
