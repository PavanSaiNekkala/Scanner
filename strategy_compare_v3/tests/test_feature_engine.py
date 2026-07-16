"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Feature Engineering

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from feature_engineering.feature_engine import FeatureEngine


# ==========================================================
# Constructor
# ==========================================================

def test_feature_engine_creation(sample_dataframe):

    engine = FeatureEngine(sample_dataframe)

    assert engine is not None


# ==========================================================
# Generate Features
# ==========================================================

def test_generate_features(sample_dataframe):

    engine = FeatureEngine(sample_dataframe)

    result = engine.run()

    assert isinstance(result, pd.DataFrame)

    assert len(result) == len(sample_dataframe)


# ==========================================================
# Original Columns Preserved
# ==========================================================

def test_original_columns_preserved(sample_dataframe):

    engine = FeatureEngine(sample_dataframe)

    result = engine.run()

    for column in sample_dataframe.columns:

        assert column in result.columns


# ==========================================================
# Expected Engineered Columns
# ==========================================================

def test_expected_feature_columns(sample_dataframe):

    engine = FeatureEngine(sample_dataframe)

    result = engine.run()

    expected = [

        "Edge Score",

        "Efficiency Score",

        "Opportunity Score",

        "Institutional Score"

    ]

    found = [

        column

        for column in expected

        if column in result.columns

    ]

    assert len(found) >= 1


# ==========================================================
# Missing Values
# ==========================================================

def test_missing_values(sample_dataframe):

    df = sample_dataframe.copy()

    df.loc[0, "Expectancy%"] = None

    engine = FeatureEngine(df)

    result = engine.run()

    assert isinstance(result, pd.DataFrame)


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_empty_dataframe():

    engine = FeatureEngine(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        engine.run()


# ==========================================================
# Single Row
# ==========================================================

def test_single_row():

    df = pd.DataFrame({

        "Stock": ["ABC"],

        "Expectancy%": [10],

        "Profit Factor": [2.5],

        "Trades": [25]

    })

    engine = FeatureEngine(df)

    result = engine.run()

    assert len(result) == 1


# ==========================================================
# Numeric Columns
# ==========================================================

def test_numeric_columns(sample_dataframe):

    engine = FeatureEngine(sample_dataframe)

    result = engine.run()

    numeric = result.select_dtypes(

        include="number"

    )

    assert len(numeric.columns) > 0


# ==========================================================
# Duplicate Execution
# ==========================================================

def test_repeatability(sample_dataframe):

    engine = FeatureEngine(sample_dataframe)

    first = engine.run()

    second = engine.run()

    pd.testing.assert_frame_equal(

        first,

        second

    )


# ==========================================================
# Performance
# ==========================================================

def test_large_dataset():

    rows = 10000

    df = pd.DataFrame({

        "Stock":

            [f"S{i}" for i in range(rows)],

        "Expectancy%":

            range(rows),

        "Profit Factor":

            range(rows),

        "Reward Risk":

            range(rows),

        "Trades":

            range(rows),

        "Win %":

            range(rows)

    })

    engine = FeatureEngine(df)

    result = engine.run()

    assert len(result) == rows