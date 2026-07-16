"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Relationship Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from relationships.relationship_engine import RelationshipEngine


# ==========================================================
# Constructor
# ==========================================================

def test_relationship_engine_creation(sample_dataframe):

    engine = RelationshipEngine(sample_dataframe)

    assert engine is not None


# ==========================================================
# Generate Relationships
# ==========================================================

def test_generate_relationships(sample_dataframe):

    engine = RelationshipEngine(sample_dataframe)

    result = engine.generate()

    assert isinstance(result, dict)


# ==========================================================
# Correlation Matrix
# ==========================================================

def test_correlation_matrix(sample_dataframe):

    engine = RelationshipEngine(sample_dataframe)

    report = engine.generate()

    if "Correlation Matrix" in report:

        matrix = report["Correlation Matrix"]

        assert isinstance(matrix, pd.DataFrame)

        assert matrix.shape[0] == matrix.shape[1]


# ==========================================================
# Dependency Matrix
# ==========================================================

def test_dependency_matrix(sample_dataframe):

    engine = RelationshipEngine(sample_dataframe)

    report = engine.generate()

    if "Dependency Matrix" in report:

        matrix = report["Dependency Matrix"]

        assert isinstance(matrix, pd.DataFrame)


# ==========================================================
# Multicollinearity
# ==========================================================

def test_multicollinearity(sample_dataframe):

    engine = RelationshipEngine(sample_dataframe)

    report = engine.generate()

    if "Multicollinearity" in report:

        vif = report["Multicollinearity"]

        assert isinstance(vif, pd.DataFrame)


# ==========================================================
# Feature Selection
# ==========================================================

def test_feature_selection(sample_dataframe):

    engine = RelationshipEngine(sample_dataframe)

    report = engine.generate()

    if "Feature Selection" in report:

        features = report["Feature Selection"]

        assert isinstance(features, pd.DataFrame)


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_empty_dataframe():

    engine = RelationshipEngine(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        engine.generate()


# ==========================================================
# Single Numeric Column
# ==========================================================

def test_single_numeric_column():

    df = pd.DataFrame({

        "A": [1, 2, 3, 4]

    })

    engine = RelationshipEngine(df)

    report = engine.generate()

    assert isinstance(report, dict)


# ==========================================================
# Duplicate Columns
# ==========================================================

def test_duplicate_columns(sample_dataframe):

    df = sample_dataframe.copy()

    df["Expectancy_Copy"] = df["Expectancy%"]

    engine = RelationshipEngine(df)

    report = engine.generate()

    assert isinstance(report, dict)


# ==========================================================
# Performance
# ==========================================================

def test_large_relationship_dataset():

    rows = 5000

    df = pd.DataFrame({

        "A": range(rows),

        "B": range(rows),

        "C": range(rows),

        "D": range(rows)

    })

    engine = RelationshipEngine(df)

    report = engine.generate()

    assert isinstance(report, dict)