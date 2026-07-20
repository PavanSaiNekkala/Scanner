"""
============================================================
Institutional Strategy Comparison Engine V3

Tables Component

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd


class Tables:
    @staticmethod
    def dataframe(dataframe: pd.DataFrame, title: str):
        st.subheader(title)

        st.dataframe(dataframe, use_container_width=True)
