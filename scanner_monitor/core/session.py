"""
core/session.py
===============

Central session state management for the
Institutional Scanner Monitor.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

# =============================================================================
# Default Session State
# =============================================================================

DEFAULT_SESSION = {

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    "app_loaded": False,

    "last_refresh": None,

    "current_page": None,

    # ---------------------------------------------------------
    # Scanner
    # ---------------------------------------------------------

    "selected_symbol": None,

    "selected_sector": "All",

    "selected_industry": "All",

    "selected_signal": "All",

    "search_text": "",

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------

    "theme": "light",

    "sidebar_expanded": True,

    # ---------------------------------------------------------
    # Portfolio
    # ---------------------------------------------------------

    "portfolio_loaded": False,

    "holdings_loaded": False,

    # ---------------------------------------------------------
    # Downloads
    # ---------------------------------------------------------

    "download_format": "csv",

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------

    "min_score": 0.0,

    "max_score": 100.0,

}


# =============================================================================
# Initialization
# =============================================================================


def initialize() -> None:
    """
    Initialize the complete session state.
    """

    for key, value in DEFAULT_SESSION.items():

        st.session_state.setdefault(

            key,

            value,

        )


# =============================================================================
# Reset
# =============================================================================


def reset() -> None:
    """
    Reset session to defaults.
    """

    st.session_state.clear()

    initialize()


# =============================================================================
# Getter
# =============================================================================


def get(

    key: str,

    default: Any = None,

) -> Any:
    """
    Retrieve a session value.
    """

    return st.session_state.get(

        key,

        default,

    )


# =============================================================================
# Setter
# =============================================================================


def set(

    key: str,

    value: Any,

) -> None:
    """
    Store a session value.
    """

    st.session_state[key] = value


# =============================================================================
# Exists
# =============================================================================


def exists(

    key: str,

) -> bool:
    """
    Check if a key exists.
    """

    return key in st.session_state


# =============================================================================
# Delete
# =============================================================================


def delete(

    key: str,

) -> None:
    """
    Remove a key.
    """

    if key in st.session_state:

        del st.session_state[key]


# =============================================================================
# Update
# =============================================================================


def update(

    values: dict[str, Any],

) -> None:
    """
    Update multiple session values.
    """

    st.session_state.update(

        values,

    )


# =============================================================================
# Toggle
# =============================================================================


def toggle(

    key: str,

) -> bool:
    """
    Toggle a boolean session value.

    Returns
    -------
    bool
        Updated value.
    """

    value = bool(

        st.session_state.get(

            key,

            False,

        )

    )

    st.session_state[key] = not value

    return st.session_state[key]


# =============================================================================
# Export
# =============================================================================


def to_dict() -> dict[str, Any]:
    """
    Export the current session.
    """

    return dict(

        st.session_state,

    )


# =============================================================================
# Import
# =============================================================================


def from_dict(

    values: dict[str, Any],

) -> None:
    """
    Restore session values.
    """

    st.session_state.update(

        values,

    )


# =============================================================================
# Convenience
# =============================================================================


def refresh_timestamp() -> None:
    """
    Store the current refresh timestamp.
    """

    from datetime import datetime

    st.session_state["last_refresh"] = datetime.now()