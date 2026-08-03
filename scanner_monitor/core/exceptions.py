"""
scanner_monitor.core.exceptions
===============================

Custom exception hierarchy for the Institutional Scanner Monitor.

This module centralizes all application-specific exceptions to provide
consistent error handling throughout the project.

The hierarchy is designed to:

- Provide a common base exception.
- Support granular exception handling.
- Preserve backward compatibility.
- Offer optional exception chaining.
"""

from __future__ import annotations

from typing import Final

__all__ = [
    # Base
    "ScannerMonitorError",
    # Configuration
    "ConfigurationError",
    # File System
    "FileMissingError",
    "DirectoryMissingError",
    "InvalidFileFormatError",
    # Data
    "DataValidationError",
    "EmptyDatasetError",
    "MissingColumnError",
    "DuplicateDataError",
    # Scanner
    "ScannerError",
    "SignalGenerationError",
    # Portfolio
    "PortfolioError",
    "HoldingsError",
    # Import / Export
    "ExportError",
    "ImportErrorData",
    # Cache
    "CacheError",
    # Security
    "PermissionDeniedError",
    "AuthenticationError",
    # API
    "APIConnectionError",
    "APIRateLimitError",
    # Database
    "DatabaseError",
    "QueryError",
]


# =============================================================================
# Base Exception
# =============================================================================


class ScannerMonitorError(Exception):
    """
    Base exception for all application-specific errors.

    Parameters
    ----------
    message:
        Optional custom error message.

    cause:
        Optional underlying exception responsible for this error.
    """

    default_message: Final[str] = "Scanner Monitor error."

    def __init__(
        self,
        message: str | None = None,
        *,
        cause: Exception | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.cause = cause

        super().__init__(self.message)

        if cause is not None:
            self.__cause__ = cause

    def __str__(self) -> str:
        return self.message


# =============================================================================
# Configuration
# =============================================================================


class ConfigurationError(ScannerMonitorError):
    """
    Raised when application configuration is invalid.
    """

    default_message = "Invalid application configuration."


# =============================================================================
# File System
# =============================================================================


class FileMissingError(ScannerMonitorError):
    """
    Raised when a required file cannot be found.
    """

    default_message = "Required file does not exist."


class DirectoryMissingError(ScannerMonitorError):
    """
    Raised when a required directory cannot be found.
    """

    default_message = "Required directory does not exist."


class InvalidFileFormatError(ScannerMonitorError):
    """
    Raised when an unsupported file format is encountered.
    """

    default_message = "Unsupported file format."


# =============================================================================
# Data
# =============================================================================


class DataValidationError(ScannerMonitorError):
    """
    Raised when dataset validation fails.
    """

    default_message = "Dataset validation failed."


class EmptyDatasetError(ScannerMonitorError):
    """
    Raised when an expected dataset is empty.
    """

    default_message = "Dataset is empty."


class MissingColumnError(ScannerMonitorError):
    """
    Raised when one or more required columns are missing.
    """

    default_message = "Required column is missing."


class DuplicateDataError(ScannerMonitorError):
    """
    Raised when duplicate records are detected.
    """

    default_message = "Duplicate data detected."


# =============================================================================
# Scanner
# =============================================================================


class ScannerError(ScannerMonitorError):
    """
    Raised when scanner execution fails.
    """

    default_message = "Scanner execution failed."


class SignalGenerationError(ScannerMonitorError):
    """
    Raised when signal generation fails.
    """

    default_message = "Unable to generate signals."


# =============================================================================
# Portfolio
# =============================================================================


class PortfolioError(ScannerMonitorError):
    """
    Raised when a portfolio operation fails.
    """

    default_message = "Portfolio operation failed."


class HoldingsError(ScannerMonitorError):
    """
    Raised when a holdings operation fails.
    """

    default_message = "Holdings operation failed."


# =============================================================================
# Import / Export
# =============================================================================


class ExportError(ScannerMonitorError):
    """
    Raised when exporting data fails.
    """

    default_message = "Export operation failed."


class ImportErrorData(ScannerMonitorError):
    """
    Raised when importing data fails.

    Named ImportErrorData intentionally to avoid shadowing Python's
    built-in ImportError exception.
    """

    default_message = "Import operation failed."


# =============================================================================
# Cache
# =============================================================================


class CacheError(ScannerMonitorError):
    """
    Raised when cache operations fail.
    """

    default_message = "Cache operation failed."


# =============================================================================
# Authentication / Authorization
# =============================================================================


class PermissionDeniedError(ScannerMonitorError):
    """
    Raised when the current user lacks permission.
    """

    default_message = "Permission denied."


class AuthenticationError(ScannerMonitorError):
    """
    Raised when authentication fails.
    """

    default_message = "Authentication failed."


# =============================================================================
# API
# =============================================================================


class APIConnectionError(ScannerMonitorError):
    """
    Raised when an API connection cannot be established.
    """

    default_message = "Unable to connect to the API."


class APIRateLimitError(ScannerMonitorError):
    """
    Raised when an API rate limit has been exceeded.
    """

    default_message = "API rate limit exceeded."


# =============================================================================
# Database
# =============================================================================


class DatabaseError(ScannerMonitorError):
    """
    Base class for database-related exceptions.
    """

    default_message = "Database operation failed."


class QueryError(DatabaseError):
    """
    Raised when a database query fails.
    """

    default_message = "Database query failed."