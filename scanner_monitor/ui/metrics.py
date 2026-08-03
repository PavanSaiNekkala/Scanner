"""
ui.metrics
==========

Reusable KPI utilities for the
Institutional Scanner Monitor.

Provides standardized:

- KPI formatting
- Metric extraction
- Numeric helpers
- Portfolio metrics
- Dashboard metrics
"""

from __future__ import annotations

from dataclasses import dataclass
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
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class MetricConfig:
    """
    Shared metric configuration.
    """

    currency_symbol: str = "₹"

    missing_text: str = "-"

    default_float: float = 0.0

    default_integer: int = 0

    precision: int = 2


CONFIG = MetricConfig()

# =============================================================================
# Safe Conversion Helpers
# =============================================================================


def safe_float(
    value: Any,
    default: float = CONFIG.default_float,
) -> float:
    """
    Safely convert value
    to float.
    """

    try:

        if pd.isna(

            value,

        ):

            return default

        return float(

            value,

        )

    except (

        TypeError,

        ValueError,

    ):

        return default


def safe_integer(
    value: Any,
    default: int = CONFIG.default_integer,
) -> int:
    """
    Safely convert value
    to integer.
    """

    try:

        if pd.isna(

            value,

        ):

            return default

        return int(

            float(

                value,

            )

        )

    except (

        TypeError,

        ValueError,

    ):

        return default


def safe_string(
    value: Any,
    default: str = CONFIG.missing_text,
) -> str:
    """
    Safely convert value
    to string.
    """

    if value is None:

        return default

    try:

        if pd.isna(

            value,

        ):

            return default

    except Exception:

        pass

    text = str(

        value,

    ).strip()

    return (

        text

        if text

        else default

    )

# =============================================================================
# Formatting Engine
# =============================================================================


def format_value(
    value: Any,
) -> str:
    """
    Generic formatter.
    """

    if value is None:

        return CONFIG.missing_text

    if isinstance(

        value,

        bool,

    ):

        return str(

            value,

        )

    if isinstance(

        value,

        int,

    ):

        return format_number(

            value,

        )

    if isinstance(

        value,

        float,

    ):

        return format_number(

            value,

        )

    return safe_string(

        value,

    )


def format_metric_number(
    value: Any,
) -> str:
    """
    Numeric KPI formatter.
    """

    return format_number(

        safe_float(

            value,

        )

    )


def format_metric_currency(
    value: Any,
) -> str:
    """
    Currency KPI formatter.
    """

    return format_currency(

        safe_float(

            value,

        )

    )


def format_metric_percent(
    value: Any,
) -> str:
    """
    Percentage KPI formatter.
    """

    return format_percent(

        safe_float(

            value,

        )

    )


def format_delta(
    value: Any,
) -> str | None:
    """
    Format delta values.
    """

    if value is None:

        return None

    return format_number(

        safe_float(

            value,

        )

    )

# =============================================================================
# Metric Extraction
# =============================================================================


def metric_exists(
    summary: pd.DataFrame,
    metric: str,
) -> bool:
    """
    Return True when a metric exists.
    """

    if summary.empty:

        return False

    required = {

        "Metric",

        "Value",

    }

    if not required.issubset(

        summary.columns,

    ):

        return False

    return (

        summary["Metric"]

        .astype(str)

        .eq(metric)

        .any()

    )


def metric_value(
    summary: pd.DataFrame,
    metric: str,
    default: float = CONFIG.default_float,
) -> float:
    """
    Read a numeric metric.
    """

    if not metric_exists(

        summary,

        metric,

    ):

        return default

    value = (

        summary.loc[

            summary["Metric"]

            ==

            metric,

            "Value",

        ]

        .iloc[0]

    )

    return safe_float(

        value,

        default,

    )


def metric_text(
    summary: pd.DataFrame,
    metric: str,
    default: str = CONFIG.missing_text,
) -> str:
    """
    Read a text metric.
    """

    if not metric_exists(

        summary,

        metric,

    ):

        return default

    value = (

        summary.loc[

            summary["Metric"]

            ==

            metric,

            "Value",

        ]

        .iloc[0]

    )

    return safe_string(

        value,

        default,

    )


