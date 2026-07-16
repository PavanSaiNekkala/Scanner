"""
============================================================
Institutional Strategy Comparison Engine V3

Charts Component

============================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd


class Charts:

    @staticmethod
    def recommendation_distribution(

        dataframe: pd.DataFrame

    ):

        st.bar_chart(

            dataframe["Recommendation"]

            .value_counts()

        )

    @staticmethod
    def composite_scores(

        dataframe: pd.DataFrame

    ):

        st.line_chart(

            dataframe

            .sort_values(

                "Composite Score"

            )["Composite Score"]

        )