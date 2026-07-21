"""
Typography
"""

import streamlit as st


def page_title(
    title,
    caption=None,
):

    st.title(title)

    if caption:
        st.caption(caption)
