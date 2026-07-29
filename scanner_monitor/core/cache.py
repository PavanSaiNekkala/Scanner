"""
core/cache.py
=============

Central caching utilities for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import pandas as pd
import streamlit as st

from core.config import (
    CACHE_TTL,
    ENABLE_CACHE,
)

T = TypeVar("T")

# =============================================================================
# Data Cache
# =============================================================================


def data_cache(
    ttl: int | None = CACHE_TTL,
    show_spinner: bool = False,
) -> Callable:
    """
    Wrapper around st.cache_data.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        if not ENABLE_CACHE:

            return func

        return st.cache_data(
            ttl=ttl,
            show_spinner=show_spinner,
        )(func)

    return decorator


# =============================================================================
# Resource Cache
# =============================================================================


def resource_cache(
    show_spinner: bool = False,
) -> Callable:
    """
    Wrapper around st.cache_resource.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        if not ENABLE_CACHE:

            return func

        return st.cache_resource(
            show_spinner=show_spinner,
        )(func)

    return decorator


# =============================================================================
# CSV Loader
# =============================================================================


@data_cache()
def load_csv(
    path: str,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load a CSV file with caching.
    """

    return pd.read_csv(
        path,
        **kwargs,
    )


# =============================================================================
# Excel Loader
# =============================================================================


@data_cache()
def load_excel(
    path: str,
    sheet_name: str | int = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load an Excel worksheet.
    """

    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        **kwargs,
    )


# =============================================================================
# Parquet Loader
# =============================================================================


@data_cache()
def load_parquet(
    path: str,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load a Parquet file.
    """

    return pd.read_parquet(
        path,
        **kwargs,
    )


# =============================================================================
# Generic Cache
# =============================================================================


@data_cache()
def cache_value(
    value: T,
) -> T:
    """
    Cache any serializable object.
    """

    return value


# =============================================================================
# Cache Management
# =============================================================================


def clear_data_cache() -> None:
    """
    Clear Streamlit data cache.
    """

    st.cache_data.clear()


def clear_resource_cache() -> None:
    """
    Clear Streamlit resource cache.
    """

    st.cache_resource.clear()


def clear_all_cache() -> None:
    """
    Clear every Streamlit cache.
    """

    clear_data_cache()

    clear_resource_cache()


# =============================================================================
# Cache Statistics
# =============================================================================


def cache_info() -> dict[str, Any]:
    """
    Return cache configuration.
    """

    return {

        "enabled": ENABLE_CACHE,

        "ttl": CACHE_TTL,

        "engine": "streamlit",

    }


# =============================================================================
# Memoization Decorator
# =============================================================================


def memoize(
    ttl: int | None = CACHE_TTL,
) -> Callable:
    """
    Alias for data_cache.
    """

    return data_cache(
        ttl=ttl,
    )