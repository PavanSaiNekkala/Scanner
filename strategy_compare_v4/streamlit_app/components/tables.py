"""
tables.py
=========

Reusable table components for the
Institutional Strategy Platform.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

# ----------------------------------------------------------
# Generic Table
# ----------------------------------------------------------


def show_table(
    df: pd.DataFrame,
    height: int = 600,
):
    """
    Display dataframe.
    """

    if df is None or df.empty:
        st.info("No data available.")

        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True,
    )


# ----------------------------------------------------------
# Styled Table
# ----------------------------------------------------------


def styled_table(
    df: pd.DataFrame,
    precision: int = 2,
):
    """
    Styled dataframe.
    """

    if df is None or df.empty:
        st.info("No data.")

        return

    styled = df.style.format(precision=precision)

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
    )


# ----------------------------------------------------------
# Top N Table
# ----------------------------------------------------------


def top_table(
    df: pd.DataFrame,
    score_column: str,
    n: int = 20,
):
    """
    Top ranking table.
    """

    if df is None or df.empty:
        return

    show_table(
        df.sort_values(
            score_column,
            ascending=False,
        ).head(n)
    )


# ----------------------------------------------------------
# Search Table
# ----------------------------------------------------------


def searchable_table(
    df: pd.DataFrame,
):
    """
    Searchable dataframe.
    """

    if df is None or df.empty:
        return

    search = st.text_input("Search")

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered.astype(str)
            .apply(
                lambda x: x.str.contains(
                    search,
                    case=False,
                    na=False,
                )
            )
            .any(axis=1)
        ]

    show_table(filtered)


# ----------------------------------------------------------
# Statistics
# ----------------------------------------------------------


def table_statistics(
    df: pd.DataFrame,
):
    """
    Dataset statistics.
    """

    if df is None or df.empty:
        return

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Rows",
            len(df),
        )

    with c2:
        st.metric(
            "Columns",
            len(df.columns),
        )

    with c3:
        st.metric(
            "Missing Values",
            int(df.isna().sum().sum()),
        )


# ----------------------------------------------------------
# Download
# ----------------------------------------------------------


def download_table(
    df: pd.DataFrame,
    filename: str,
):
    """
    Download dataframe.
    """

    csv = df.to_csv(
        index=False,
    )

    st.download_button(
        "📥 Download CSV",
        csv,
        filename,
        "text/csv",
    )
