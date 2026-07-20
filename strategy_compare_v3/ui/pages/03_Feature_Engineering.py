"""
============================================================
Institutional Strategy Comparison Engine V3

Page 03 - Feature Engineering

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from feature_engineering.feature_engine import FeatureEngine

st.set_page_config(page_title="Feature Engineering", page_icon="⚙️", layout="wide")

st.title("⚙️ Feature Engineering")

uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

if st.button("Generate Features"):
    engineered = FeatureEngine(df).run()

    st.success("Features Generated")

    st.dataframe(engineered, use_container_width=True)
