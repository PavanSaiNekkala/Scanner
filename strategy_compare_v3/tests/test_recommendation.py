"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Recommendation Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from recommendation.recommendation_engine import RecommendationEngine


# ==========================================================
# Constructor
# ==========================================================

def test_recommendation_engine_creation(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    assert engine is not None


# ==========================================================
# Run Engine
# ==========================================================

def test_generate_recommendations(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    assert isinstance(result, pd.DataFrame)


# ==========================================================
# Recommendation Column
# ==========================================================

def test_recommendation_column_exists(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    assert "Recommendation" in result.columns


# ==========================================================
# Recommendation Values
# ==========================================================

def test_recommendation_values(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    valid = {

        "STRONG BUY",

        "BUY",

        "ACCUMULATE",

        "WATCH",

        "HOLD",

        "REDUCE",

        "SELL",

        "AVOID"

    }

    assert set(result["Recommendation"]).issubset(valid)


# ==========================================================
# Row Count
# ==========================================================

def test_row_count(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    assert len(result) == len(scored_dataframe)


# ==========================================================
# No Missing Recommendations
# ==========================================================

def test_no_missing_recommendations(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    assert result["Recommendation"].isna().sum() == 0


# ==========================================================
# Composite Score Preserved
# ==========================================================

def test_composite_score_exists(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    assert "Composite Score" in result.columns


# ==========================================================
# Recommendation Distribution
# ==========================================================

def test_distribution(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    result = engine.generate()

    distribution = result["Recommendation"].value_counts()

    assert distribution.sum() == len(result)


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_empty_dataframe():

    engine = RecommendationEngine(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        engine.generate()


# ==========================================================
# Repeatability
# ==========================================================

def test_repeatability(scored_dataframe):

    engine = RecommendationEngine(scored_dataframe)

    first = engine.generate()

    second = engine.generate()

    pd.testing.assert_frame_equal(

        first,

        second

    )


# ==========================================================
# Recommendation Threshold Test
# ==========================================================

def test_threshold_logic():

    df = pd.DataFrame({

        "Stock": ["AAA"],

        "Composite Score": [95],

        "Institutional Score": [95]

    })

    engine = RecommendationEngine(df)

    result = engine.generate()

    assert result.iloc[0]["Recommendation"] in {

        "STRONG BUY",

        "BUY"

    }


# ==========================================================
# Performance
# ==========================================================

def test_large_dataset():

    rows = 10000

    df = pd.DataFrame({

        "Stock":

            [f"S{i}" for i in range(rows)],

        "Composite Score":

            [80] * rows,

        "Institutional Score":

            [78] * rows

    })

    engine = RecommendationEngine(df)

    result = engine.generate()

    assert len(result) == rows