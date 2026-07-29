"""
ui.metrics
==========

Reusable KPI and formatting utilities for the
Institutional Scanner Monitor.

Features
--------
- KPI cards
- Currency formatting
- Percentage formatting
- Numeric formatting
- Delta formatting
- Portfolio metrics
- Summary metrics
- DataFrame metric extraction
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from ui.theme import (
    THEME,
    format_currency,
    format_number,
    format_percent,
)

# =============================================================================
# Generic Helpers
# =============================================================================


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """

    try:

        if pd.isna(value):

            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert to integer.
    """

    try:

        if pd.isna(value):

            return default

        return int(float(value))

    except (
        TypeError,
        ValueError,
    ):

        return default


# =============================================================================
# DataFrame Helpers
# =============================================================================


def metric_value(
    summary: pd.DataFrame,
    metric: str,
    default: float = 0.0,
) -> float:
    """
    Read a metric from a Metric/Value table.

    Expected format:

    Metric | Value
    ---------------
    Return | 12.5
    """

    if summary.empty:

        return default

    if (
        "Metric" not in summary.columns
        or "Value" not in summary.columns
    ):

        return default

    row = summary.loc[
        summary["Metric"] == metric
    ]

    if row.empty:

        return default

    return safe_float(
        row.iloc[0]["Value"],
        default,
    )


def metric_exists(
    summary: pd.DataFrame,
    metric: str,
) -> bool:
    """
    Check whether metric exists.
    """

    if summary.empty:

        return False

    if "Metric" not in summary.columns:

        return False

    return metric in summary["Metric"].values


# =============================================================================
# Streamlit Metrics
# =============================================================================


def show_metric(
    label: str,
    value: Any,
    *,
    delta: Any | None = None,
    help_text: str | None = None,
) -> None:
    """
    Standard metric card.
    """

    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text,
    )


def show_currency_metric(
    label: str,
    value: float,
    *,
    delta: float | None = None,
) -> None:
    """
    Currency metric.
    """

    delta_text = None

    if delta is not None:

        delta_text = format_currency(delta)

    st.metric(
        label=label,
        value=format_currency(value),
        delta=delta_text,
    )


def show_percent_metric(
    label: str,
    value: float,
    *,
    delta: float | None = None,
) -> None:
    """
    Percentage metric.
    """

    delta_text = None

    if delta is not None:

        delta_text = format_percent(delta)

    st.metric(
        label=label,
        value=format_percent(value),
        delta=delta_text,
    )


def show_number_metric(
    label: str,
    value: float,
) -> None:
    """
    Numeric metric.
    """

    st.metric(
        label=label,
        value=format_number(value),
    )


# =============================================================================
# Portfolio KPIs
# =============================================================================


def portfolio_kpis(
    summary: pd.DataFrame,
) -> None:
    """
    Render institutional portfolio KPIs.
    """

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        show_currency_metric(
            "Portfolio Value",
            metric_value(
                summary,
                "Portfolio Value",
            ),
        )

    with col2:

        show_percent_metric(
            "Expected Return",
            metric_value(
                summary,
                "Expected Return",
            ),
        )

    with col3:

        show_percent_metric(
            "Portfolio Risk",
            metric_value(
                summary,
                "Portfolio Risk",
            ),
        )

    with col4:

        show_number_metric(
            "Holdings",
            metric_value(
                summary,
                "Number of Holdings",
            ),
        )


# =============================================================================
# Risk KPIs
# =============================================================================


def risk_kpis(
    risk_summary: pd.DataFrame,
) -> None:
    """
    Display risk summary metrics.
    """

    col1, col2, col3 = st.columns(3)

    with col1:

        show_percent_metric(
            "Volatility",
            metric_value(
                risk_summary,
                "Portfolio Volatility",
            ),
        )

    with col2:

        show_percent_metric(
            "Drawdown",
            metric_value(
                risk_summary,
                "Maximum Drawdown",
            ),
        )

    with col3:

        show_percent_metric(
            "Value at Risk",
            metric_value(
                risk_summary,
                "Value at Risk",
            ),
        )


# =============================================================================
# Execution KPIs
# =============================================================================


def execution_kpis(
    execution: pd.DataFrame,
) -> None:
    """
    Execution summary metrics.
    """

    col1, col2, col3 = st.columns(3)

    with col1:

        show_number_metric(
            "Buy Orders",
            metric_value(
                execution,
                "Buy Orders",
            ),
        )

    with col2:

        show_number_metric(
            "Sell Orders",
            metric_value(
                execution,
                "Sell Orders",
            ),
        )

    with col3:

        show_number_metric(
            "Rebalance Orders",
            metric_value(
                execution,
                "Rebalance Orders",
            ),
        )


# =============================================================================
# Status Badge
# =============================================================================


def status_badge(
    status: str,
) -> None:
    """
    Render a colored status badge.
    """

    color = THEME.INFO

    value = status.upper()

    if value == "ACTIVE":

        color = THEME.INFO

    elif value == "TARGET HIT":

        color = THEME.SUCCESS

    elif value == "STOP HIT":

        color = THEME.DANGER

    elif value == "EXIT DUE":

        color = THEME.WARNING

    st.markdown(
        f"""
<div
style="
display:inline-block;
padding:5px 12px;
border-radius:12px;
background:{color};
color:white;
font-weight:600;
font-size:0.85rem;
">
{status}
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# Summary Statistics
# =============================================================================


def dataframe_statistics(
    df: pd.DataFrame,
) -> dict[str, int]:
    """
    Basic dataset statistics.
    """

    return {

        "Rows": len(df),

        "Columns": len(df.columns),

        "Missing Values": int(
            df.isna().sum().sum()
        ),

        "Duplicate Rows": int(
            df.duplicated().sum()
        ),

    }


def dataframe_info(
    df: pd.DataFrame,
) -> None:
    """
    Display dataframe statistics.
    """

    stats = dataframe_statistics(df)

    cols = st.columns(len(stats))

    for col, (key, value) in zip(
        cols,
        stats.items(),
    ):

        with col:

            st.metric(
                key,
                value,
            )