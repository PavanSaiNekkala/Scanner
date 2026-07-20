"""
============================================================
Institutional Strategy Comparison Engine V3

Page 08 - Visualization

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from visualization.dashboards import DashboardEngine

st.set_page_config(page_title="Visualization", page_icon="📈", layout="wide")

st.title("📈 Visual Analytics")

uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)

else:
    df = pd.read_excel(uploaded_file)

if st.button("Generate Visualizations"):
    dashboard = DashboardEngine(df).run()

    st.success("Charts Generated")

    st.write(dashboard)
