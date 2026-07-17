"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    tests/test_portfolio.py

Purpose:
    Unit tests for portfolio modules.

=============================================================
"""

import numpy as np
import pandas as pd

from portfolio.allocation import (
    equal_weight,
    score_weight,
    edge_weight,
    reliability_weight,
    blended_weight,
    allocate_portfolio,
)

from portfolio.risk_filter import (
    apply_risk_filters,
)


###############################################################################
# Sample Data
###############################################################################

def sample_dataframe():

    return pd.DataFrame({

        "Stock": [

            "ABC",

            "XYZ",

            "PQR",

            "DEF",

            "LMN"

        ],

        "Composite Score": [

            95,

            82,

            71,

            64,

            45

        ],

        "Edge Score": [

            93,

            80,

            70,

            60,

            35

        ],

        "Reliability Score": [

            90,

            79,

            73,

            62,

            40

        ],

        "Efficiency Score": [

            88,

            76,

            70,

            61,

            42

        ],

        "Expectancy": [

            4.2,

            2.6,

            1.9,

            0.8,

            -0.5

        ],

        "Profit Factor": [

            2.3,

            1.8,

            1.5,

            1.2,

            0.8

        ],

        "Reward Risk": [

            2.8,

            2.2,

            1.7,

            1.3,

            0.9

        ],

        "Trades": [

            150,

            120,

            80,

            50,

            12

        ]

    })


###############################################################################
# Equal Weight
###############################################################################

def test_equal_weight():

    df = equal_weight(

        sample_dataframe()

    )

    assert round(

        df["Weight"].sum(),

        2

    ) == 100.00


###############################################################################
# Composite Allocation
###############################################################################

def test_score_weight():

    df = score_weight(

        sample_dataframe()

    )

    assert np.isclose(

        df["Weight"].sum(),

        100.0

    )


###############################################################################
# Edge Allocation
###############################################################################

def test_edge_weight():

    df = edge_weight(

        sample_dataframe()

    )

    assert np.isclose(

        df["Weight"].sum(),

        100.0

    )


###############################################################################
# Reliability Allocation
###############################################################################

def test_reliability_weight():

    df = reliability_weight(

        sample_dataframe()

    )

    assert np.isclose(

        df["Weight"].sum(),

        100.0

    )


###############################################################################
# Blended Allocation
###############################################################################

def test_blended_weight():

    df = blended_weight(

        sample_dataframe()

    )

    assert np.isclose(

        df["Weight"].sum(),

        100.0

    )


###############################################################################
# Allocation Dispatcher
###############################################################################

def test_allocate_portfolio():

    df = allocate_portfolio(

        sample_dataframe()

    )

    assert np.isclose(

        df["Weight"].sum(),

        100.0

    )


###############################################################################
# Risk Filter
###############################################################################

def test_apply_risk_filters():

    df = apply_risk_filters(

        sample_dataframe()

    )

    assert len(df) > 0


###############################################################################
# Remove Negative Expectancy
###############################################################################

def test_negative_expectancy_removed():

    df = apply_risk_filters(

        sample_dataframe()

    )

    assert (

        df["Expectancy"] >= 0

    ).all()


###############################################################################
# Minimum Profit Factor
###############################################################################

def test_profit_factor_filter():

    df = apply_risk_filters(

        sample_dataframe()

    )

    assert (

        df["Profit Factor"] >= 1

    ).all()


###############################################################################
# Duplicate Stocks
###############################################################################

def test_duplicate_stocks_removed():

    df = sample_dataframe()

    duplicate = df.iloc[[0]].copy()

    df = pd.concat(

        [

            df,

            duplicate

        ],

        ignore_index=True

    )

    filtered = apply_risk_filters(df)

    assert (

        filtered["Stock"]

        .duplicated()

        .sum()

        == 0

    )


###############################################################################
# Portfolio Total Weight
###############################################################################

def test_total_weight():

    df = allocate_portfolio(

        sample_dataframe()

    )

    assert round(

        df["Weight"].sum(),

        2

    ) == 100.00


###############################################################################
# Positive Weights
###############################################################################

def test_positive_weights():

    df = allocate_portfolio(

        sample_dataframe()

    )

    assert (

        df["Weight"] > 0

    ).all()


###############################################################################
# No Missing Weights
###############################################################################

def test_no_missing_weights():

    df = allocate_portfolio(

        sample_dataframe()

    )

    assert (

        df["Weight"]

        .isna()

        .sum()

        == 0

    )