"""
Settings
========

Institutional Strategy Platform Settings
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from services.loader import clear_session

st.set_page_config(
    page_title="Settings",
    page_icon="⚙",
    layout="wide",
)

st.title("⚙ Settings")

st.caption("Application configuration and maintenance.")

# ==========================================================
# Session
# ==========================================================

st.header("Session")

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Reports Loaded",
        (
            "Yes"
            if st.session_state.get(
                "reports_loaded",
                False,
            )
            else "No"
        ),
    )

with c2:
    st.metric(
        "Output Folder",
        st.session_state.get(
            "output_folder",
            "Not Selected",
        ),
    )

# ==========================================================
# Output Folder
# ==========================================================

st.divider()

st.header("Output Directory")

folder = st.text_input(
    "Default Output Folder",
    value=st.session_state.get(
        "output_folder",
        "output",
    ),
)

if Path(folder).exists():
    st.success("Directory Exists")

else:
    st.warning("Directory Not Found")

# ==========================================================
# Cache
# ==========================================================

st.divider()

st.header("Cache")

left, right = st.columns(2)

with left:
    if st.button(
        "Clear Streamlit Cache",
        use_container_width=True,
    ):
        st.cache_data.clear()

        st.success("Cache Cleared")

with right:
    if st.button(
        "Reset Session",
        use_container_width=True,
    ):
        clear_session()

        st.success("Session Reset")

# ==========================================================
# Environment
# ==========================================================

st.divider()

st.header("Environment")

st.json(
    {
        "Python": st.__version__,
        "Framework": "Streamlit",
        "Application": "Institutional Strategy Platform",
        "Version": "4.0",
    }
)

# ==========================================================
# Theme
# ==========================================================

st.divider()

st.header("Dashboard Preferences")

theme = st.selectbox(
    "Theme",
    [
        "System",
        "Light",
        "Dark",
    ],
)

layout = st.selectbox(
    "Layout",
    [
        "Wide",
        "Centered",
    ],
)

st.info("Theme changes are applied from Streamlit configuration.")

# ==========================================================
# Statistics
# ==========================================================

st.divider()

st.header("Session Statistics")

stats = {
    "Strategy Report": "Loaded" if "strategy_report" in st.session_state else "No",
    "Stock Report": "Loaded" if "stock_report" in st.session_state else "No",
    "Leaderboard Report": (
        "Loaded" if "leaderboard_report" in st.session_state else "No"
    ),
    "Portfolio Report": "Loaded" if "portfolio_report" in st.session_state else "No",
    "Robustness Report": "Loaded" if "robustness_report" in st.session_state else "No",
    "Correlation Report": (
        "Loaded" if "correlation_report" in st.session_state else "No"
    ),
    "Final Report": "Loaded" if "final_report" in st.session_state else "No",
}

st.dataframe(
    stats,
    use_container_width=True,
)

# ==========================================================
# About
# ==========================================================

st.divider()

st.header("About")

st.markdown("""
### Institutional Strategy Comparison Platform

Version **4.0**

Features:

- Strategy Comparison
- Stock Comparison
- Institutional Rankings
- Portfolio Construction
- Correlation Analysis
- Robustness Analysis
- Interactive Dashboards
- Excel Report Generation

Developed using:

- Streamlit
- Pandas
- Plotly
- NumPy
""")
