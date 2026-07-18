"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
portfolio/risk_filter.py

Purpose
-------
Institutional risk filtering engine used before
portfolio construction.

Applies standardized institutional quality filters
to retain only high-confidence trading strategies.

=============================================================
"""

from __future__ import annotations

from typing import Callable

import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    EDGE_SCORE,
    RELIABILITY_SCORE,
    EFFICIENCY_SCORE,
    EXPECTANCY,
    PROFIT_FACTOR,
    REWARD_RISK,
    TRADES,
)

from strategy_compare_v4.config.thresholds import (
    MIN_COMPOSITE_SCORE,
    MIN_EDGE_SCORE,
    MIN_RELIABILITY_SCORE,
    MIN_EFFICIENCY_SCORE,
    MIN_EXPECTANCY,
    MIN_PROFIT_FACTOR,
    MIN_REWARD_RISK,
    MIN_TRADES,
    TOP_STOCKS,
)

from strategy_compare_v4.utils.helpers import (
    require_columns,
)

from strategy_compare_v4.utils.math_utils import (
    round_dataframe,
)

from strategy_compare_v4.utils.logger import (
    get_logger,
    banner,
)

logger = get_logger(__name__)


# ============================================================
# Validation
# ============================================================

def validate_input(
    df: pd.DataFrame,
    required_columns: list[str],
) -> pd.DataFrame:
    """
    Validate the input dataframe
    before applying filters.
    """

    banner(

        logger,

        "Validating Risk Filter Input",

    )

    require_columns(

        df,

        required_columns,

    )

    logger.info(

        "Rows             : %d",

        len(

            df,

        ),

    )

    logger.info(

        "Unique Stocks    : %d",

        df["Stock"].nunique(),

    )

    return df.copy()


# ============================================================
# Composite Score Filter
# ============================================================

def filter_composite_score(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove low Composite
    Score strategies.
    """

    df = validate_input(

        df,

        [

            "Stock",

            COMPOSITE_SCORE,

        ],

    )

    filtered = (

        df.loc[

            df[

                COMPOSITE_SCORE

            ]

            >=

            MIN_COMPOSITE_SCORE

        ]

        .copy()

    )

    logger.info(

        "Composite Score Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Edge Score Filter
# ============================================================

def filter_edge_score(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove weak Edge
    Score strategies.
    """

    df = validate_input(

        df,

        [

            "Stock",

            EDGE_SCORE,

        ],

    )

    filtered = (

        df.loc[

            df[

                EDGE_SCORE

            ]

            >=

            MIN_EDGE_SCORE

        ]

        .copy()

    )

    logger.info(

        "Edge Score Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )

# ============================================================
# Reliability Filter
# ============================================================

def filter_reliability(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep reliable
    strategies.
    """

    df = validate_input(

        df,

        [

            "Stock",

            RELIABILITY_SCORE,

        ],

    )

    filtered = (

        df.loc[

            df[

                RELIABILITY_SCORE

            ]

            >=

            MIN_RELIABILITY_SCORE

        ]

        .copy()

    )

    logger.info(

        "Reliability Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Efficiency Filter
# ============================================================

def filter_efficiency(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep efficient
    strategies.
    """

    df = validate_input(

        df,

        [

            "Stock",

            EFFICIENCY_SCORE,

        ],

    )

    filtered = (

        df.loc[

            df[

                EFFICIENCY_SCORE

            ]

            >=

            MIN_EFFICIENCY_SCORE

        ]

        .copy()

    )

    logger.info(

        "Efficiency Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Expectancy Filter
# ============================================================

def filter_expectancy(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep positive
    expectancy strategies.
    """

    df = validate_input(

        df,

        [

            "Stock",

            EXPECTANCY,

        ],

    )

    filtered = (

        df.loc[

            df[

                EXPECTANCY

            ]

            >=

            MIN_EXPECTANCY

        ]

        .copy()

    )

    logger.info(

        "Expectancy Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Profit Factor Filter
# ============================================================

def filter_profit_factor(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep strategies with
    sufficient Profit Factor.
    """

    df = validate_input(

        df,

        [

            "Stock",

            PROFIT_FACTOR,

        ],

    )

    filtered = (

        df.loc[

            df[

                PROFIT_FACTOR

            ]

            >=

            MIN_PROFIT_FACTOR

        ]

        .copy()

    )

    logger.info(

        "Profit Factor Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )

# ============================================================
# Reward / Risk Filter
# ============================================================

def filter_reward_risk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep strategies having
    sufficient Reward/Risk.
    """

    df = validate_input(

        df,

        [

            "Stock",

            REWARD_RISK,

        ],

    )

    filtered = (

        df.loc[

            df[

                REWARD_RISK

            ]

            >=

            MIN_REWARD_RISK

        ]

        .copy()

    )

    logger.info(

        "Reward/Risk Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Trade Count Filter
# ============================================================

def filter_trade_count(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep strategies with
    sufficient trade history.
    """

    df = validate_input(

        df,

        [

            "Stock",

            TRADES,

        ],

    )

    filtered = (

        df.loc[

            df[

                TRADES

            ]

            >=

            MIN_TRADES

        ]

        .copy()

    )

    logger.info(

        "Trade Count Filter : %d -> %d",

        len(df),

        len(filtered),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Top Ranked Filter
# ============================================================

def filter_top_ranked(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep the highest-ranked
    opportunities.
    """

    df = validate_input(

        df,

        [

            "Stock",

            COMPOSITE_SCORE,

        ],

    )

    filtered = (

        df

        .sort_values(

            COMPOSITE_SCORE,

            ascending=False,

        )

        .head(

            TOP_STOCKS,

        )

        .copy()

    )

    logger.info(

        "Top Ranked Filter : %d retained",

        len(

            filtered,

        ),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Remove Duplicates
# ============================================================

def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep only the
    highest-ranked strategy
    for each stock.
    """

    df = validate_input(

        df,

        [

            "Stock",

            COMPOSITE_SCORE,

        ],

    )

    original_rows = len(

        df,

    )

    filtered = (

        df

        .sort_values(

            COMPOSITE_SCORE,

            ascending=False,

        )

        .drop_duplicates(

            subset="Stock",

            keep="first",

        )

        .reset_index(

            drop=True,

        )

    )

    logger.info(

        "Duplicates Removed : %d",

        original_rows

        -

        len(

            filtered,

        ),

    )

    return round_dataframe(

        filtered,

        decimals=2,

    )


# ============================================================
# Institutional Risk Filter Pipeline
# ============================================================

def apply_risk_filters(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply the complete
    institutional risk
    filtering pipeline.
    """

    banner(

        logger,

        "Institutional Risk Filter",

    )

    filters: list[

        Callable[[pd.DataFrame], pd.DataFrame]

    ] = [

        filter_expectancy,

        filter_profit_factor,

        filter_reward_risk,

        filter_trade_count,

        filter_edge_score,

        filter_reliability,

        filter_efficiency,

        filter_composite_score,

        remove_duplicates,

        filter_top_ranked,

    ]

    filtered = df.copy()

    logger.info(

        "Initial Universe : %d",

        len(

            filtered,

        ),

    )

    for risk_filter in filters:

        filtered = risk_filter(

            filtered,

        )

    filtered = (

        filtered

        .reset_index(

            drop=True,

        )

    )

    filtered = round_dataframe(

        filtered,

        decimals=2,

    )

    logger.info(

        "Final Universe : %d",

        len(

            filtered,

        ),

    )

    logger.info(

        "Institutional risk filtering completed."

    )

    return filtered