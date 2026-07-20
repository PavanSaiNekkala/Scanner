"""
============================================================
Institutional Strategy Comparison Engine V3

Page 09 - Reports

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from reports.report_engine import ReportEngine

st.set_page_config(page_title="Reports", page_icon="📑", layout="wide")

st.title("📑 Reports")

uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)

else:
    df = pd.read_excel(uploaded_file)

if st.button("Generate Reports"):
    report = ReportEngine(df).run()

    st.success("Reports Generated")

    st.write(report)

    if "Excel File" in report:
        with open(report["Excel File"], "rb") as f:
            st.download_button(
                "Download Excel Report", data=f, file_name="Institutional_Report.xlsx"
            )
