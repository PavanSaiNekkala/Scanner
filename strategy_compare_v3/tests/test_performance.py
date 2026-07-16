"""
============================================================
Institutional Strategy Comparison Engine V3

Performance Tests

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from feature_engineering.feature_engine import FeatureEngine
from normalization.normalization_engine import NormalizationEngine
from scoring.scoring_engine import ScoringEngine
from pipeline.analysis_pipeline import AnalysisPipeline


# ==========================================================
# Dataset Factory
# ==========================================================

def create_dataframe(rows: int):

    np.random.seed(42)

    return pd.DataFrame({

        "Stock": [f"S{i}" for i in range(rows)],

        "Expectancy%": np.random.uniform(0, 30, rows),

        "Profit Factor": np.random.uniform(0.5, 5, rows),

        "Reward Risk": np.random.uniform(0.5, 4, rows),

        "Trades": np.random.randint(10, 500, rows),

        "Win %": np.random.uniform(20, 95, rows),

        "Signal Quality": np.random.uniform(40, 100, rows),

        "Holding Efficiency": np.random.uniform(20, 100, rows)

    })


# ==========================================================
# Feature Engineering
# ==========================================================

@pytest.mark.performance
def test_feature_engine_speed():

    df = create_dataframe(10000)

    start = time.perf_counter()

    FeatureEngine(df).run()

    elapsed = time.perf_counter() - start

    assert elapsed < 10


# ==========================================================
# Normalization
# ==========================================================

@pytest.mark.performance
def test_normalization_speed():

    df = create_dataframe(10000)

    start = time.perf_counter()

    NormalizationEngine(df).run()

    elapsed = time.perf_counter() - start

    assert elapsed < 10


# ==========================================================
# Scoring
# ==========================================================

@pytest.mark.performance
def test_scoring_speed():

    df = create_dataframe(10000)

    start = time.perf_counter()

    ScoringEngine(df).run()

    elapsed = time.perf_counter() - start

    assert elapsed < 10


# ==========================================================
# Pipeline
# ==========================================================

@pytest.mark.performance
def test_pipeline_speed():

    df = create_dataframe(5000)

    pipeline = AnalysisPipeline(df)

    start = time.perf_counter()

    pipeline.run()

    elapsed = time.perf_counter() - start

    assert elapsed < 30


# ==========================================================
# Memory Growth
# ==========================================================

@pytest.mark.performance
@pytest.mark.parametrize(

    "rows",

    [

        100,

        1000,

        5000,

        10000

    ]

)

def test_scalability(rows):

    df = create_dataframe(rows)

    result = FeatureEngine(df).run()

    assert len(result) == rows


# ==========================================================
# Repeatability
# ==========================================================

@pytest.mark.performance
def test_repeatability():

    df = create_dataframe(2000)

    pipeline = AnalysisPipeline(df)

    first = pipeline.run()

    second = pipeline.run()

    assert first.keys() == second.keys()


# ==========================================================
# Stress Test
# ==========================================================

@pytest.mark.performance
def test_stress_dataset():

    rows = 50000

    df = create_dataframe(rows)

    result = FeatureEngine(df).run()

    assert len(result) == rows


# ==========================================================
# Benchmark
# ==========================================================

@pytest.mark.performance
def test_pipeline_benchmark():

    df = create_dataframe(10000)

    start = time.perf_counter()

    AnalysisPipeline(df).run()

    runtime = time.perf_counter() - start

    print(f"\nPipeline Runtime : {runtime:.3f} sec")

    assert runtime > 0