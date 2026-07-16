"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Scoring Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from scoring.scoring_engine import ScoringEngine


# ==========================================================
# Constructor
# ==========================================================

def test_scoring_engine_creation(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    assert engine is not None


# ==========================================================
# Run Engine
# ==========================================================

def test_generate_scores(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    assert isinstance(result, pd.DataFrame)


# ==========================================================
# Row Count
# ==========================================================

def test_row_count(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    assert len(result) == len(sample_dataframe)


# ==========================================================
# Score Columns
# ==========================================================

def test_score_columns_exist(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    expected = [

        "Edge Score",

        "Risk Score",

        "Efficiency Score",

        "Stability Score",

        "Reliability Score",

        "Opportunity Score",

        "Execution Score",

        "Institutional Score",

        "Composite Score"

    ]

    found = [

        column

        for column in expected

        if column in result.columns

    ]

    assert len(found) >= 5


# ==========================================================
# Score Types
# ==========================================================

def test_score_numeric(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    score_columns = [

        column

        for column in result.columns

        if column.endswith("Score")

    ]

    for column in score_columns:

        assert pd.api.types.is_numeric_dtype(

            result[column]

        )


# ==========================================================
# No Missing Scores
# ==========================================================

def test_no_missing_scores(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    score_columns = [

        column

        for column in result.columns

        if column.endswith("Score")

    ]

    for column in score_columns:

        assert result[column].isna().sum() == 0


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_empty_dataframe():

    engine = ScoringEngine(

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

        "Expectancy%": [12],

        "Profit Factor": [2.4],

        "Reward Risk": [1.8]

    })

    engine = ScoringEngine(df)

    result = engine.run()

    assert len(result) == 1


# ==========================================================
# Repeatability
# ==========================================================

def test_repeatability(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    first = engine.run()

    second = engine.run()

    pd.testing.assert_frame_equal(

        first,

        second

    )


# ==========================================================
# Large Dataset
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

    engine = ScoringEngine(df)

    result = engine.run()

    assert len(result) == rows


# ==========================================================
# Composite Score Exists
# ==========================================================

def test_composite_score_exists(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    assert "Composite Score" in result.columns


# ==========================================================
# Institutional Score Exists
# ==========================================================

def test_institutional_score_exists(sample_dataframe):

    engine = ScoringEngine(sample_dataframe)

    result = engine.run()

    assert "Institutional Score" in result.columns