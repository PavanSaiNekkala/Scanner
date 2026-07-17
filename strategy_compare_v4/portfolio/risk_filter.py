"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    portfolio/risk_filter.py

Purpose:
    Institutional risk filters applied before
    portfolio allocation.

=============================================================
"""

from __future__ import annotations

import pandas as pd

from config.thresholds import (
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


###############################################################################
# Composite Score Filter
###############################################################################

def filter_composite_score(df):
    """
    Remove low composite score strategies.
    """

    return df.loc[
        df["Composite Score"] >= MIN_COMPOSITE_SCORE
    ].copy()


###############################################################################
# Edge Score Filter
###############################################################################

def filter_edge_score(df):
    """
    Remove weak edge strategies.
    """

    return df.loc[
        df["Edge Score"] >= MIN_EDGE_SCORE
    ].copy()


###############################################################################
# Reliability Filter
###############################################################################

def filter_reliability(df):
    """
    Keep reliable strategies.
    """

    return df.loc[
        df["Reliability Score"] >= MIN_RELIABILITY_SCORE
    ].copy()


###############################################################################
# Efficiency Filter
###############################################################################

def filter_efficiency(df):
    """
    Keep efficient strategies.
    """

    return df.loc[
        df["Efficiency Score"] >= MIN_EFFICIENCY_SCORE
    ].copy()


###############################################################################
# Expectancy Filter
###############################################################################

def filter_expectancy(df):
    """
    Positive expectancy only.
    """

    return df.loc[
        df["Expectancy"] >= MIN_EXPECTANCY
    ].copy()


###############################################################################
# Profit Factor Filter
###############################################################################

def filter_profit_factor(df):
    """
    Profit Factor filter.
    """

    return df.loc[
        df["Profit Factor"] >= MIN_PROFIT_FACTOR
    ].copy()


###############################################################################
# Reward Risk Filter
###############################################################################

def filter_reward_risk(df):
    """
    Reward/Risk filter.
    """

    return df.loc[
        df["Reward Risk"] >= MIN_REWARD_RISK
    ].copy()


###############################################################################
# Trade Count Filter
###############################################################################

def filter_trade_count(df):
    """
    Minimum historical trades.
    """

    return df.loc[
        df["Trades"] >= MIN_TRADES
    ].copy()


###############################################################################
# Top Ranked Filter
###############################################################################

def filter_top_ranked(df):
    """
    Keep highest ranked opportunities.
    """

    return (
        df.sort_values(
            "Composite Score",
            ascending=False
        )
        .head(TOP_STOCKS)
        .copy()
    )


###############################################################################
# Remove Duplicates
###############################################################################

def remove_duplicates(df):
    """
    One entry per stock.
    """

    return (
        df.sort_values(
            "Composite Score",
            ascending=False
        )
        .drop_duplicates(
            subset="Stock",
            keep="first"
        )
        .reset_index(drop=True)
    )


###############################################################################
# Full Risk Filter
###############################################################################

def apply_risk_filters(df):
    """
    Apply all institutional filters.
    """

    df = filter_expectancy(df)

    df = filter_profit_factor(df)

    df = filter_reward_risk(df)

    df = filter_trade_count(df)

    df = filter_edge_score(df)

    df = filter_reliability(df)

    df = filter_efficiency(df)

    df = filter_composite_score(df)

    df = remove_duplicates(df)

    df = filter_top_ranked(df)

    return df.reset_index(drop=True)