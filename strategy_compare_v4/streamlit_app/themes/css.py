"""
Global CSS
"""

import streamlit as st


def load_css():

    st.markdown(
        """
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

[data-testid="stSidebar"]{
    width:260px;
}

.stMetric{
    border-radius:10px;
    border:1px solid #dee2e6;
    padding:12px;
}

div[data-testid="stDataFrame"]{
    border-radius:8px;
}

</style>
""",
        unsafe_allow_html=True,
    )
