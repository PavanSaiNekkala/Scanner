"""
============================================================
Institutional Strategy Comparison Engine V3

Page 02 - Relationships

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from relationships.relationship_engine import RelationshipEngine

st.set_page_config(
    page_title="Relationships",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 Relationships")

uploaded_file = st.file_uploader(
    "Upload CSV / Excel",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.stop()

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

if st.button("Run Relationships"):

    engine = RelationshipEngine(df)

    result = engine.generate()

    if isinstance(result, dict):

        for name, dataframe in result.items():

            st.subheader(name)

            st.dataframe(
                dataframe,
                use_container_width=True
            )

    else:

        st.dataframe(
            result,
            use_container_width=True
        )