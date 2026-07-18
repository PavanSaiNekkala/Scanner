"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
tests/test_portfolio.py

Purpose
-------
Unit tests for portfolio allocation and
risk filtering modules.

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from portfolio.allocation import (
    allocate_portfolio,
    blended_weight,
    edge_weight,
    equal_weight,
    reliability_weight,
    score_weight,
)

from portfolio.risk_filter import (
    apply_risk_filters,
)

TOTAL_WEIGHT = 100.0


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """
    Sample portfolio used across all tests.
    """

    return pd.DataFrame(
        {
            "Stock": [
                "ABC",
                "XYZ",
                "PQR",
                "DEF",
                "LMN",
            ],
            "Composite Score": [
                95,
                82,
                71,
                64,
                45,
            ],
            "Edge Score": [
                93,
                80,
                70,
                60,
                35,
            ],
            "Reliability Score": [
                90,
                79,
                73,
                62,
                40,
            ],
            "Efficiency Score": [
                88,
                76,
                70,
                61,
                42,
            ],
            "Expectancy": [
                4.2,
                2.6,
                1.9,
                0.8,
                -0.5,
            ],
            "Profit Factor": [
                2.3,
                1.8,
                1.5,
                1.2,
                0.8,
            ],
            "Reward Risk": [
                2.8,
                2.2,
                1.7,
                1.3,
                0.9,
            ],
            "Trades": [
                150,
                120,
                80,
                50,
                12,
            ],
        }
    )


# ============================================================
# Allocation Methods
# ============================================================

@pytest.mark.parametrize(
    "allocator",
    [
        equal_weight,
        score_weight,
        edge_weight,
        reliability_weight,
        blended_weight,
    ],
)
def test_allocation_methods(
    allocator,
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Every allocation method must
    produce valid portfolio weights.
    """

    df = allocator(sample_dataframe)

    assert df["Weight"].sum() == pytest.approx(
        TOTAL_WEIGHT
    )

    assert (df["Weight"] > 0).all()

    assert not df["Weight"].isna().any()


# ============================================================
# Allocation Dispatcher
# ============================================================

def test_allocate_portfolio(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Dispatcher should allocate
    valid portfolio weights.
    """

    df = allocate_portfolio(sample_dataframe)

    assert df["Weight"].sum() == pytest.approx(
        TOTAL_WEIGHT
    )

    assert (df["Weight"] > 0).all()

    assert not df["Weight"].isna().any()


# ============================================================
# Risk Filters
# ============================================================

def test_apply_risk_filters(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Risk filter should return
    a non-empty portfolio.
    """

    df = apply_risk_filters(sample_dataframe)

    assert len(df) > 0


def test_negative_expectancy_removed(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Negative expectancy strategies
    should be removed.
    """

    df = apply_risk_filters(sample_dataframe)

    assert (df["Expectancy"] >= 0).all()


def test_profit_factor_filter(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Profit Factor filter.
    """

    df = apply_risk_filters(sample_dataframe)

    assert (df["Profit Factor"] >= 1).all()


def test_duplicate_stocks_removed(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Duplicate stocks should be removed.
    """

    duplicate = sample_dataframe.iloc[[0]].copy()

    df = pd.concat(
        [
            sample_dataframe,
            duplicate,
        ],
        ignore_index=True,
    )

    filtered = apply_risk_filters(df)

    assert (
        filtered["Stock"]
        .duplicated()
        .sum()
        == 0
    )


# ============================================================
# Edge Cases
# ============================================================

def test_single_stock_allocation(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Single stock should receive
    100% allocation.
    """

    df = sample_dataframe.head(1)

    result = allocate_portfolio(df)

    assert result["Weight"].iloc[0] == pytest.approx(
        TOTAL_WEIGHT
    )


def test_zero_composite_scores(
    sample_dataframe: pd.DataFrame,
) -> None:
    """
    Allocation should handle
    zero composite scores.
    """

    df = sample_dataframe.copy()

    df["Composite Score"] = 0

    result = score_weight(df)

    assert not result["Weight"].isna().any()


def test_empty_dataframe() -> None:
    """
    Empty DataFrame should raise.
    """

    with pytest.raises(Exception):

        allocate_portfolio(
            pd.DataFrame()
        )


def test_missing_columns() -> None:
    """
    Missing required columns
    should raise an exception.
    """

    df = pd.DataFrame(
        {
            "Stock": ["ABC"],
        }
    )

    with pytest.raises(Exception):

        allocate_portfolio(df)