"""
============================================================
Institutional Strategy Comparison Engine V3

Sidebar Component

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import streamlit as st


class Sidebar:

    """
    Reusable Sidebar Component.
    """

    @staticmethod
    def render():

        st.sidebar.title(

            "Navigation"

        )

        st.sidebar.markdown(

            "---"

        )

        uploaded_file = st.sidebar.file_uploader(

            "Upload Strategy Report",

            type=[

                "csv",

                "xlsx"

            ]

        )

        normalization = st.sidebar.selectbox(

            "Normalization Method",

            [

                "Percentile",

                "Min-Max",

                "Z-Score",

                "Robust Z-Score",

                "Quantile"

            ]

        )

        recommendation = st.sidebar.selectbox(

            "Recommendation Model",

            [

                "Composite",

                "Institutional"

            ]

        )

        top_n = st.sidebar.slider(

            "Top Strategies",

            5,

            100,

            25

        )

        run = st.sidebar.button(

            "Run Analysis"

        )

        st.sidebar.markdown(

            "---"

        )

        return {

            "file":

                uploaded_file,

            "normalization":

                normalization,

            "recommendation":

                recommendation,

            "top_n":

                top_n,

            "run":

                run

        }