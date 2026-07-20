"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/exceptions.py

Custom Exceptions

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


class StrategyCompareError(Exception):
    """
    Base exception for the application.
    """

    def __init__(self, message: str):
        super().__init__(message)


# ==========================================================
# FILE ERRORS
# ==========================================================


class FileValidationError(StrategyCompareError):
    """
    Raised when an input file is invalid.
    """

    pass


class UnsupportedFileTypeError(FileValidationError):
    """
    Raised for unsupported file formats.
    """

    pass


class EmptyFileError(FileValidationError):
    """
    Raised when an input file contains no data.
    """

    pass


# ==========================================================
# DATA ERRORS
# ==========================================================


class DataValidationError(StrategyCompareError):
    """
    Raised when dataframe validation fails.
    """

    pass


class MissingColumnError(DataValidationError):
    """
    Raised when required columns are absent.
    """

    pass


class DuplicateColumnError(DataValidationError):
    """
    Raised when duplicate column names exist.
    """

    pass


class NoNumericColumnsError(DataValidationError):
    """
    Raised when no numeric columns exist.
    """

    pass


class EmptyDataFrameError(DataValidationError):
    """
    Raised when dataframe is empty.
    """

    pass


# ==========================================================
# ANALYTICS
# ==========================================================


class ProfilingError(StrategyCompareError):
    """
    Raised during profiling.
    """

    pass


class RelationshipAnalysisError(StrategyCompareError):
    """
    Raised during relationship analysis.
    """

    pass


class FeatureEngineeringError(StrategyCompareError):
    """
    Raised during feature engineering.
    """

    pass


class NormalizationError(StrategyCompareError):
    """
    Raised during normalization.
    """

    pass


class ScoringError(StrategyCompareError):
    """
    Raised during score generation.
    """

    pass


class RecommendationError(StrategyCompareError):
    """
    Raised during recommendation generation.
    """

    pass


class OptimizationError(StrategyCompareError):
    """
    Raised during optimization.
    """

    pass


class ReportGenerationError(StrategyCompareError):
    """
    Raised while creating reports.
    """

    pass


class VisualizationError(StrategyCompareError):
    """
    Raised during chart generation.
    """

    pass


# ==========================================================
# CONFIGURATION
# ==========================================================


class ConfigurationError(StrategyCompareError):
    """
    Raised when configuration is invalid.
    """

    pass


# ==========================================================
# CACHE
# ==========================================================


class CacheError(StrategyCompareError):
    """
    Raised during cache operations.
    """

    pass
