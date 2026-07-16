"""
============================================================
Institutional Strategy Comparison Engine V3

Integration Tests - Analysis Pipeline

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from pipeline.analysis_pipeline import AnalysisPipeline


# ==========================================================
# Constructor
# ==========================================================

def test_pipeline_creation(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    assert pipeline is not None


# ==========================================================
# Run Pipeline
# ==========================================================

def test_pipeline_run(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result,

        dict

    )


# ==========================================================
# Expected Sections
# ==========================================================

def test_pipeline_sections(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    expected = [

        "Profiling",

        "Relationships",

        "Features",

        "Normalization",

        "Scoring",

        "Recommendation",

        "Optimization",

        "Visualization",

        "Reports",

        "Execution Time"

    ]

    for section in expected:

        assert section in result


# ==========================================================
# Profiling Output
# ==========================================================

def test_pipeline_profiling(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result["Profiling"],

        dict

    )


# ==========================================================
# Relationship Output
# ==========================================================

def test_pipeline_relationships(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result["Relationships"],

        dict

    )


# ==========================================================
# Feature Output
# ==========================================================

def test_pipeline_features(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result["Features"],

        pd.DataFrame

    )


# ==========================================================
# Normalization Output
# ==========================================================

def test_pipeline_normalization(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result["Normalization"],

        dict

    )


# ==========================================================
# Recommendation Output
# ==========================================================

def test_pipeline_recommendation(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result["Recommendation"],

        pd.DataFrame

    )


# ==========================================================
# Reports Output
# ==========================================================

def test_pipeline_reports(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert isinstance(

        result["Reports"],

        dict

    )


# ==========================================================
# Summary
# ==========================================================

def test_pipeline_summary(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    pipeline.run()

    summary = pipeline.summary()

    assert isinstance(

        summary,

        dict

    )

    assert "Execution Time" in summary


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_pipeline_empty_dataframe():

    pipeline = AnalysisPipeline(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        pipeline.run()


# ==========================================================
# Repeatability
# ==========================================================

def test_pipeline_repeatability(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    first = pipeline.run()

    second = pipeline.run()

    assert first.keys() == second.keys()


# ==========================================================
# Large Dataset
# ==========================================================

def test_pipeline_large_dataset():

    rows = 5000

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

    pipeline = AnalysisPipeline(df)

    result = pipeline.run()

    assert isinstance(

        result,

        dict

    )


# ==========================================================
# Execution Time
# ==========================================================

def test_pipeline_execution_time(sample_dataframe):

    pipeline = AnalysisPipeline(

        sample_dataframe

    )

    result = pipeline.run()

    assert result["Execution Time"] >= 0