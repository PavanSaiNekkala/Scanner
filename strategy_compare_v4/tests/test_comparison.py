"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
tests/test_comparison.py

Purpose
-------
Unit tests for comparison modules.

Tests
-----
• Strategy comparison
• Stock comparison
• Leaderboards
• Robustness analysis
• Correlation analysis

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from comparison.strategy_compare import compare_strategies
from comparison.stock_compare import compare_stocks
from comparison.leaderboard import (
    strategy_leaderboard,
    stock_leaderboard,
)
from comparison.robustness import robustness_score
from comparison.correlation import strategy_correlation


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def comparison_dataframe() -> pd.DataFrame:
    """
    Sample comparison dataset.
    """

    return pd.DataFrame(
        {
            "Strategy": [
                "ATR",
                "EMA",
                "RSI",
                "MACD",
            ],
            "Stock": [
                "ABC",
                "XYZ",
                "PQR",
                "DEF",
            ],
            "Composite Score": [
                92,
                84,
                78,
                70,
            ],
            "Edge Score": [
                90,
                82,
                75,
                68,
            ],
            "Reliability Score": [
                91,
                80,
                73,
                66,
            ],
            "Efficiency Score": [
                89,
                79,
                71,
                64,
            ],
            "Expectancy": [
                4.2,
                2.8,
                1.9,
                0.8,
            ],
            "Profit Factor": [
                2.4,
                1.8,
                1.5,
                1.2,
            ],
            "Reward Risk": [
                2.8,
                2.1,
                1.7,
                1.3,
            ],
            "Trades / Year": [
                180,
                140,
                90,
                60,
            ],
            "Recommendation": [
                "Strong Buy",
                "Buy",
                "Watch",
                "Improve",
            ],
        }
    )


@pytest.fixture
def correlation_dataframe() -> pd.DataFrame:
    """
    Sample return matrix.
    """

    return pd.DataFrame(
        {
            "ATR": [1, 2, 3, 4, 5],
            "EMA": [1.1, 2.2, 3.2, 3.9, 5.0],
            "RSI": [5, 4, 3, 2, 1],
        }
    )


# ============================================================
# Strategy Comparison
# ============================================================

def test_compare_strategies(
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    Strategy comparison should
    return a DataFrame.
    """

    result = compare_strategies(
        comparison_dataframe
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) > 0


# ============================================================
# Stock Comparison
# ============================================================

def test_compare_stocks(
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    Stock comparison should
    return a DataFrame.
    """

    result = compare_stocks(
        comparison_dataframe
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) > 0


# ============================================================
# Leaderboards
# ============================================================

@pytest.mark.parametrize(
    "leaderboard_function",
    [
        strategy_leaderboard,
        stock_leaderboard,
    ],
)
def test_leaderboards(
    leaderboard_function,
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    Leaderboards should return
    ranked DataFrames.
    """

    result = leaderboard_function(
        comparison_dataframe
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) > 0


# ============================================================
# Robustness
# ============================================================

def test_robustness_score(
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    Robustness analysis.
    """

    result = robustness_score(
        comparison_dataframe
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) > 0


# ============================================================
# Correlation
# ============================================================

def test_strategy_correlation(
    correlation_dataframe: pd.DataFrame,
) -> None:
    """
    Correlation matrix.
    """

    result = strategy_correlation(
        correlation_dataframe
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert result.shape[0] == result.shape[1]

    assert np.allclose(
        np.diag(result),
        1.0,
    )


# ============================================================
# Edge Cases
# ============================================================

def test_empty_dataframe() -> None:
    """
    Empty input should raise.
    """

    with pytest.raises(Exception):

        compare_strategies(
            pd.DataFrame()
        )


def test_missing_columns() -> None:
    """
    Missing required columns.
    """

    df = pd.DataFrame(
        {
            "Stock": [
                "ABC",
            ]
        }
    )

    with pytest.raises(Exception):

        compare_strategies(df)


def test_single_strategy() -> None:
    """
    Single strategy comparison.
    """

    df = pd.DataFrame(
        {
            "Strategy": ["ATR"],
            "Stock": ["ABC"],
            "Composite Score": [90],
            "Edge Score": [88],
            "Reliability Score": [85],
            "Efficiency Score": [84],
            "Expectancy": [3.5],
            "Profit Factor": [2.0],
            "Reward Risk": [2.1],
            "Trades / Year": [120],
            "Recommendation": ["Strong Buy"],
        }
    )

    result = compare_strategies(df)

    assert len(result) == 1


def test_correlation_is_symmetric(
    correlation_dataframe: pd.DataFrame,
) -> None:
    """
    Correlation matrix should
    be symmetric.
    """

    result = strategy_correlation(
        correlation_dataframe
    )

    assert result.equals(
        result.T
    )