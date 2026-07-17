"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    reports/charts.py

Purpose:
    Chart generation for reports and dashboard.

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


###############################################################################
# Common Save
###############################################################################

def save_chart(

    figure,

    output_path,

    dpi=300

):
    """
    Save chart to disk.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(

        parents=True,

        exist_ok=True

    )

    figure.savefig(

        output_path,

        dpi=dpi,

        bbox_inches="tight"

    )

    plt.close(figure)


###############################################################################
# Top Composite Scores
###############################################################################

def composite_score_chart(

    df,

    top_n=20

):
    """
    Composite Score bar chart.
    """

    data = (

        df

        .nlargest(

            top_n,

            "Composite Score"

        )

    )

    fig, ax = plt.subplots(

        figsize=(12,6)

    )

    ax.bar(

        data["Stock"],

        data["Composite Score"]

    )

    ax.set_title(

        "Top Composite Scores"

    )

    ax.set_ylabel(

        "Composite Score"

    )

    ax.tick_params(

        axis="x",

        rotation=90

    )

    fig.tight_layout()

    return fig


###############################################################################
# Edge Score
###############################################################################

def edge_score_chart(

    df,

    top_n=20

):

    data = (

        df

        .nlargest(

            top_n,

            "Edge Score"

        )

    )

    fig, ax = plt.subplots(

        figsize=(12,6)

    )

    ax.bar(

        data["Stock"],

        data["Edge Score"]

    )

    ax.set_title(

        "Top Edge Scores"

    )

    ax.tick_params(

        axis="x",

        rotation=90

    )

    fig.tight_layout()

    return fig


###############################################################################
# Recommendation Distribution
###############################################################################

def recommendation_chart(

    df

):

    counts = (

        df["Recommendation"]

        .value_counts()

    )

    fig, ax = plt.subplots(

        figsize=(8,8)

    )

    ax.pie(

        counts,

        labels=counts.index,

        autopct="%1.1f%%"

    )

    ax.set_title(

        "Recommendation Distribution"

    )

    return fig


###############################################################################
# Profit Factor vs Expectancy
###############################################################################

def expectancy_profit_chart(

    df

):

    fig, ax = plt.subplots(

        figsize=(10,6)

    )

    ax.scatter(

        df["Profit Factor"],

        df["Expectancy"]

    )

    ax.set_xlabel(

        "Profit Factor"

    )

    ax.set_ylabel(

        "Expectancy"

    )

    ax.set_title(

        "Profit Factor vs Expectancy"

    )

    fig.tight_layout()

    return fig


###############################################################################
# Reliability vs Efficiency
###############################################################################

def reliability_efficiency_chart(

    df

):

    fig, ax = plt.subplots(

        figsize=(10,6)

    )

    ax.scatter(

        df["Reliability Score"],

        df["Efficiency Score"]

    )

    ax.set_xlabel(

        "Reliability Score"

    )

    ax.set_ylabel(

        "Efficiency Score"

    )

    ax.set_title(

        "Reliability vs Efficiency"

    )

    fig.tight_layout()

    return fig


###############################################################################
# Score Histogram
###############################################################################

def score_histogram(

    df,

    column

):

    fig, ax = plt.subplots(

        figsize=(10,6)

    )

    ax.hist(

        df[column],

        bins=20

    )

    ax.set_title(

        column

    )

    fig.tight_layout()

    return fig


###############################################################################
# Correlation Heatmap
###############################################################################

def correlation_heatmap(

    correlation_df

):

    fig, ax = plt.subplots(

        figsize=(10,8)

    )

    image = ax.imshow(

        correlation_df,

        aspect="auto"

    )

    ax.set_xticks(

        range(

            len(correlation_df.columns)

        )

    )

    ax.set_xticklabels(

        correlation_df.columns,

        rotation=90

    )

    ax.set_yticks(

        range(

            len(correlation_df.index)

        )

    )

    ax.set_yticklabels(

        correlation_df.index

    )

    fig.colorbar(

        image

    )

    fig.tight_layout()

    return fig


###############################################################################
# Portfolio Allocation
###############################################################################

def portfolio_chart(

    portfolio_df

):

    fig, ax = plt.subplots(

        figsize=(10,8)

    )

    ax.pie(

        portfolio_df["Weight"],

        labels=portfolio_df["Stock"],

        autopct="%1.1f%%"

    )

    ax.set_title(

        "Portfolio Allocation"

    )

    return fig


###############################################################################
# Export All Charts
###############################################################################

def export_all_charts(

    comparison_df,

    portfolio_df,

    correlation_df,

    output_directory

):

    output_directory = Path(output_directory)

    output_directory.mkdir(

        parents=True,

        exist_ok=True

    )

    save_chart(

        composite_score_chart(comparison_df),

        output_directory / "composite_scores.png"

    )

    save_chart(

        edge_score_chart(comparison_df),

        output_directory / "edge_scores.png"

    )

    save_chart(

        recommendation_chart(comparison_df),

        output_directory / "recommendations.png"

    )

    save_chart(

        expectancy_profit_chart(comparison_df),

        output_directory / "expectancy_profit.png"

    )

    save_chart(

        reliability_efficiency_chart(comparison_df),

        output_directory / "reliability_efficiency.png"

    )

    save_chart(

        correlation_heatmap(correlation_df),

        output_directory / "correlation_heatmap.png"

    )

    save_chart(

        portfolio_chart(portfolio_df),

        output_directory / "portfolio.png"

    )