def metric_integer(
    summary: pd.DataFrame,
    metric: str,
    default: int = CONFIG.default_integer,
) -> int:
    """
    Read an integer metric.
    """

    if not metric_exists(

        summary,

        metric,

    ):

        return default

    value = (

        summary.loc[

            summary["Metric"]

            ==

            metric,

            "Value",

        ]

        .iloc[0]

    )

    return safe_integer(

        value,

        default,

    )


# =============================================================================
# Metric Collections
# =============================================================================


def metric_dictionary(
    summary: pd.DataFrame,
) -> dict[str, Any]:
    """
    Convert Metric/Value table
    into a dictionary.
    """

    if summary.empty:

        return {}

    required = {

        "Metric",

        "Value",

    }

    if not required.issubset(

        summary.columns,

    ):

        return {}

    return dict(

        zip(

            summary["Metric"],

            summary["Value"],

            strict=False,

        )

    )


def available_metrics(
    summary: pd.DataFrame,
) -> list[str]:
    """
    Return available metrics.
    """

    if summary.empty:

        return []

    if "Metric" not in summary.columns:

        return []

    return sorted(

        summary["Metric"]

        .astype(str)

        .tolist()

    )


# =============================================================================
# Generic KPI Components
# =============================================================================


def show_metric(
    label: str,
    value: Any,
    *,
    delta: Any | None = None,
    help_text: str | None = None,
) -> None:
    """
    Standard Streamlit KPI.
    """

    st.metric(

        label=label,

        value=format_value(

            value,

        ),

        delta=(

            format_delta(

                delta,

            )

            if delta is not None

            else None

        ),

        help=help_text,

    )


def show_number_metric(
    label: str,
    value: Any,
) -> None:
    """
    Numeric KPI.
    """

    st.metric(

        label,

        format_metric_number(

            value,

        ),

    )


def show_currency_metric(
    label: str,
    value: Any,
    *,
    delta: Any | None = None,
) -> None:
    """
    Currency KPI.
    """

    st.metric(

        label,

        format_metric_currency(

            value,

        ),

        delta=(

            format_metric_currency(

                delta,

            )

            if delta is not None

            else None

        ),

    )


def show_percent_metric(
    label: str,
    value: Any,
    *,
    delta: Any | None = None,
) -> None:
    """
    Percentage KPI.
    """

    st.metric(

        label,

        format_metric_percent(

            value,

        ),

        delta=(

            format_metric_percent(

                delta,

            )

            if delta is not None

            else None

        ),

    )

# =============================================================================
# KPI Row
# =============================================================================


def metric_row(
    metrics: list[
        tuple[
            str,
            Any,
            str,
        ]
    ],
) -> None:
    """
    Display a horizontal KPI row.

    Metric Types
    ------------
    number
    currency
    percent
    """

    if not metrics:

        return

    columns = st.columns(

        len(

            metrics,

        )

    )

    for column, metric in zip(

        columns,

        metrics,

    ):

        label, value, metric_type = metric

        with column:

            if metric_type == "currency":

                show_currency_metric(

                    label,

                    value,

                )

            elif metric_type == "percent":

                show_percent_metric(

                    label,

                    value,

                )

            else:

                show_number_metric(

                    label,

                    value,

                )


# =============================================================================
# Executive KPIs
# =============================================================================

def executive_metrics(
    *,
    portfolio_value: float,
    expected_return: float,
    portfolio_risk: float,
    holdings: int,
) -> None:
    """
    Executive dashboard KPIs.
    """

    metric_row(

        [

            (

                "Portfolio Value",

                portfolio_value,

                "currency",

            ),

            (

                "Expected Return",

                expected_return,

                "percent",

            ),

            (

                "Portfolio Risk",

                portfolio_risk,

                "percent",

            ),

            (

                "Holdings",

                holdings,

                "number",

            ),

        ]

    )


# =============================================================================
# Portfolio KPIs
# =============================================================================


def portfolio_kpis(
    summary: pd.DataFrame,
) -> None:
    """
    Portfolio dashboard KPIs.
    """

    executive_metrics(

        portfolio_value=metric_value(

            summary,

            "Portfolio Value",

        ),

        expected_return=metric_value(

            summary,

            "Expected Return",

        ),

        portfolio_risk=metric_value(

            summary,

            "Portfolio Risk",

        ),

        holdings=metric_integer(

            summary,

            "Number of Holdings",

        ),

    )


