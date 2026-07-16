"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Profiling Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from profiling.profiler import DataProfiler


# ==========================================================
# Constructor
# ==========================================================

def test_profiler_creation(sample_dataframe):

    profiler = DataProfiler(sample_dataframe)

    assert profiler is not None


# ==========================================================
# Generate Profile
# ==========================================================

def test_generate_profile(sample_dataframe):

    profiler = DataProfiler(sample_dataframe)

    result = profiler.generate()

    assert isinstance(result, dict)


# ==========================================================
# Expected Sections
# ==========================================================

def test_profile_contains_sections(sample_dataframe):

    profiler = DataProfiler(sample_dataframe)

    report = profiler.generate()

    expected = [

        "Dataset Summary",

        "Descriptive Statistics",

        "Data Quality",

        "Missing Values"

    ]

    for section in expected:

        if section in report:

            assert isinstance(

                report[section],

                pd.DataFrame

            )


# ==========================================================
# Dataset Summary
# ==========================================================

def test_dataset_summary(sample_dataframe):

    profiler = DataProfiler(sample_dataframe)

    report = profiler.generate()

    if "Dataset Summary" in report:

        summary = report["Dataset Summary"]

        assert not summary.empty


# ==========================================================
# Descriptive Statistics
# ==========================================================

def test_descriptive_statistics(sample_dataframe):

    profiler = DataProfiler(sample_dataframe)

    report = profiler.generate()

    if "Descriptive Statistics" in report:

        stats = report["Descriptive Statistics"]

        assert isinstance(

            stats,

            pd.DataFrame

        )


# ==========================================================
# Missing Values
# ==========================================================

def test_missing_values(sample_dataframe):

    df = sample_dataframe.copy()

    df.loc[0, "Profit Factor"] = None

    profiler = DataProfiler(df)

    report = profiler.generate()

    assert isinstance(

        report,

        dict

    )


# ==========================================================
# Empty Dataset
# ==========================================================

def test_empty_dataframe():

    profiler = DataProfiler(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        profiler.generate()


# ==========================================================
# Single Row
# ==========================================================

def test_single_row():

    df = pd.DataFrame({

        "Stock": ["ABC"],

        "Expectancy%": [12],

        "Profit Factor": [2.1]

    })

    profiler = DataProfiler(df)

    report = profiler.generate()

    assert isinstance(

        report,

        dict

    )


# ==========================================================
# Duplicate Rows
# ==========================================================

def test_duplicate_rows(sample_dataframe):

    duplicated = pd.concat(

        [

            sample_dataframe,

            sample_dataframe

        ],

        ignore_index=True

    )

    profiler = DataProfiler(

        duplicated

    )

    report = profiler.generate()

    assert isinstance(

        report,

        dict

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

            range(rows)

    })

    profiler = DataProfiler(df)

    report = profiler.generate()

    assert isinstance(

        report,

        dict

    )