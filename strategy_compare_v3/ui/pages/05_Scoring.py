"""
============================================================
Institutional Strategy Comparison Engine V3

Page 05 - Scoring

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from feature_engineering.feature_engine import FeatureEngine
from normalization.normalization_engine import NormalizationEngine
from scoring.scoring_engine import ScoringEngine

st.set_page_config(page_title="Scoring", page_icon="🏆", layout="wide")

st.title("🏆 Strategy Scoring")

uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

if st.button("Generate Scores"):
    feature_df = FeatureEngine(df).run()

    normalized = NormalizationEngine(feature_df).run()["Percentile"]

    scores = ScoringEngine(normalized).run()

    st.dataframe(scores, use_container_width=True)
