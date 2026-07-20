"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Normalization Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from normalization.normalization_engine import NormalizationEngine

# ==========================================================
# Constructor
# ==========================================================


def test_normalization_engine_creation(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    assert engine is not None


# ==========================================================
# Run Engine
# ==========================================================


def test_run_normalization(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    result = engine.run()

    assert isinstance(result, dict)


# ==========================================================
# Expected Methods
# ==========================================================


def test_available_methods(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    result = engine.run()

    expected = ["Percentile", "Min-Max", "Z-Score", "Robust Z-Score", "Quantile"]

    for method in expected:
        assert method in result


# ==========================================================
# Returned Objects
# ==========================================================


def test_return_types(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    result = engine.run()

    for dataframe in result.values():
        assert isinstance(dataframe, pd.DataFrame)


# ==========================================================
# Row Count
# ==========================================================


def test_row_count(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    result = engine.run()

    for dataframe in result.values():
        assert len(dataframe) == len(sample_dataframe)


# ==========================================================
# Numeric Values
# ==========================================================


def test_numeric_columns(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    result = engine.run()

    percentile = result["Percentile"]

    numeric = percentile.select_dtypes(include="number")

    assert len(numeric.columns) > 0


# ==========================================================
# Missing Values
# ==========================================================


def test_missing_values(sample_dataframe):
    df = sample_dataframe.copy()

    df.loc[0, "Profit Factor"] = None

    engine = NormalizationEngine(df)

    result = engine.run()

    assert isinstance(result, dict)


# ==========================================================
# Empty DataFrame
# ==========================================================


def test_empty_dataframe():
    engine = NormalizationEngine(pd.DataFrame())

    with pytest.raises(Exception):
        engine.run()


# ==========================================================
# Single Row
# ==========================================================


def test_single_row():
    df = pd.DataFrame({"Stock": ["ABC"], "Expectancy%": [12], "Profit Factor": [2.4]})

    engine = NormalizationEngine(df)

    result = engine.run()

    assert isinstance(result, dict)


# ==========================================================
# Repeatability
# ==========================================================


def test_repeatability(sample_dataframe):
    engine = NormalizationEngine(sample_dataframe)

    first = engine.run()

    second = engine.run()

    pd.testing.assert_frame_equal(first["Percentile"], second["Percentile"])


# ==========================================================
# Performance
# ==========================================================


def test_large_dataset():
    rows = 10000

    df = pd.DataFrame(
        {
            "Stock": [f"S{i}" for i in range(rows)],
            "Expectancy%": range(rows),
            "Profit Factor": range(rows),
            "Reward Risk": range(rows),
            "Trades": range(rows),
        }
    )

    engine = NormalizationEngine(df)

    result = engine.run()

    assert len(result["Percentile"]) == rows
