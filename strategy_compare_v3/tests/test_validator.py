"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Data Validator

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.validator import DataValidator


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def valid_dataframe():

    return pd.DataFrame({

        "Stock": ["ABC", "XYZ"],

        "Expectancy%": [12.5, 18.2],

        "Profit Factor": [1.8, 2.3],

        "Trades": [50, 80]

    })


@pytest.fixture
def empty_dataframe():

    return pd.DataFrame()


# ==========================================================
# Constructor
# ==========================================================

def test_validator_creation(valid_dataframe):

    validator = DataValidator(valid_dataframe)

    assert validator is not None


# ==========================================================
# Valid Dataset
# ==========================================================

def test_validate_valid_dataframe(valid_dataframe):

    validator = DataValidator(valid_dataframe)

    assert validator.validate() is True


# ==========================================================
# Empty Dataset
# ==========================================================

def test_validate_empty_dataframe(empty_dataframe):

    validator = DataValidator(empty_dataframe)

    with pytest.raises(ValueError):

        validator.validate()


# ==========================================================
# Duplicate Columns
# ==========================================================

def test_duplicate_columns():

    df = pd.DataFrame(

        [[1, 2]],

        columns=["A", "A"]

    )

    validator = DataValidator(df)

    with pytest.raises(ValueError):

        validator.validate()


# ==========================================================
# Missing Values
# ==========================================================

def test_missing_values(valid_dataframe):

    df = valid_dataframe.copy()

    df.loc[0, "Profit Factor"] = None

    validator = DataValidator(df)

    result = validator.validate()

    assert result is True


# ==========================================================
# Column Exists
# ==========================================================

def test_required_column_exists(valid_dataframe):

    assert "Stock" in valid_dataframe.columns


# ==========================================================
# Column Missing
# ==========================================================

def test_required_column_missing(valid_dataframe):

    df = valid_dataframe.drop(

        columns=["Stock"]

    )

    validator = DataValidator(df)

    with pytest.raises(ValueError):

        validator.validate()


# ==========================================================
# Numeric Columns
# ==========================================================

def test_numeric_columns(valid_dataframe):

    numeric = valid_dataframe.select_dtypes(

        include="number"

    )

    assert len(numeric.columns) == 3


# ==========================================================
# Invalid Numeric Type
# ==========================================================

def test_invalid_numeric_type(valid_dataframe):

    df = valid_dataframe.copy()

    df["Trades"] = [

        "ABC",

        "XYZ"

    ]

    validator = DataValidator(df)

    with pytest.raises(ValueError):

        validator.validate()


# ==========================================================
# DataFrame Shape
# ==========================================================

def test_dataframe_shape(valid_dataframe):

    validator = DataValidator(valid_dataframe)

    validator.validate()

    assert valid_dataframe.shape == (2, 4)


# ==========================================================
# Large Dataset
# ==========================================================

def test_large_dataframe():

    rows = 10000

    df = pd.DataFrame({

        "Stock":

            [f"S{i}" for i in range(rows)],

        "Expectancy%":

            range(rows),

        "Profit Factor":

            range(rows),

        "Trades":

            range(rows)

    })

    validator = DataValidator(df)

    assert validator.validate() is True