"""
metrics.py
==========

Reusable KPI metrics for the
Institutional Strategy Platform.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

# ==========================================================
# Helpers
# ==========================================================


def first_existing(
    df: pd.DataFrame,
    *columns: str,
) -> str | None:
    """
    Return the first column that exists.
    """

    for column in columns:
        if column in df.columns:
            return column

    return None


# ==========================================================
# Generic KPI
# ==========================================================


def kpi(
    label: str,
    value,
    delta=None,
    help_text=None,
):
    """
    Generic KPI.
    """

    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text,
    )


# ==========================================================
# Dataset Summary
# ==========================================================


def dataset_summary(df: pd.DataFrame):
    """
    Dataset summary KPIs.
    """

    if df is None or df.empty:
        st.warning("Dataset is empty.")
        return

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi("Rows", len(df))

    with c2:
        kpi("Columns", len(df.columns))

    with c3:
        kpi(
            "Missing",
            int(df.isna().sum().sum()),
        )

    with c4:
        kpi(
            "Memory (KB)",
            round(
                df.memory_usage(deep=True).sum() / 1024,
                2,
            ),
        )


# ==========================================================
# Strategy KPIs
# ==========================================================


def strategy_metrics(df: pd.DataFrame):
    """
    Strategy metrics.
    """

    if df.empty:
        return

    c1, c2, c3, c4 = st.columns(4)

    strategy_col = first_existing(
        df,
        "Strategy",
        "Strategy Rank",
    )

    composite_col = first_existing(
        df,
        "Composite Score",
        "AverageComposite",
    )

    edge_col = first_existing(
        df,
        "Edge Score",
    )

    expectancy_col = first_existing(
        df,
        "Weighted Expectancy",
        "Weighted Expectancy%",
        "AverageWeightedExpectancy",
    )

    with c1:
        value = df[strategy_col].nunique() if strategy_col == "Strategy" else len(df)

        kpi("Strategies", value)

    with c2:
        if composite_col:
            kpi(
                "Avg Composite",
                round(df[composite_col].mean(), 2),
            )

    with c3:
        if edge_col:
            kpi(
                "Avg Edge",
                round(df[edge_col].mean(), 2),
            )

    with c4:
        if expectancy_col:
            kpi(
                "Avg Weighted Expectancy",
                f"{df[expectancy_col].mean():.2f}",
            )


# ==========================================================
# Stock KPIs
# ==========================================================


def stock_metrics(df: pd.DataFrame):
    """
    Stock metrics.
    """

    if df.empty:
        return

    c1, c2, c3, c4 = st.columns(4)

    score_col = first_existing(
        df,
        "Institutional Score",
    )

    edge_col = first_existing(
        df,
        "Edge Score",
    )

    with c1:
        kpi(
            "Stocks",
            df["Stock"].nunique(),
        )

    with c2:
        if score_col:
            kpi(
                "Avg Score",
                round(df[score_col].mean(), 2),
            )

    with c3:
        if edge_col:
            kpi(
                "Avg Edge",
                round(df[edge_col].mean(), 2),
            )

    with c4:
        if "Recommendation" in df.columns:
            kpi(
                "Strong Buy",
                (df["Recommendation"] == "STRONG BUY").sum(),
            )


# ==========================================================
# Portfolio KPIs
# ==========================================================


def portfolio_metrics(df: pd.DataFrame):
    """
    Portfolio KPIs.
    """

    if df.empty:
        return

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi("Holdings", len(df))

    with c2:
        if "Weight %" in df.columns:
            kpi(
                "Weight",
                f"{df['Weight %'].sum():.2f}%",
            )

    with c3:
        if "Expected Return %" in df.columns:
            kpi(
                "Expected Return",
                f"{df['Expected Return %'].mean():.2f}%",
            )

    with c4:
        if "Institutional Score" in df.columns:
            kpi(
                "Portfolio Score",
                round(
                    df["Institutional Score"].mean(),
                    2,
                ),
            )


# ==========================================================
# Recommendation KPIs
# ==========================================================


def recommendation_metrics(df: pd.DataFrame):
    """
    Recommendation summary.
    """

    if df.empty or "Recommendation" not in df.columns:
        return

    recommendations = [
        "STRONG BUY",
        "BUY",
        "WATCH",
        "IMPROVE",
        "AVOID",
        "REJECT",
    ]

    cols = st.columns(len(recommendations))

    for rec, col in zip(
        recommendations,
        cols,
        strict=False,
    ):
        with col:
            kpi(
                rec,
                (df["Recommendation"] == rec).sum(),
            )


# ==========================================================
# Performance KPIs
# ==========================================================


def performance_metrics(df: pd.DataFrame):
    """
    Performance KPIs.
    """

    if df.empty:
        return

    cols = st.columns(4)

    metric_groups = [
        ("Weighted Expectancy", "Weighted Expectancy%", "AverageWeightedExpectancy"),
        ("Profit Factor", "AverageProfitFactor"),
        ("Reward Risk", "AverageRewardRisk"),
        ("Trades", "Trades / Year"),
    ]

    for group, col in zip(
        metric_groups,
        cols,
        strict=False,
    ):
        with col:
            metric = first_existing(df, *group)

            if metric is None:
                continue

            value = round(df[metric].mean(), 2)

            display = f"{value:.2f}%" if "%" in metric else f"{value:.2f}"

            kpi(metric, display)


# ==========================================================
# Risk KPIs
# ==========================================================


def risk_metrics(df: pd.DataFrame):
    """
    Risk KPIs.
    """

    if df.empty:
        return

    metrics = [
        "Max Drawdown %",
        "Recovery Factor",
        "Volatility",
        "Risk Score",
    ]

    cols = st.columns(4)

    for metric, col in zip(
        metrics,
        cols,
        strict=False,
    ):
        with col:
            if metric not in df.columns:
                continue

            value = round(
                df[metric].mean(),
                2,
            )

            display = f"{value:.2f}%" if "%" in metric else f"{value:.2f}"

            kpi(metric, display)


# ==========================================================
# Executive Dashboard
# ==========================================================


def executive_dashboard(
    strategy_df: pd.DataFrame,
    stock_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
):
    """
    Executive summary KPIs.
    """

    c1, c2, c3 = st.columns(3)

    with c1:
        strategy_col = first_existing(
            strategy_df,
            "Strategy",
            "Strategy Rank",
        )

        if strategy_col == "Strategy":
            strategies = strategy_df[strategy_col].nunique()
        elif strategy_df is not None and not strategy_df.empty:
            strategies = len(strategy_df)
        else:
            strategies = 0

        kpi(
            "Strategies",
            strategies,
        )

    with c2:
        stocks = (
            stock_df["Stock"].nunique()
            if (
                stock_df is not None
                and not stock_df.empty
                and "Stock" in stock_df.columns
            )
            else 0
        )

        kpi(
            "Stocks",
            stocks,
        )

    with c3:
        holdings = len(portfolio_df) if portfolio_df is not None else 0

        kpi(
            "Portfolio Holdings",
            holdings,
        )
