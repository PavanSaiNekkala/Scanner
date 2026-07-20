"""
cache.py
========

Caching utilities for the
Institutional Strategy Platform.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

# ==========================================================
# Cached CSV Loader
# ==========================================================


@st.cache_data(show_spinner=False)
def read_csv(file: str | Path) -> pd.DataFrame:
    """
    Cached CSV reader.
    """

    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(file)

    return pd.read_csv(file)


# ==========================================================
# Cached Excel Loader
# ==========================================================


@st.cache_data(show_spinner=False)
def read_excel(file: str | Path) -> dict[str, pd.DataFrame]:
    """
    Cached Excel reader.
    """

    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(file)

    excel = pd.ExcelFile(file)

    sheets = {}

    for sheet in excel.sheet_names:
        sheets[sheet] = pd.read_excel(
            excel,
            sheet_name=sheet,
        )

    return {str(k): v for k, v in sheets.items()}


# ==========================================================
# Cached Parquet Loader
# ==========================================================


@st.cache_data(show_spinner=False)
def read_parquet(file: str | Path) -> pd.DataFrame:
    """
    Cached parquet reader.
    """

    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(file)

    return pd.read_parquet(file)


# ==========================================================
# DataFrame Memory Usage
# ==========================================================


@st.cache_data(show_spinner=False)
def dataframe_memory(df: pd.DataFrame) -> float:
    """
    Memory usage in MB.
    """

    return round(
        float(df.memory_usage(deep=True).sum() / 1024 / 1024),
        2,
    )


# ==========================================================
# DataFrame Shape
# ==========================================================


@st.cache_data(show_spinner=False)
def dataframe_shape(df: pd.DataFrame):
    return df.shape


# ==========================================================
# Column Summary
# ==========================================================


@st.cache_data(show_spinner=False)
def column_summary(df: pd.DataFrame):
    return pd.DataFrame(
        {
            "Column": df.columns,
            "Type": df.dtypes.astype(str),
            "Missing": df.isna().sum().values,
            "Unique": df.nunique().values,
        }
    )


# ==========================================================
# Numeric Summary
# ==========================================================


@st.cache_data(show_spinner=False)
def numeric_summary(df: pd.DataFrame):
    numeric = df.select_dtypes(include="number")

    if numeric.empty:
        return pd.DataFrame()

    return numeric.describe().T


# ==========================================================
# Session Helpers
# ==========================================================


def set_data(
    key: str,
    value,
):
    st.session_state[key] = value


def get_data(
    key: str,
    default=None,
):
    return st.session_state.get(
        key,
        default,
    )


def has_data(
    key: str,
):
    return key in st.session_state


def remove_data(
    key: str,
):
    if key in st.session_state:
        del st.session_state[key]


def clear_session():
    st.session_state.clear()


# ==========================================================
# Cache Management
# ==========================================================


def clear_cache():
    """
    Clear all Streamlit caches.
    """

    st.cache_data.clear()

    st.cache_resource.clear()


# ==========================================================
# Cached Filtering
# ==========================================================


@st.cache_data(show_spinner=False)
def filter_dataframe(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    return df[df[column] == value]


# ==========================================================
# Cached Sorting
# ==========================================================


@st.cache_data(show_spinner=False)
def sort_dataframe(
    df: pd.DataFrame,
    column: str,
    ascending=False,
):
    return df.sort_values(
        column,
        ascending=ascending,
    )


# ==========================================================
# Cached Top N
# ==========================================================


@st.cache_data(show_spinner=False)
def top_n(
    df: pd.DataFrame,
    column: str,
    n: int = 20,
):
    return df.sort_values(
        column,
        ascending=False,
    ).head(n)


# ==========================================================
# Cached Bottom N
# ==========================================================


@st.cache_data(show_spinner=False)
def bottom_n(
    df: pd.DataFrame,
    column: str,
    n: int = 20,
):
    return df.sort_values(
        column,
        ascending=True,
    ).head(n)


# ==========================================================
# Cached Correlation
# ==========================================================


@st.cache_data(show_spinner=False)
def correlation_matrix(
    df: pd.DataFrame,
):
    numeric = df.select_dtypes(include="number")

    return numeric.corr()


# ==========================================================
# Cached Missing Values
# ==========================================================


@st.cache_data(show_spinner=False)
def missing_values(
    df: pd.DataFrame,
):
    return (
        df.isna()
        .sum()
        .sort_values(
            ascending=False,
        )
    )


# ==========================================================
# Cache Information
# ==========================================================


def cache_info():
    return {
        "Cached Objects": len(st.session_state),
        "Session Keys": list(st.session_state.keys()),
    }
