"""
============================================================
Institutional Strategy Comparison Engine V3

Page 04 - Normalization

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from feature_engineering.feature_engine import FeatureEngine
from normalization.normalization_engine import NormalizationEngine

st.set_page_config(page_title="Normalization", page_icon="📏", layout="wide")

st.title("📏 Normalization")

uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

if st.button("Normalize Data"):
    feature_df = FeatureEngine(df).run()

    normalized = NormalizationEngine(feature_df).run()

    method = st.selectbox("Normalization Method", list(normalized.keys())[:-1])

    st.dataframe(normalized[method], use_container_width=True)
