"""
components.py
=============

Reusable Streamlit UI components for the
Institutional Scanner Monitor.

These helpers provide a consistent look
and feel across every dashboard page.
"""

from __future__ import annotations

from typing import Iterable

import streamlit as st


# =============================================================================
# Page Section
# =============================================================================


def section(
    title: str,
    description: str | None = None,
) -> None:
    """
    Render a standardized page section.
    """

    st.markdown(f"## {title}")

    if description:

        st.caption(description)


# =============================================================================
# Divider
# =============================================================================


def divider() -> None:
    """
    Render a horizontal divider.
    """

    st.divider()


# =============================================================================
# Page Spacer
# =============================================================================


def spacer(
    height: int = 1,
) -> None:
    """
    Insert vertical spacing.
    """

    for _ in range(height):

        st.write("")


# =============================================================================
# Badge
# =============================================================================


def badge(
    text: str,
    color: str = "blue",
) -> None:
    """
    Render a small colored badge.
    """

    st.markdown(

        f"""
        <span style="
            background:{color};
            color:white;
            padding:4px 10px;
            border-radius:12px;
            font-size:0.8rem;
            font-weight:600;
        ">
            {text}
        </span>
        """,

        unsafe_allow_html=True,

    )


# =============================================================================
# Page Title
# =============================================================================


def page_title(
    title: str,
    subtitle: str | None = None,
) -> None:
    """
    Render the page title.
    """

    st.title(title)

    if subtitle:

        st.caption(subtitle)

# =============================================================================
# Information Box
# =============================================================================


def info_box(
    message: str,
) -> None:
    """
    Render an informational message.
    """

    st.info(message)


# =============================================================================
# Success Box
# =============================================================================


def success_box(
    message: str,
) -> None:
    """
    Render a success message.
    """

    st.success(message)


# =============================================================================
# Warning Box
# =============================================================================


def warning_box(
    message: str,
) -> None:
    """
    Render a warning message.
    """

    st.warning(message)


# =============================================================================
# Error Box
# =============================================================================


def error_box(
    message: str,
) -> None:
    """
    Render an error message.
    """

    st.error(message)


# =============================================================================
# Empty State
# =============================================================================


def empty_state(
    message: str = "No data available.",
) -> None:
    """
    Display a standardized empty state.
    """

    st.info(message)


# =============================================================================
# Key / Value List
# =============================================================================


def key_value_list(
    items: dict,
) -> None:
    """
    Render key/value pairs.
    """

    for key, value in items.items():

        left, right = st.columns([1, 2])

        with left:

            st.markdown(f"**{key}**")

        with right:

            st.write(value)


# =============================================================================
# Footer
# =============================================================================


def footer(
    text: str,
) -> None:
    """
    Render a page footer.
    """

    st.divider()

    st.caption(text)