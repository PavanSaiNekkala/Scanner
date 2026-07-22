"""
cache.py
========

Caching utilities for the
Institutional Strategy Platform.

Provides:
- Cached file readers
- DataFrame utilities
- Session helpers
- Cache management
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

# ==========================================================
# Cached CSV Loader
# ==========================================================


@st.cache_data(show_spinner=False)
def read_csv(
    file: str | Path,
    modified_time: float,
) -> pd.DataFrame:
    """
    Cached CSV reader.

    modified_time forces cache refresh
    when the source file changes.
    """

    _ = modified_time

    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(file)

    return pd.read_csv(
        file,
        low_memory=False,
    )


# ==========================================================
# Cached Excel Loader
# ==========================================================


@st.cache_data(show_spinner=False)
def read_excel(
    file: str | Path,
    modified_time: float,
) -> dict[str, pd.DataFrame]:
    """
    Cached Excel reader.

    Returns all worksheets.
    """

    _ = modified_time

    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(file)

    excel = pd.ExcelFile(
        file,
    )

    sheets = {}

    for sheet in excel.sheet_names:
        sheets[sheet] = pd.read_excel(
            excel,
            sheet_name=sheet,
        )

    return {str(key): value for key, value in sheets.items()}


# ==========================================================
# Cached Parquet Loader
# ==========================================================


@st.cache_data(show_spinner=False)
def read_parquet(
    file: str | Path,
    modified_time: float,
) -> pd.DataFrame:
    """
    Cached parquet reader.
    """

    _ = modified_time

    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(file)

    return pd.read_parquet(
        file,
    )


# ==========================================================
# DataFrame Memory Usage
# ==========================================================


@st.cache_data(show_spinner=False)
def dataframe_memory(
    df: pd.DataFrame,
) -> float:
    """
    Memory usage in MB.
    """

    return round(
        float(
            df.memory_usage(
                deep=True,
            ).sum()
            / 1024
            / 1024
        ),
        2,
    )


# ==========================================================
# DataFrame Shape
# ==========================================================


@st.cache_data(show_spinner=False)
def dataframe_shape(
    df: pd.DataFrame,
) -> tuple[int, int]:
    """
    Return dataframe shape.
    """

    return df.shape


# ==========================================================
# Column Summary
# ==========================================================


@st.cache_data(show_spinner=False)
def column_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate column information.
    """

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
def numeric_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Numeric statistics summary.
    """

    numeric = df.select_dtypes(
        include="number",
    )

    if numeric.empty:
        return pd.DataFrame()

    return numeric.describe().T


# ==========================================================
# Session Helpers
# ==========================================================


def set_data(
    key: str,
    value,
) -> None:
    """
    Store session data.
    """

    st.session_state[key] = value


def get_data(
    key: str,
    default=None,
):
    """
    Retrieve session data.
    """

    return st.session_state.get(
        key,
        default,
    )


def has_data(
    key: str,
) -> bool:
    """
    Check session key.
    """

    return key in st.session_state


def remove_data(
    key: str,
) -> None:
    """
    Remove session key.
    """

    if key in st.session_state:
        del st.session_state[key]


def clear_session() -> None:
    """
    Clear Streamlit session.
    """

    st.session_state.clear()


# ==========================================================
# Cache Management
# ==========================================================


def clear_cache() -> None:
    """
    Clear all Streamlit caches.
    """

    st.cache_data.clear()

    st.cache_resource.clear()

    st.session_state.clear()


# ==========================================================
# Cached Filtering
# ==========================================================


@st.cache_data(show_spinner=False)
def filter_dataframe(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    """
    Filter dataframe.
    """

    return df[df[column] == value]


# ==========================================================
# Cached Sorting
# ==========================================================


@st.cache_data(show_spinner=False)
def sort_dataframe(
    df: pd.DataFrame,
    column: str,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Sort dataframe.
    """

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
) -> pd.DataFrame:
    """
    Return top N rows.
    """

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
) -> pd.DataFrame:
    """
    Return bottom N rows.
    """

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
) -> pd.DataFrame:
    """
    Generate correlation matrix.
    """

    numeric = df.select_dtypes(
        include="number",
    )

    return numeric.corr()


# ==========================================================
# Cached Missing Values
# ==========================================================


@st.cache_data(show_spinner=False)
def missing_values(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Return missing value counts.
    """

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


def cache_info() -> dict[str, object]:
    """
    Return cache/session information.
    """

    return {
        "Cached Objects": len(
            st.session_state,
        ),
        "Session Keys": list(
            st.session_state.keys(),
        ),
    }


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "read_csv",
    "read_excel",
    "read_parquet",
    "dataframe_memory",
    "dataframe_shape",
    "column_summary",
    "numeric_summary",
    "set_data",
    "get_data",
    "has_data",
    "remove_data",
    "clear_session",
    "clear_cache",
    "filter_dataframe",
    "sort_dataframe",
    "top_n",
    "bottom_n",
    "correlation_matrix",
    "missing_values",
    "cache_info",
]
