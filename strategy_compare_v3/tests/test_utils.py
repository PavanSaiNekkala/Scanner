"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Utility Functions

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# Update these imports to match your actual utils.py
from core.utils import (
    safe_divide,
    percentage,
    to_numeric,
)


# ==========================================================
# safe_divide()
# ==========================================================

def test_safe_divide_normal():

    assert safe_divide(10, 2) == 5


def test_safe_divide_zero():

    result = safe_divide(10, 0)

    assert result == 0


def test_safe_divide_negative():

    assert safe_divide(-10, 2) == -5


def test_safe_divide_numpy():

    a = np.array([10, 20, 30])

    b = np.array([2, 4, 5])

    result = safe_divide(a, b)

    assert np.allclose(result, [5, 5, 6])


# ==========================================================
# percentage()
# ==========================================================

def test_percentage():

    assert percentage(25, 100) == 25


def test_percentage_zero():

    assert percentage(0, 100) == 0


def test_percentage_full():

    assert percentage(100, 100) == 100


# ==========================================================
# to_numeric()
# ==========================================================

def test_to_numeric_series():

    series = pd.Series(

        ["10", "20", "30"]

    )

    converted = to_numeric(series)

    assert converted.dtype.kind in ("i", "f")


def test_to_numeric_invalid():

    series = pd.Series(

        ["10", "ABC", "20"]

    )

    converted = to_numeric(series)

    assert converted.isna().sum() == 1


# ==========================================================
# Edge Cases
# ==========================================================

@pytest.mark.parametrize(

    "numerator, denominator",

    [

        (0, 1),

        (1, 0),

        (0, 0),

        (-5, 2),

        (5, -2),

    ],

)

def test_safe_divide_edge_cases(

    numerator,

    denominator,

):

    safe_divide(

        numerator,

        denominator

    )


# ==========================================================
# Performance
# ==========================================================

def test_large_series_numeric():

    series = pd.Series(

        np.random.randint(

            0,

            1000,

            100000

        ).astype(str)

    )

    converted = to_numeric(series)

    assert len(converted) == 100000