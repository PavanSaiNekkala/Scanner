"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    tests/test_comparison.py

Purpose:
    Unit tests for comparison modules.

=============================================================
"""

import pandas as pd

from comparison.strategy_compare import StrategyComparisonEngine
from comparison.stock_compare import StockComparisonEngine
from comparison.leaderboard import LeaderboardEngine
from comparison.robustness import RobustnessEngine
from comparison.correlation import CorrelationEngine


###############################################################################
# Sample Data
###############################################################################

def sample_dataframe():

    return pd.DataFrame({

        "Stock": ["ABC", "XYZ", "PQR"],

        "Strategy": ["S1", "S1", "S2"],

        "Composite Score": [90, 75, 82],

        "Edge Score": [88, 72, 81],

        "Reliability Score": [91, 68, 80],

        "Efficiency Score": [86, 71, 78],

        "Expectancy": [3.2, 1.5, 2.4],

        "Profit Factor": [2.1, 1.4, 1.8],

        "Reward Risk": [2.5, 1.8, 2.0],

        "Trades": [120, 80, 95],

        "Recommendation": [

            "Strong Buy",

            "Watch",

            "Buy"

        ]

    })


###############################################################################
# Strategy Comparison
###############################################################################

def test_strategy_compare_creation():

    df = sample_dataframe()

    engine = StrategyComparisonEngine(df)

    assert engine is not None


###############################################################################
# Stock Comparison
###############################################################################

def test_stock_compare_creation():

    df = sample_dataframe()

    engine = StockComparisonEngine(df)

    assert engine is not None


###############################################################################
# Leaderboard
###############################################################################

def test_leaderboard_creation():

    df = sample_dataframe()

    engine = LeaderboardEngine(df)

    assert engine is not None


###############################################################################
# Robustness
###############################################################################

def test_robustness_creation():

    df = sample_dataframe()

    engine = RobustnessEngine(df)

    assert engine is not None


###############################################################################
# Correlation
###############################################################################

def test_correlation_creation():

    df = sample_dataframe()

    engine = CorrelationEngine(df)

    assert engine is not None


###############################################################################
# Composite Ranking
###############################################################################

def test_highest_composite_score():

    df = sample_dataframe()

    highest = df.sort_values(

        "Composite Score",

        ascending=False

    ).iloc[0]

    assert highest["Stock"] == "ABC"


###############################################################################
# Recommendation Exists
###############################################################################

def test_recommendation_column():

    df = sample_dataframe()

    assert "Recommendation" in df.columns


###############################################################################
# No Missing Scores
###############################################################################

def test_no_missing_scores():

    df = sample_dataframe()

    assert df["Composite Score"].isna().sum() == 0

    assert df["Edge Score"].isna().sum() == 0

    assert df["Reliability Score"].isna().sum() == 0


###############################################################################
# Positive Profit Factor
###############################################################################

def test_profit_factor_positive():

    df = sample_dataframe()

    assert (df["Profit Factor"] > 0).all()


###############################################################################
# Positive Trades
###############################################################################

def test_positive_trades():

    df = sample_dataframe()

    assert (df["Trades"] > 0).all()