"""
ui.components
=============

Reusable UI components for the
Institutional Scanner Monitor.

Provides standardized page
components used across every
dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class ComponentConfig:
    """
    Shared component configuration.
    """

    badge_radius: str = "12px"

    badge_padding: str = "4px 10px"

    badge_font_size: str = "0.80rem"

    badge_font_weight: str = "600"

    default_badge_color: str = "#2563EB"

    default_empty_message: str = (
        "No data available."
    )


CONFIG = ComponentConfig()

# =============================================================================
# HTML Renderer
# =============================================================================


def render_html(
    html: str,
) -> None:
    """
    Render HTML safely.
    """

    st.markdown(

        html,

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
    Display page title.
    """

    st.title(

        title,

    )

    if subtitle:

        st.caption(

            subtitle,

        )


# =============================================================================
# Section
# =============================================================================


def section(
    title: str,
    description: str | None = None,
) -> None:
    """
    Display section heading.
    """

    st.subheader(

        title,

    )

    if description:

        st.caption(

            description,

        )


# =============================================================================
# Divider
# =============================================================================


def divider() -> None:
    """
    Standard divider.
    """

    st.divider()


# =============================================================================
# Spacer
# =============================================================================


def spacer(
    lines: int = 1,
) -> None:
    """
    Vertical spacing.
    """

    for _ in range(

        max(

            0,

            lines,

        )

    ):

        st.write("")


# =============================================================================
# Badge
# =============================================================================


def badge(
    text: str,
    color: str = (
        CONFIG.default_badge_color
    ),
) -> None:
    """
    Display badge.
    """

    render_html(

        f"""
<span
style="
background:{color};
color:white;
padding:{CONFIG.badge_padding};
border-radius:{CONFIG.badge_radius};
font-size:{CONFIG.badge_font_size};
font-weight:{CONFIG.badge_font_weight};
">

{text}

</span>
"""

    )


# =============================================================================
# Message Components
# =============================================================================


def info_box(
    message: str,
) -> None:
    """
    Information message.
    """

    st.info(

        message,

    )


def success_box(
    message: str,
) -> None:
    """
    Success message.
    """

    st.success(

        message,

    )


def warning_box(
    message: str,
) -> None:
    """
    Warning message.
    """

    st.warning(

        message,

    )


def error_box(
    message: str,
) -> None:
    """
    Error message.
    """

    st.error(

        message,

    )

# =============================================================================
# Empty State
# =============================================================================


def empty_state(
    message: str = (
        CONFIG.default_empty_message
    ),
) -> None:
    """
    Display standardized
    empty state.
    """

    st.info(

        message,

    )


# =============================================================================
# Key / Value Components
# =============================================================================


def key_value(
    key: str,
    value: Any,
) -> None:
    """
    Display a single
    key/value pair.
    """

    left, right = st.columns(

        [1, 2],

    )

    with left:

        st.markdown(

            f"**{key}**",

        )

    with right:

        st.write(

            value,

        )


def key_value_list(
    items: dict[
        str,
        Any,
    ],
) -> None:
    """
    Display multiple
    key/value pairs.
    """

    if not items:

        empty_state(

            "Nothing to display.",

        )

        return

    for key, value in (

        items.items()

    ):

        key_value(

            key,

            value,

        )


# =============================================================================
# Information Panel
# =============================================================================


def information_panel(
    title: str,
    items: dict[
        str,
        Any,
    ],
) -> None:
    """
    Display an
    information panel.
    """

    st.subheader(

        title,

    )

    key_value_list(

        items,

    )


# =============================================================================
# Status Panel
# =============================================================================


def status_panel(
    title: str,
    status: str,
    description: str | None = None,
) -> None:
    """
    Display status panel.
    """

    st.subheader(

        title,

    )

    badge(

        status,

    )

    if description:

        st.caption(

            description,

        )


# =============================================================================
# Footer
# =============================================================================


def footer(
    text: str,
) -> None:
    """
    Display footer.
    """

    divider()

    st.caption(

        text,

    )


# =============================================================================
# Utility Helpers
# =============================================================================


def page_header(
    title: str,
    subtitle: str | None = None,
) -> None:
    """
    Standard page header.
    """

    page_title(

        title,

        subtitle,

    )

    divider()


def page_section(
    title: str,
    description: str | None = None,
) -> None:
    """
    Standard page section.
    """

    section(

        title,

        description,

    )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    "CONFIG",

    "render_html",

    "page_title",

    "page_header",

    "section",

    "page_section",

    "divider",

    "spacer",

    "badge",

    "info_box",

    "success_box",

    "warning_box",

    "error_box",

    "empty_state",

    "key_value",

    "key_value_list",

    "information_panel",

    "status_panel",

    "footer",

]