"""
============================================================
Institutional Strategy Comparison Engine V3

Page 07 - Optimization

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from feature_engineering.feature_engine import FeatureEngine
from normalization.normalization_engine import NormalizationEngine
from scoring.scoring_engine import ScoringEngine
from optimization.optimization_engine import OptimizationEngine

st.set_page_config(page_title="Optimization", page_icon="⚡", layout="wide")

st.title("⚡ Strategy Optimization")

uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

if st.button("Run Optimization"):
    feature_df = FeatureEngine(df).run()

    normalized = NormalizationEngine(feature_df).run()["Percentile"]

    scored = ScoringEngine(normalized).run()

    # ---------------------------------------------
    # Example Objective Function
    # ---------------------------------------------

    def objective(data):
        return data["Composite Score"].mean()

    parameter_space = {
        "Edge Weight": [0.10, 0.15, 0.20],
        "Risk Weight": [0.10, 0.15, 0.20],
    }

    scenarios = {"Baseline": lambda x: x, "Stress Test": lambda x: x}

    optimization = OptimizationEngine(scored, objective).run(parameter_space, scenarios)

    st.success("Optimization Completed")

    for section, result in optimization.items():
        st.subheader(section)

        st.write(result)
