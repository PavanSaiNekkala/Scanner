"""
============================================================
Institutional Strategy Comparison Engine V3

Page 10 - Settings

============================================================
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(

    page_title="Settings",

    page_icon="⚙️",

    layout="wide"

)

st.title("⚙️ Settings")

st.subheader("Application Configuration")

normalization = st.selectbox(

    "Default Normalization",

    [

        "Percentile",

        "Min-Max",

        "Z-Score",

        "Robust Z-Score",

        "Quantile"

    ]

)

recommendation = st.selectbox(

    "Recommendation Model",

    [

        "Composite",

        "Institutional"

    ]

)

top_n = st.slider(

    "Default Top N",

    5,

    100,

    25

)

if st.button("Save Settings"):

    st.success("Settings saved successfully.")

st.info(
    "Configuration persistence can be implemented "
    "later using config.py or a JSON/YAML file."
)