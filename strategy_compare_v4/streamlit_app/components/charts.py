"""
Interactive Charts
==================

Reusable Plotly charts for the
Institutional Strategy Comparison Platform.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Generic Bar Chart
# ---------------------------------------------------------


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
):
    """Interactive bar chart."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        text=y,
        title=title,
    )

    fig.update_layout(
        height=500,
        template="plotly_white",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Top N Bar Chart
# ---------------------------------------------------------


def top_n_bar(
    df: pd.DataFrame,
    column: str,
    score: str,
    n: int = 10,
    title: str = "",
):
    """Top N ranking."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    top = df.sort_values(score, ascending=False).head(n)

    fig = px.bar(
        top,
        x=column,
        y=score,
        text=score,
        color=score,
        title=title,
    )

    fig.update_layout(height=500)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Pie Chart
# ---------------------------------------------------------


def pie_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
):
    """Pie chart."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    fig = px.pie(
        df,
        names=names,
        values=values,
        hole=0.45,
        title=title,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Scatter Plot
# ---------------------------------------------------------


def scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    size: str | None = None,
    hover: str | None = None,
    title: str = "",
):
    """Scatter plot."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        hover_name=hover,
        title=title,
    )

    fig.update_layout(height=550)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Histogram
# ---------------------------------------------------------


def histogram(
    df: pd.DataFrame,
    column: str,
    title: str,
):
    """Histogram."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    fig = px.histogram(
        df,
        x=column,
        nbins=30,
        title=title,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Box Plot
# ---------------------------------------------------------


def box_plot(
    df: pd.DataFrame,
    column: str,
    title: str,
):
    """Box plot."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    fig = px.box(
        df,
        y=column,
        title=title,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Correlation Heatmap
# ---------------------------------------------------------


def correlation_heatmap(
    corr: pd.DataFrame,
    title: str = "Correlation Matrix",
):
    """Heatmap."""

    if corr is None or corr.empty:
        st.info("No correlation data.")
        return

    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdBu",
            zmid=0,
            text=corr.round(2),
            texttemplate="%{text}",
        )
    )

    fig.update_layout(
        title=title,
        height=700,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Radar Chart
# ---------------------------------------------------------


def radar_chart(
    values: dict,
    title: str,
):
    """Radar chart."""

    categories = list(values.keys())
    scores = list(values.values())

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=title,
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title=title,
        height=600,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Recommendation Distribution
# ---------------------------------------------------------


def recommendation_chart(
    df: pd.DataFrame,
):
    """Recommendation distribution."""

    if df is None or df.empty or "Recommendation" not in df.columns:
        st.info("Recommendation data unavailable.")
        return

    summary = df["Recommendation"].value_counts().reset_index()

    summary.columns = [
        "Recommendation",
        "Count",
    ]

    fig = px.bar(
        summary,
        x="Recommendation",
        y="Count",
        color="Recommendation",
        text="Count",
        title="Recommendation Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Data Preview
# ---------------------------------------------------------


def dataframe(
    df: pd.DataFrame,
):
    """Display dataframe."""

    if df is None or df.empty:
        st.info("No data available.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
