"""
============================================================
Institutional Strategy Comparison Engine V3

Metrics Component

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd


class Metrics:
    """
    Dashboard KPI Metrics
    """

    @staticmethod
    def render(df: pd.DataFrame):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Strategies", len(df))

        with col2:
            st.metric("Average Score", round(df["Composite Score"].mean(), 2))

        with col3:
            st.metric("Best Score", round(df["Composite Score"].max(), 2))

        with col4:
            st.metric("Strong Buy", int((df["Recommendation"] == "STRONG BUY").sum()))
