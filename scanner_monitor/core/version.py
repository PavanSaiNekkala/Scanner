"""
core/version.py
===============

Application version and build metadata
for the Institutional Scanner Monitor.
"""

from __future__ import annotations

from datetime import datetime
from platform import platform
from platform import python_version

# =============================================================================
# Application
# =============================================================================

APP_NAME = "Institutional Scanner Monitor"

APP_SHORT_NAME = "Scanner Monitor"

VERSION = "1.0.0"

VERSION_MAJOR = 1

VERSION_MINOR = 0

VERSION_PATCH = 0

# =============================================================================
# Release
# =============================================================================

RELEASE_STAGE = "Production"

BUILD_NUMBER = 1

BUILD_DATE = "2026-07-29"

RELEASE_DATE = "2026-07-29"

# =============================================================================
# Author
# =============================================================================

AUTHOR = "Pavan Sai"

ORGANIZATION = "Institutional Scanner"

LICENSE = "MIT"

# =============================================================================
# URLs
# =============================================================================

DOCUMENTATION = ""

GITHUB = ""

WEBSITE = ""

# =============================================================================
# Python
# =============================================================================

PYTHON_VERSION = python_version()

PLATFORM = platform()

# =============================================================================
# Version String
# =============================================================================

FULL_VERSION = (

    f"{VERSION}"

    f" ({RELEASE_STAGE})"

)

# =============================================================================
# Runtime
# =============================================================================


def build_timestamp() -> str:
    """
    Current timestamp.
    """

    return datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S",

    )


def version_info() -> dict[str, str]:
    """
    Return version metadata.
    """

    return {

        "application": APP_NAME,

        "version": VERSION,

        "release_stage": RELEASE_STAGE,

        "build_number": str(BUILD_NUMBER),

        "build_date": BUILD_DATE,

        "release_date": RELEASE_DATE,

        "author": AUTHOR,

        "organization": ORGANIZATION,

        "python": PYTHON_VERSION,

        "platform": PLATFORM,

    }


def version_string() -> str:
    """
    Return display version.
    """

    return (

        f"{APP_NAME} "

        f"v{VERSION}"

    )


def about() -> str:
    """
    Human-readable application info.
    """

    return (
        f"{APP_NAME}\n"
        f"Version : {VERSION}\n"
        f"Release : {RELEASE_STAGE}\n"
        f"Build   : {BUILD_NUMBER}\n"
        f"Python  : {PYTHON_VERSION}\n"
        f"Platform: {PLATFORM}"
    )