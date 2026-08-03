"""
ui/charts.py
============

Reusable Plotly charts for the
Institutional Scanner Monitor.

This module centralizes every
chart used throughout the
dashboard.

Author
------
Nekkala Pavan Sai
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.theme import THEME

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class ChartConfig:
    """
    Shared chart configuration.
    """

    height: int = 420

    template: str = "plotly_white"

    legend: bool = True

    margin_left: int = 10

    margin_right: int = 10

    margin_top: int = 40

    margin_bottom: int = 10


CONFIG = ChartConfig()

# =============================================================================
# Theme
# =============================================================================

COLORS = [

    THEME.PRIMARY,

    THEME.SUCCESS,

    THEME.WARNING,

    THEME.INFO,

    THEME.DANGER,

]

# =============================================================================
# Empty Chart
# =============================================================================


def empty_chart(
    message: str = "No chart data available.",
) -> None:
    """
    Display an empty chart message.
    """

    st.info(
        message,
    )

# =============================================================================
# Validation
# =============================================================================


def valid_dataframe(
    dataframe: pd.DataFrame,
) -> bool:
    """
    Validate dataframe.
    """

    return (

        dataframe is not None

        and

        not dataframe.empty

    )


def column_exists(
    dataframe: pd.DataFrame,
    column: str,
) -> bool:
    """
    Validate column.
    """

    return (

        valid_dataframe(
            dataframe,
        )

        and

        column in dataframe.columns

    )


# =============================================================================
# Figure Helpers
# =============================================================================


def apply_layout(
    figure: go.Figure,
    *,
    title: str | None = None,
    x_title: str | None = None,
    y_title: str | None = None,
) -> go.Figure:
    """
    Apply institutional layout.
    """

    figure.update_layout(

        template=CONFIG.template,

        height=CONFIG.height,

        showlegend=CONFIG.legend,

        colorway=COLORS,

        title=title,

        xaxis_title=x_title,

        yaxis_title=y_title,

        margin=dict(

            l=CONFIG.margin_left,

            r=CONFIG.margin_right,

            t=CONFIG.margin_top,

            b=CONFIG.margin_bottom,

        ),

    )

    return figure


def display_chart(
    figure: go.Figure,
) -> None:
    """
    Display Plotly figure.
    """

    st.plotly_chart(

        figure,

        use_container_width=True,

    )

# =============================================================================
# Generic Chart Builder
# =============================================================================


def render_chart(
    figure: go.Figure,
) -> None:
    """
    Apply layout and display.
    """

    display_chart(

        apply_layout(

            figure,

        )

    )

# =============================================================================
# Line Chart
# =============================================================================


def line_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
    markers: bool = True,
) -> None:
    """
    Display a line chart.
    """

    if not (

        column_exists(
            dataframe,
            x,
        )

        and

        column_exists(
            dataframe,
            y,
        )

    ):

        empty_chart()

        return

    figure = px.line(

        dataframe,

        x=x,

        y=y,

        color=color,

        markers=markers,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Bar Chart
# =============================================================================


def bar_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
    text: str | None = None,
) -> None:
    """
    Display a vertical bar chart.
    """

    if not (

        column_exists(
            dataframe,
            x,
        )

        and

        column_exists(
            dataframe,
            y,
        )

    ):

        empty_chart()

        return

    figure = px.bar(

        dataframe,

        x=x,

        y=y,

        color=color,

        text=text,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Horizontal Bar Chart
# =============================================================================


def horizontal_bar_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
    text: str | None = None,
) -> None:
    """
    Display a horizontal bar chart.
    """

    if not (

        column_exists(
            dataframe,
            x,
        )

        and

        column_exists(
            dataframe,
            y,
        )

    ):

        empty_chart()

        return

    figure = px.bar(

        dataframe,

        x=x,

        y=y,

        orientation="h",

        color=color,

        text=text,

    )

    figure.update_layout(

        yaxis=dict(

            autorange="reversed",

        ),

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Scatter Chart
# =============================================================================


def scatter_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
    hover_name: str | None = None,
) -> None:
    """
    Display a scatter chart.
    """

    if not (

        column_exists(
            dataframe,
            x,
        )

        and

        column_exists(
            dataframe,
            y,
        )

    ):

        empty_chart()

        return

    figure = px.scatter(

        dataframe,

        x=x,

        y=y,

        color=color,

        hover_name=hover_name,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Histogram
# =============================================================================


def histogram_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    title: str | None = None,
    bins: int = 30,
) -> None:
    """
    Display a histogram.
    """

    if not column_exists(

        dataframe,

        x,

    ):

        empty_chart()

        return

    figure = px.histogram(

        dataframe,

        x=x,

        nbins=bins,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

        )

    )


# =============================================================================
# Pie Chart
# =============================================================================


def pie_chart(
    dataframe: pd.DataFrame,
    *,
    names: str,
    values: str,
    title: str | None = None,
    hole: float = 0.45,
) -> None:
    """
    Display a pie / donut chart.
    """

    if not (

        column_exists(
            dataframe,
            names,
        )

        and

        column_exists(
            dataframe,
            values,
        )

    ):

        empty_chart()

        return

    figure = px.pie(

        dataframe,

        names=names,

        values=values,

        hole=hole,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

        )

    )

# =============================================================================
# Treemap
# =============================================================================


def treemap_chart(
    dataframe: pd.DataFrame,
    *,
    path: list[str],
    values: str,
    title: str | None = None,
    color: str | None = None,
) -> None:
    """
    Display a treemap.
    """

    if not valid_dataframe(
        dataframe,
    ):

        empty_chart()

        return

    if values not in dataframe.columns:

        empty_chart()

        return

    figure = px.treemap(

        dataframe,

        path=path,

        values=values,

        color=color,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

        )

    )


# =============================================================================
# Area Chart
# =============================================================================


def area_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
) -> None:
    """
    Display an area chart.
    """

    if not (

        column_exists(
            dataframe,
            x,
        )

        and

        column_exists(
            dataframe,
            y,
        )

    ):

        empty_chart()

        return

    figure = px.area(

        dataframe,

        x=x,

        y=y,

        color=color,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Box Plot
# =============================================================================


def box_chart(
    dataframe: pd.DataFrame,
    *,
    x: str | None = None,
    y: str | None = None,
    title: str | None = None,
    color: str | None = None,
) -> None:
    """
    Display a box plot.
    """

    if y is None:

        empty_chart()

        return

    if not column_exists(
        dataframe,
        y,
    ):

        empty_chart()

        return

    figure = px.box(

        dataframe,

        x=x,

        y=y,

        color=color,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Violin Plot
# =============================================================================


def violin_chart(
    dataframe: pd.DataFrame,
    *,
    x: str | None = None,
    y: str,
    title: str | None = None,
    color: str | None = None,
    box: bool = True,
) -> None:
    """
    Display a violin plot.
    """

    if not column_exists(
        dataframe,
        y,
    ):

        empty_chart()

        return

    figure = px.violin(

        dataframe,

        x=x,

        y=y,

        color=color,

        box=box,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Bubble Chart
# =============================================================================


def bubble_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    size: str,
    title: str | None = None,
    color: str | None = None,
    hover_name: str | None = None,
) -> None:
    """
    Display a bubble chart.
    """

    required = (

        x,

        y,

        size,

    )

    if any(

        column not in dataframe.columns

        for column in required

    ):

        empty_chart()

        return

    figure = px.scatter(

        dataframe,

        x=x,

        y=y,

        size=size,

        color=color,

        hover_name=hover_name,

    )

    render_chart(

        apply_layout(

            figure,

            title=title,

            x_title=x,

            y_title=y,

        )

    )


# =============================================================================
# Timeline Chart
# =============================================================================


def timeline_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
) -> None:
    """
    Generic timeline chart.
    Suitable for portfolio,
    performance, execution,
    and history pages.
    """

    line_chart(

        dataframe,

        x=x,

        y=y,

        title=title,

        color=color,

        markers=True,

    )

# =============================================================================
# Financial Charts
# =============================================================================


def portfolio_allocation_chart(
    dataframe: pd.DataFrame,
    *,
    category: str,
    weight: str,
) -> None:
    """
    Portfolio allocation.
    """

    pie_chart(

        dataframe,

        names=category,

        values=weight,

        title="Portfolio Allocation",

    )


def sector_exposure_chart(
    dataframe: pd.DataFrame,
    *,
    sector: str,
    exposure: str,
) -> None:
    """
    Sector exposure.
    """

    horizontal_bar_chart(

        dataframe,

        x=exposure,

        y=sector,

        title="Sector Exposure",

        color=exposure,

        text=exposure,

    )


def holdings_distribution_chart(
    dataframe: pd.DataFrame,
    *,
    symbol: str,
    weight: str,
) -> None:
    """
    Holdings distribution.
    """

    bar_chart(

        dataframe,

        x=symbol,

        y=weight,

        title="Holdings Distribution",

        color=weight,

        text=weight,

    )


def performance_trend_chart(
    dataframe: pd.DataFrame,
    *,
    date: str,
    value: str,
) -> None:
    """
    Portfolio performance.
    """

    line_chart(

        dataframe,

        x=date,

        y=value,

        title="Performance Trend",

        markers=True,

    )


def drawdown_chart(
    dataframe: pd.DataFrame,
    *,
    date: str,
    drawdown: str,
) -> None:
    """
    Drawdown history.
    """

    area_chart(

        dataframe,

        x=date,

        y=drawdown,

        title="Drawdown",

    )


def risk_trend_chart(
    dataframe: pd.DataFrame,
    *,
    date: str,
    metric: str,
) -> None:
    """
    Historical risk.
    """

    line_chart(

        dataframe,

        x=date,

        y=metric,

        title="Risk Trend",

        markers=True,

    )


def execution_trend_chart(
    dataframe: pd.DataFrame,
    *,
    date: str,
    executions: str,
) -> None:
    """
    Execution history.
    """

    line_chart(

        dataframe,

        x=date,

        y=executions,

        title="Execution Trend",

        markers=True,

    )


def pnl_distribution_chart(
    dataframe: pd.DataFrame,
    *,
    pnl: str,
) -> None:
    """
    P&L distribution.
    """

    histogram_chart(

        dataframe,

        x=pnl,

        title="P&L Distribution",

    )


def risk_return_chart(
    dataframe: pd.DataFrame,
    *,
    risk: str,
    returns: str,
    symbol: str | None = None,
) -> None:
    """
    Risk vs return.
    """

    scatter_chart(

        dataframe,

        x=risk,

        y=returns,

        title="Risk vs Return",

        hover_name=symbol,

    )


# =============================================================================
# Dashboard Components
# =============================================================================


def chart_card(
    title: str,
    chart_function,
    *args,
    **kwargs,
) -> None:
    """
    Render a chart inside
    a dashboard container.
    """

    st.subheader(

        title,

    )

    chart_function(

        *args,

        **kwargs,

    )


def chart_section(
    title: str,
    caption: str | None = None,
) -> None:
    """
    Standard chart section.
    """

    st.subheader(

        title,

    )

    if caption:

        st.caption(

            caption,

        )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    "CONFIG",

    "COLORS",

    "empty_chart",

    "valid_dataframe",

    "column_exists",

    "apply_layout",

    "display_chart",

    "render_chart",

    "line_chart",

    "bar_chart",

    "horizontal_bar_chart",

    "scatter_chart",

    "histogram_chart",

    "pie_chart",

    "treemap_chart",

    "area_chart",

    "box_chart",

    "violin_chart",

    "bubble_chart",

    "timeline_chart",

    "portfolio_allocation_chart",

    "sector_exposure_chart",

    "holdings_distribution_chart",

    "performance_trend_chart",

    "drawdown_chart",

    "risk_trend_chart",

    "execution_trend_chart",

    "pnl_distribution_chart",

    "risk_return_chart",

    "chart_card",

    "chart_section",

]