# =============================================================================
# Holdings KPIs
# =============================================================================


def holdings_kpis(
    holdings: pd.DataFrame,
) -> None:
    """
    Holdings overview.
    """

    if holdings.empty:

        return

    metric_row(

        [

            (

                "Holdings",

                len(

                    holdings,

                ),

                "number",

            ),

            (

                "Columns",

                len(

                    holdings.columns,

                ),

                "number",

            ),

            (

                "Missing",

                int(

                    holdings

                    .isna()

                    .sum()

                    .sum()

                ),

                "number",

            ),

            (

                "Duplicates",

                int(

                    holdings

                    .duplicated()

                    .sum()

                ),

                "number",

            ),

        ]

    )


# =============================================================================
# Summary KPIs
# =============================================================================


def summary_metrics(
    summary: dict[
        str,
        Any,
    ],
) -> None:
    """
    Render summary metrics
    from a dictionary.
    """

    metrics = []

    for label, value in (

        summary.items()

    ):

        if isinstance(

            value,

            float,

        ):

            metric_type = "number"

        elif isinstance(

            value,

            int,

        ):

            metric_type = "number"

        else:

            metric_type = "number"

        metrics.append(

            (

                label,

                value,

                metric_type,

            )

        )

    metric_row(

        metrics,

    )

# =============================================================================
# Risk KPIs
# =============================================================================


def risk_kpis(
    summary: pd.DataFrame,
) -> None:
    """
    Display portfolio risk KPIs.
    """

    metric_row(

        [

            (

                "Volatility",

                metric_value(

                    summary,

                    "Portfolio Volatility",

                ),

                "percent",

            ),

            (

                "Maximum Drawdown",

                metric_value(

                    summary,

                    "Maximum Drawdown",

                ),

                "percent",

            ),

            (

                "Value at Risk",

                metric_value(

                    summary,

                    "Value at Risk",

                ),

                "percent",

            ),

        ]

    )


# =============================================================================
# Execution KPIs
# =============================================================================


def execution_kpis(
    summary: pd.DataFrame,
) -> None:
    """
    Display execution KPIs.
    """

    metric_row(

        [

            (

                "Buy Orders",

                metric_integer(

                    summary,

                    "Buy Orders",

                ),

                "number",

            ),

            (

                "Sell Orders",

                metric_integer(

                    summary,

                    "Sell Orders",

                ),

                "number",

            ),

            (

                "Rebalance Orders",

                metric_integer(

                    summary,

                    "Rebalance Orders",

                ),

                "number",

            ),

        ]

    )


# =============================================================================
# Performance KPIs
# =============================================================================


def performance_kpis(
    summary: pd.DataFrame,
) -> None:
    """
    Display performance KPIs.
    """

    metric_row(

        [

            (

                "Total Return",

                metric_value(

                    summary,

                    "Total Return",

                ),

                "percent",

            ),

            (

                "Annual Return",

                metric_value(

                    summary,

                    "Annual Return",

                ),

                "percent",

            ),

            (

                "Sharpe Ratio",

                metric_value(

                    summary,

                    "Sharpe Ratio",

                ),

                "number",

            ),

            (

                "Sortino Ratio",

                metric_value(

                    summary,

                    "Sortino Ratio",

                ),

                "number",

            ),

        ]

    )

# =============================================================================
# Daily Monitor KPIs
# =============================================================================


