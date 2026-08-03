"""
scanner_monitor.core.version
============================

Application version and build metadata for the
Institutional Scanner Monitor.

This module centralizes application version information,
release metadata, runtime details, and helper functions
used throughout the application.
"""

from __future__ import annotations

from datetime import datetime
from platform import platform
from platform import python_version
from typing import Final

__all__ = [
    # Application
    "APP_NAME",
    "APP_SHORT_NAME",
    "VERSION",
    "VERSION_MAJOR",
    "VERSION_MINOR",
    "VERSION_PATCH",
    # Release
    "RELEASE_STAGE",
    "BUILD_NUMBER",
    "BUILD_DATE",
    "RELEASE_DATE",
    # Author
    "AUTHOR",
    "ORGANIZATION",
    "LICENSE",
    # URLs
    "DOCUMENTATION",
    "GITHUB",
    "WEBSITE",
    # Runtime
    "PYTHON_VERSION",
    "PLATFORM",
    # Version
    "FULL_VERSION",
    # Helpers
    "build_timestamp",
    "version_info",
    "version_string",
    "about",
]

# =============================================================================
# Application
# =============================================================================

APP_NAME: Final[str] = "Institutional Scanner Monitor"

APP_SHORT_NAME: Final[str] = "Scanner Monitor"

VERSION_MAJOR: Final[int] = 1

VERSION_MINOR: Final[int] = 0

VERSION_PATCH: Final[int] = 0

VERSION: Final[str] = (
    f"{VERSION_MAJOR}."
    f"{VERSION_MINOR}."
    f"{VERSION_PATCH}"
)

# =============================================================================
# Release
# =============================================================================

RELEASE_STAGE: Final[str] = "Production"

BUILD_NUMBER: Final[int] = 1

BUILD_DATE: Final[str] = "2026-07-29"

RELEASE_DATE: Final[str] = "2026-07-29"

# =============================================================================
# Author
# =============================================================================

AUTHOR: Final[str] = "Pavan Sai"

ORGANIZATION: Final[str] = "Institutional Scanner"

LICENSE: Final[str] = "MIT"

# =============================================================================
# URLs
# =============================================================================

DOCUMENTATION: Final[str] = ""

GITHUB: Final[str] = ""

WEBSITE: Final[str] = ""

# =============================================================================
# Runtime
# =============================================================================

PYTHON_VERSION: Final[str] = python_version()

PLATFORM: Final[str] = platform()

# =============================================================================
# Display Version
# =============================================================================

FULL_VERSION: Final[str] = (
    f"{VERSION} ({RELEASE_STAGE})"
)

# =============================================================================
# Helpers
# =============================================================================


def build_timestamp() -> str:
    """
    Return the current local timestamp.

    Returns
    -------
    str
        Timestamp formatted as
        YYYY-MM-DD HH:MM:SS.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S",
    )


def version_info() -> dict[str, str]:
    """
    Return application version metadata.

    Returns
    -------
    dict[str, str]
        Dictionary containing build,
        runtime, and release information.
    """

    return {
        "application": APP_NAME,
        "short_name": APP_SHORT_NAME,
        "version": VERSION,
        "full_version": FULL_VERSION,
        "release_stage": RELEASE_STAGE,
        "build_number": str(BUILD_NUMBER),
        "build_date": BUILD_DATE,
        "release_date": RELEASE_DATE,
        "author": AUTHOR,
        "organization": ORGANIZATION,
        "license": LICENSE,
        "python": PYTHON_VERSION,
        "platform": PLATFORM,
        "documentation": DOCUMENTATION,
        "github": GITHUB,
        "website": WEBSITE,
    }


def version_string() -> str:
    """
    Return the application display version.

    Returns
    -------
    str
    """

    return (
        f"{APP_NAME} "
        f"v{VERSION}"
    )


def about() -> str:
    """
    Return a human-readable
    application summary.

    Returns
    -------
    str
    """

    return (
        f"{APP_NAME}\n"
        f"Version      : {VERSION}\n"
        f"Release      : {RELEASE_STAGE}\n"
        f"Build        : {BUILD_NUMBER}\n"
        f"Build Date   : {BUILD_DATE}\n"
        f"Release Date : {RELEASE_DATE}\n"
        f"Author       : {AUTHOR}\n"
        f"Organization : {ORGANIZATION}\n"
        f"License      : {LICENSE}\n"
        f"Python       : {PYTHON_VERSION}\n"
        f"Platform     : {PLATFORM}"
    )