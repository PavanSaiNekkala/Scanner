"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Optimization Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import pandas as pd
import pytest

from optimization.optimization_engine import OptimizationEngine

# ==========================================================
# Objective Function
# ==========================================================


def objective(df):
    return df["Composite Score"].mean()


# ==========================================================
# Parameter Space
# ==========================================================

PARAMETERS = {"Edge Weight": [0.10, 0.15], "Risk Weight": [0.10, 0.20]}


# ==========================================================
# Scenarios
# ==========================================================

SCENARIOS = {"Baseline": lambda df: df, "Stress": lambda df: df}


# ==========================================================
# Constructor
# ==========================================================


def test_optimization_creation(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    assert engine is not None


# ==========================================================
# Run Optimization
# ==========================================================


def test_run_optimization(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    result = engine.run(PARAMETERS, SCENARIOS)

    assert isinstance(result, dict)


# ==========================================================
# Best Parameters
# ==========================================================


def test_best_parameters_exist(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    result = engine.run(PARAMETERS, SCENARIOS)

    assert "Best Parameters" in result


# ==========================================================
# Best Score
# ==========================================================


def test_best_score_exists(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    result = engine.run(PARAMETERS, SCENARIOS)

    assert "Best Score" in result


# ==========================================================
# Scenario Results
# ==========================================================


def test_scenarios(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    result = engine.run(PARAMETERS, SCENARIOS)

    assert "Scenario Results" in result


# ==========================================================
# Objective Function
# ==========================================================


def test_objective_returns_float(scored_dataframe):
    value = objective(scored_dataframe)

    assert isinstance(value, float)


# ==========================================================
# Empty Dataset
# ==========================================================


def test_empty_dataframe():
    engine = OptimizationEngine(pd.DataFrame(), objective)

    with pytest.raises(Exception):
        engine.run(PARAMETERS, SCENARIOS)


# ==========================================================
# Invalid Parameter Space
# ==========================================================


def test_invalid_parameter_space(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    with pytest.raises(Exception):
        engine.run({}, SCENARIOS)


# ==========================================================
# Invalid Scenario
# ==========================================================


def test_invalid_scenario(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    with pytest.raises(Exception):
        engine.run(PARAMETERS, {})


# ==========================================================
# Repeatability
# ==========================================================


def test_repeatability(scored_dataframe):
    engine = OptimizationEngine(scored_dataframe, objective)

    first = engine.run(PARAMETERS, SCENARIOS)

    second = engine.run(PARAMETERS, SCENARIOS)

    assert first.keys() == second.keys()


# ==========================================================
# Performance
# ==========================================================


def test_large_dataset():
    rows = 10000

    df = pd.DataFrame(
        {"Composite Score": [80.0] * rows, "Institutional Score": [75.0] * rows}
    )

    engine = OptimizationEngine(df, objective)

    result = engine.run(PARAMETERS, SCENARIOS)

    assert isinstance(result, dict)


# ==========================================================
# Objective Improvement
# ==========================================================


def test_objective_value(scored_dataframe):
    baseline = objective(scored_dataframe)

    engine = OptimizationEngine(scored_dataframe, objective)

    result = engine.run(PARAMETERS, SCENARIOS)

    assert result["Best Score"] >= baseline