def daily_monitor_kpis(
    daily_monitor: pd.DataFrame,
    portfolio_summary: pd.DataFrame | None = None,
    risk_summary: pd.DataFrame | None = None,
) -> None:
    """
    Display Daily Monitor KPI cards.

    Parameters
    ----------
    daily_monitor:
        Latest scanner output.

    portfolio_summary:
        Optional portfolio summary.

    risk_summary:
        Optional risk summary.
    """

    if daily_monitor.empty:

        return


    buy_signals = 0


    for column in (

        "Recommendation",

        "Signal",

        "Action",

    ):

        if column in daily_monitor.columns:

            buy_signals = int(

                daily_monitor[column]

                .astype(str)

                .str.upper()

                .isin(

                    [

                        "BUY",

                        "STRONG BUY",

                    ]

                )

                .sum()

            )

            break


    sectors = 0

    if "Sector" in daily_monitor.columns:

        sectors = (

            daily_monitor["Sector"]

            .nunique()

        )


    risk_reports = 0

    if (

        risk_summary is not None

        and not risk_summary.empty

    ):

        risk_reports = len(
            risk_summary,
        )


    metric_row(

        [

            (

                "Scanner Records",

                len(daily_monitor),

                "number",

            ),

            (

                "Buy Signals",

                buy_signals,

                "number",

            ),

            (

                "Sectors",

                sectors,

                "number",

            ),

            (

                "Risk Reports",

                risk_reports,

                "number",

            ),

        ]

    )

# =============================================================================
# History KPIs
# =============================================================================


def history_kpis(
    portfolio_history: pd.DataFrame,
    performance_history: pd.DataFrame,
    risk_history: pd.DataFrame,
) -> None:
    """
    Display historical analytics KPI cards.
    """

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        show_number_metric(
            "Portfolio Records",
            len(portfolio_history),
        )


    with col2:

        show_number_metric(
            "Performance Records",
            len(performance_history),
        )


    with col3:

        show_number_metric(
            "Risk Records",
            len(risk_history),
        )


    with col4:

        total_records = (

            len(portfolio_history)

            +

            len(performance_history)

            +

            len(risk_history)

        )

        show_number_metric(
            "Total History",
            total_records,
        )

# =============================================================================
# Status Badge
# =============================================================================


_STATUS_COLORS = {

    "ACTIVE":

        THEME.INFO,

    "BUY":

        THEME.SUCCESS,

    "SELL":

        THEME.DANGER,

    "WATCH":

        THEME.WARNING,

    "TARGET HIT":

        THEME.SUCCESS,

    "STOP HIT":

        THEME.DANGER,

    "EXIT":

        THEME.WARNING,

    "EXIT DUE":

        THEME.WARNING,

}


def status_badge(
    status: str,
) -> None:
    """
    Render a colored status badge.
    """

    color = _STATUS_COLORS.get(

        safe_string(

            status,

        ).upper(),

        THEME.INFO,

    )

    st.markdown(

        f"""
<div
style="
display:inline-block;
padding:6px 14px;
border-radius:16px;
background:{color};
color:white;
font-weight:600;
font-size:0.85rem;
">

{safe_string(status)}

</div>
""",

        unsafe_allow_html=True,

    )


# =============================================================================
# DataFrame Statistics
# =============================================================================


def dataframe_statistics(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    """
    Return dataset statistics.
    """

    if dataframe.empty:

        return {

            "Rows": 0,

            "Columns": 0,

            "Missing Values": 0,

            "Duplicate Rows": 0,

        }

    return {

        "Rows":

            len(

                dataframe,

            ),

        "Columns":

            len(

                dataframe.columns,

            ),

        "Missing Values":

            int(

                dataframe

                .isna()

                .sum()

                .sum()

            ),

        "Duplicate Rows":

            int(

                dataframe

                .duplicated()

                .sum()

            ),

    }


def dataframe_info(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display dataset information.
    """

    metrics = dataframe_statistics(

        dataframe,

    )

    metric_row(

        [

            (

                label,

                value,

                "number",

            )

            for label, value

            in metrics.items()

        ]

    )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    "CONFIG",

    "safe_float",

    "safe_integer",

    "safe_string",

    "format_value",

    "format_metric_number",

    "format_metric_currency",

    "format_metric_percent",

    "format_delta",

    "metric_exists",

    "metric_value",

    "metric_text",

    "metric_integer",

    "metric_dictionary",

    "available_metrics",

    "show_metric",

    "show_number_metric",

    "show_currency_metric",

    "show_percent_metric",

    "metric_row",

    "executive_metrics",

    "portfolio_kpis",

    "holdings_kpis",

    "summary_metrics",

    "risk_kpis",

    "execution_kpis",

    "daily_monitor_kpis",

    "history_kpis",

    "performance_kpis",

    "status_badge",

    "dataframe_statistics",

    "dataframe_info",

]