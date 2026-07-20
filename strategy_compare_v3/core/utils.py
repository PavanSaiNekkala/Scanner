"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/utils.py
Author : Pavan Sai

Reusable utility functions used across the project.
============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from core.constants import (
    DECIMAL_PLACES,
    IQR_MULTIPLIER,
)

# ==========================================================
# DIRECTORY UTILITIES
# ==========================================================


def create_directory(path: Path) -> None:
    """
    Create directory if it does not exist.
    """

    path.mkdir(parents=True, exist_ok=True)


# ==========================================================
# FILE UTILITIES
# ==========================================================


def get_extension(file_path: str | Path) -> str:
    """
    Returns file extension.
    """

    return Path(file_path).suffix.lower()


# ==========================================================
# COLUMN UTILITIES
# ==========================================================


def numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Return numeric column names.
    """

    return df.select_dtypes(include=np.number).columns.tolist()


def categorical_columns(df: pd.DataFrame) -> List[str]:
    """
    Return categorical columns.
    """

    return df.select_dtypes(exclude=np.number).columns.tolist()


def datetime_columns(df: pd.DataFrame) -> List[str]:
    """
    Return datetime columns.
    """

    return df.select_dtypes(include=["datetime"]).columns.tolist()


# ==========================================================
# DATAFRAME UTILITIES
# ==========================================================


def dataframe_memory_mb(df: pd.DataFrame) -> float:
    """
    DataFrame memory usage in MB.
    """

    memory = df.memory_usage(deep=True).sum() / (1024**2)

    return round(memory, DECIMAL_PLACES)


def duplicate_rows(df: pd.DataFrame) -> int:
    """
    Number of duplicate rows.
    """

    return int(df.duplicated().sum())


# ==========================================================
# SAFE DIVISION
# ==========================================================


def safe_divide(numerator, denominator):
    """
    Prevent divide-by-zero.
    """

    denominator = np.where(denominator == 0, np.nan, denominator)

    return numerator / denominator


# ==========================================================
# BASIC STATISTICS
# ==========================================================


def coefficient_of_variation(series: pd.Series) -> float:
    """
    CV = Std / Mean
    """

    mean = series.mean()

    if mean == 0:
        return np.nan

    return (series.std() / mean) * 100


def standard_error(series: pd.Series) -> float:
    """
    Standard Error.
    """

    return series.std() / np.sqrt(series.count())


def interquartile_range(series: pd.Series) -> float:
    """
    IQR.
    """

    return series.quantile(0.75) - series.quantile(0.25)


# ==========================================================
# OUTLIERS
# ==========================================================


def outlier_count_iqr(series: pd.Series) -> int:
    """
    Count outliers using IQR.
    """

    q1 = series.quantile(0.25)

    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - IQR_MULTIPLIER * iqr

    upper = q3 + IQR_MULTIPLIER * iqr

    return int(((series < lower) | (series > upper)).sum())


# ==========================================================
# Z SCORE
# ==========================================================


def z_score(series: pd.Series) -> pd.Series:
    """
    Z-score.
    """

    std = series.std()

    if std == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)

    return (series - series.mean()) / std


# ==========================================================
# ROUNDING
# ==========================================================


def round_series(series: pd.Series, decimals: int = DECIMAL_PLACES) -> pd.Series:
    """
    Round Series.
    """

    return series.round(decimals)


# ==========================================================
# DATA CLEANING
# ==========================================================


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataframe column names.
    """

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("%", "Pct", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    return df


def convert_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely convert numeric-like columns while preserving
    identifiers and text columns.
    """

    df = df.copy()

    text_keywords = {
        "stock",
        "symbol",
        "strategy",
        "name",
        "remark",
        "remarks",
        "sector",
        "industry",
        "recommendation",
    }

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        if column.lower() in text_keywords:
            continue

        cleaned = (
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )

        converted = pd.to_numeric(cleaned, errors="coerce")

        # Convert only if most values are numeric
        if converted.notna().mean() >= 0.80:
            df[column] = converted

    return df


# ==========================================================
# PERCENTAGE
# ==========================================================


def percentage(part: float, whole: float) -> float:
    """
    Percentage calculation.
    """

    if whole == 0:
        return 0

    return round((part / whole) * 100, 2)


# ==========================================================
# SUMMARY
# ==========================================================


def dataframe_shape(df: pd.DataFrame) -> tuple[int, int]:
    """
    Returns dataframe shape.
    """

    return df.shape


def numeric_column_count(df: pd.DataFrame) -> int:
    """
    Number of numeric columns.
    """

    return len(numeric_columns(df))


def categorical_column_count(df: pd.DataFrame) -> int:
    """
    Number of categorical columns.
    """

    return len(categorical_columns(df))


# ==========================================================
# END
# ==========================================================
