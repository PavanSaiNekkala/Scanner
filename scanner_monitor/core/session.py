"""
scanner_monitor.core.session
============================

Central Streamlit session state management for the
Institutional Scanner Monitor.

This module provides a consistent interface for initializing,
reading, updating, exporting, and resetting Streamlit session
state while preserving backward compatibility.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Final

import streamlit as st

__all__ = [
    "DEFAULT_SESSION",
    "initialize",
    "reset",
    "get",
    "set",
    "exists",
    "delete",
    "update",
    "toggle",
    "to_dict",
    "from_dict",
    "refresh_timestamp",
]

# =============================================================================
# Default Session State
# =============================================================================

DEFAULT_SESSION: Final[dict[str, Any]] = {

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------

    "app_loaded": False,
    "last_refresh": None,
    "current_page": None,

    # -------------------------------------------------------------------------
    # Scanner
    # -------------------------------------------------------------------------

    "selected_symbol": None,
    "selected_sector": "All",
    "selected_industry": "All",
    "selected_signal": "All",
    "search_text": "",

    # -------------------------------------------------------------------------
    # Dashboard
    # -------------------------------------------------------------------------

    "theme": "light",
    "sidebar_expanded": True,

    # -------------------------------------------------------------------------
    # Portfolio
    # -------------------------------------------------------------------------

    "portfolio_loaded": False,
    "holdings_loaded": False,

    # -------------------------------------------------------------------------
    # Downloads
    # -------------------------------------------------------------------------

    "download_format": "csv",

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------

    "min_score": 0.0,
    "max_score": 100.0,
}

# =============================================================================
# Initialization
# =============================================================================


def initialize() -> None:
    """
    Initialize all default session state values.

    Existing values are preserved.
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
    Reset the entire session state to defaults.
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

    Parameters
    ----------
    key
        Session key.

    default
        Value returned if the key does not exist.
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
    Return True if the session key exists.
    """

    return key in st.session_state


# =============================================================================
# Delete
# =============================================================================


def delete(
    key: str,
) -> None:
    """
    Remove a session key if it exists.
    """

    st.session_state.pop(
        key,
        None,
    )


# =============================================================================
# Update
# =============================================================================


def update(
    values: dict[str, Any],
) -> None:
    """
    Update multiple session values.
    """

    if values:
        st.session_state.update(values)


# =============================================================================
# Toggle
# =============================================================================


def toggle(
    key: str,
) -> bool:
    """
    Toggle a boolean session value.

    If the key does not exist,
    False is assumed.

    Returns
    -------
    bool
        Updated value.
    """

    new_value = not bool(
        st.session_state.get(
            key,
            False,
        )
    )

    st.session_state[key] = new_value

    return new_value


# =============================================================================
# Export
# =============================================================================


def to_dict() -> dict[str, Any]:
    """
    Export the complete session state.
    """

    return dict(st.session_state)


# =============================================================================
# Import
# =============================================================================


def from_dict(
    values: dict[str, Any],
) -> None:
    """
    Restore session state from a dictionary.
    """

    if values:
        st.session_state.update(values)


# =============================================================================
# Convenience
# =============================================================================


def refresh_timestamp() -> None:
    """
    Update the session refresh timestamp.
    """

    st.session_state["last_refresh"] = datetime.now()