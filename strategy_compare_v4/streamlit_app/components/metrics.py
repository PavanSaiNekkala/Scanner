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
        kpi(
            "Rows",
            len(df),
        )

    with c2:
        kpi(
            "Columns",
            len(df.columns),
        )

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

    with c1:
        kpi(
            "Strategies",
            df["Strategy"].nunique(),
        )

    with c2:
        if "Composite Score" in df.columns:
            kpi(
                "Avg Composite",
                round(
                    df["Composite Score"].mean(),
                    2,
                ),
            )

    with c3:
        if "Edge Score" in df.columns:
            kpi(
                "Avg Edge",
                round(
                    df["Edge Score"].mean(),
                    2,
                ),
            )

    with c4:
        if "Expectancy%" in df.columns:
            kpi(
                "Avg Expectancy",
                f"{df['Expectancy%'].mean():.2f}%",
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

    with c1:
        kpi(
            "Stocks",
            df["Stock"].nunique(),
        )

    with c2:
        if "Institutional Score" in df.columns:
            kpi(
                "Avg Score",
                round(
                    df["Institutional Score"].mean(),
                    2,
                ),
            )

    with c3:
        if "Edge Score" in df.columns:
            kpi(
                "Avg Edge",
                round(
                    df["Edge Score"].mean(),
                    2,
                ),
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
        kpi(
            "Holdings",
            len(df),
        )

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

    metrics = [
        "Expectancy%",
        "Profit Factor",
        "Reward Risk",
        "Trades / Year",
    ]

    for metric, col in zip(
        metrics,
        cols,
        strict=False,
    ):
        with col:
            if metric in df.columns:
                value = round(
                    df[metric].mean(),
                    2,
                )

                display_value = f"{value:.2f}%" if "%" in metric else f"{value:.2f}"

                kpi(
                    metric,
                    display_value,
                )


# ==========================================================
# Risk KPIs
# ==========================================================


def risk_metrics(df: pd.DataFrame):
    """
    Risk statistics.
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
            if metric in df.columns:
                value = round(
                    df[metric].mean(),
                    2,
                )

                display_value = f"{value:.2f}%" if "%" in metric else f"{value:.2f}"

                kpi(
                    metric,
                    display_value,
                )


# ==========================================================
# Executive Dashboard
# ==========================================================


def executive_dashboard(
    strategy_df,
    stock_df,
    portfolio_df,
):
    """
    Executive summary.
    """

    c1, c2, c3 = st.columns(3)

    with c1:
        if strategy_df is not None:
            kpi(
                "Strategies",
                strategy_df["Strategy"].nunique(),
            )

    with c2:
        if stock_df is not None:
            kpi(
                "Stocks",
                stock_df["Stock"].nunique(),
            )

    with c3:
        if portfolio_df is not None:
            kpi(
                "Portfolio Holdings",
                len(portfolio_df),
            )
