"""
core/exceptions.py
==================

Custom exceptions used throughout the
Institutional Scanner Monitor.
"""

from __future__ import annotations


# =============================================================================
# Base Exception
# =============================================================================


class ScannerMonitorError(Exception):
    """
    Base exception for the application.
    """

    default_message = "Scanner Monitor error."

    def __init__(
        self,
        message: str | None = None,
    ) -> None:

        super().__init__(
            message or self.default_message,
        )


# =============================================================================
# Configuration
# =============================================================================


class ConfigurationError(
    ScannerMonitorError,
):
    """
    Invalid application configuration.
    """

    default_message = (
        "Invalid application configuration."
    )


# =============================================================================
# File System
# =============================================================================


class FileMissingError(
    ScannerMonitorError,
):
    """
    Required file not found.
    """

    default_message = (
        "Required file does not exist."
    )


class DirectoryMissingError(
    ScannerMonitorError,
):
    """
    Required directory not found.
    """

    default_message = (
        "Required directory does not exist."
    )


class InvalidFileFormatError(
    ScannerMonitorError,
):
    """
    Unsupported file format.
    """

    default_message = (
        "Unsupported file format."
    )


# =============================================================================
# Data
# =============================================================================


class DataValidationError(
    ScannerMonitorError,
):
    """
    Dataset validation failed.
    """

    default_message = (
        "Dataset validation failed."
    )


class EmptyDatasetError(
    ScannerMonitorError,
):
    """
    Dataset is empty.
    """

    default_message = (
        "Dataset is empty."
    )


class MissingColumnError(
    ScannerMonitorError,
):
    """
    Required dataframe column missing.
    """

    default_message = (
        "Required column is missing."
    )


class DuplicateDataError(
    ScannerMonitorError,
):
    """
    Duplicate records detected.
    """

    default_message = (
        "Duplicate data detected."
    )


# =============================================================================
# Scanner
# =============================================================================


class ScannerError(
    ScannerMonitorError,
):
    """
    Scanner execution failed.
    """

    default_message = (
        "Scanner execution failed."
    )


class SignalGenerationError(
    ScannerMonitorError,
):
    """
    Signal generation failed.
    """

    default_message = (
        "Unable to generate signals."
    )


# =============================================================================
# Portfolio
# =============================================================================


class PortfolioError(
    ScannerMonitorError,
):
    """
    Portfolio operation failed.
    """

    default_message = (
        "Portfolio operation failed."
    )


class HoldingsError(
    ScannerMonitorError,
):
    """
    Holdings operation failed.
    """

    default_message = (
        "Holdings operation failed."
    )


# =============================================================================
# Downloads
# =============================================================================


class ExportError(
    ScannerMonitorError,
):
    """
    Export failed.
    """

    default_message = (
        "Export operation failed."
    )


class ImportErrorData(
    ScannerMonitorError,
):
    """
    Import failed.
    """

    default_message = (
        "Import operation failed."
    )


# =============================================================================
# Cache
# =============================================================================


class CacheError(
    ScannerMonitorError,
):
    """
    Cache operation failed.
    """

    default_message = (
        "Cache operation failed."
    )


# =============================================================================
# Authentication
# =============================================================================


class PermissionDeniedError(
    ScannerMonitorError,
):
    """
    Permission denied.
    """

    default_message = (
        "Permission denied."
    )


class AuthenticationError(
    ScannerMonitorError,
):
    """
    Authentication failed.
    """

    default_message = (
        "Authentication failed."
    )


# =============================================================================
# API
# =============================================================================


class APIConnectionError(
    ScannerMonitorError,
):
    """
    API connection failed.
    """

    default_message = (
        "Unable to connect to the API."
    )


class APIRateLimitError(
    ScannerMonitorError,
):
    """
    API rate limit exceeded.
    """

    default_message = (
        "API rate limit exceeded."
    )


# =============================================================================
# Database
# =============================================================================


class DatabaseError(
    ScannerMonitorError,
):
    """
    Database operation failed.
    """

    default_message = (
        "Database operation failed."
    )


class QueryError(
    DatabaseError,
):
    """
    Database query failed.
    """

    default_message = (
        "Database query failed."
    )