"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
reports/charts.py

Purpose
-------
Institutional chart generation for reports,
dashboard visualization, and analytics.

Features
--------
• Composite Score Charts
• Edge Score Charts
• Recommendation Distribution
• Scatter Charts
• Histograms
• Correlation Heatmap
• Portfolio Allocation

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    EDGE_SCORE,
    EXPECTANCY,
    PROFIT_FACTOR,
    RELIABILITY_SCORE,
    EFFICIENCY_SCORE,
    RECOMMENDATION,
    WEIGHT,
)

from strategy_compare_v4.utils.helpers import (
    require_columns,
)

from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)

logger = get_logger(__name__)


# ============================================================
# Save Chart
# ============================================================

def save_chart(
    figure,
    output_path: str | Path,
    dpi: int = 300,
):
    """
    Save chart to disk.
    """

    banner(

        logger,

        "Saving Chart",

    )

    output_path = Path(

        output_path,

    )

    output_path.parent.mkdir(

        parents=True,

        exist_ok=True,

    )

    figure.savefig(

        output_path,

        dpi=dpi,

        bbox_inches="tight",

    )

    plt.close(

        figure,

    )

    logger.info(

        "Chart saved : %s",

        output_path,

    )


# ============================================================
# Composite Score Chart
# ============================================================

def composite_score_chart(
    df: pd.DataFrame,
    top_n: int = 20,
):
    """
    Top Composite Score chart.
    """

    require_columns(

        df,

        [

            "Stock",

            COMPOSITE_SCORE,

        ],

    )

    logger.info(

        "Generating Composite Score chart."

    )

    data = (

        df

        .nlargest(

            top_n,

            COMPOSITE_SCORE,

        )

    )

    fig, ax = plt.subplots(

        figsize=(12, 6),

    )

    ax.bar(

        data["Stock"],

        data[

            COMPOSITE_SCORE

        ],

    )

    ax.set_title(

        "Top Composite Scores",

    )

    ax.set_ylabel(

        COMPOSITE_SCORE,

    )

    ax.tick_params(

        axis="x",

        rotation=90,

    )

    fig.tight_layout()

    return fig


# ============================================================
# Edge Score Chart
# ============================================================

def edge_score_chart(
    df: pd.DataFrame,
    top_n: int = 20,
):
    """
    Top Edge Score chart.
    """

    require_columns(

        df,

        [

            "Stock",

            EDGE_SCORE,

        ],

    )

    logger.info(

        "Generating Edge Score chart."

    )

    data = (

        df

        .nlargest(

            top_n,

            EDGE_SCORE,

        )

    )

    fig, ax = plt.subplots(

        figsize=(12, 6),

    )

    ax.bar(

        data["Stock"],

        data[

            EDGE_SCORE

        ],

    )

    ax.set_title(

        "Top Edge Scores",

    )

    ax.set_ylabel(

        EDGE_SCORE,

    )

    ax.tick_params(

        axis="x",

        rotation=90,

    )

    fig.tight_layout()

    return fig

# ============================================================
# Recommendation Distribution
# ============================================================

def recommendation_chart(
    df: pd.DataFrame,
):
    """
    Recommendation
    distribution chart.
    """

    require_columns(

        df,

        [

            RECOMMENDATION,

        ],

    )

    logger.info(

        "Generating Recommendation Distribution chart."

    )

    counts = (

        df[

            RECOMMENDATION

        ]

        .value_counts()

    )

    fig, ax = plt.subplots(

        figsize=(8, 8),

    )

    ax.pie(

        counts,

        labels=counts.index,

        autopct="%1.1f%%",

    )

    ax.set_title(

        "Recommendation Distribution",

    )

    fig.tight_layout()

    return fig


# ============================================================
# Profit Factor vs Expectancy
# ============================================================

def expectancy_profit_chart(
    df: pd.DataFrame,
):
    """
    Scatter chart of
    Profit Factor vs
    Expectancy.
    """

    require_columns(

        df,

        [

            PROFIT_FACTOR,

            EXPECTANCY,

        ],

    )

    logger.info(

        "Generating Profit Factor vs Expectancy chart."

    )

    fig, ax = plt.subplots(

        figsize=(10, 6),

    )

    ax.scatter(

        df[

            PROFIT_FACTOR

        ],

        df[

            EXPECTANCY

        ],

    )

    ax.set_xlabel(

        PROFIT_FACTOR,

    )

    ax.set_ylabel(

        EXPECTANCY,

    )

    ax.set_title(

        "Profit Factor vs Expectancy",

    )

    fig.tight_layout()

    return fig


# ============================================================
# Reliability vs Efficiency
# ============================================================

def reliability_efficiency_chart(
    df: pd.DataFrame,
):
    """
    Scatter chart of
    Reliability Score
    versus Efficiency Score.
    """

    require_columns(

        df,

        [

            RELIABILITY_SCORE,

            EFFICIENCY_SCORE,

        ],

    )

    logger.info(

        "Generating Reliability vs Efficiency chart."

    )

    fig, ax = plt.subplots(

        figsize=(10, 6),

    )

    ax.scatter(

        df[

            RELIABILITY_SCORE

        ],

        df[

            EFFICIENCY_SCORE

        ],

    )

    ax.set_xlabel(

        RELIABILITY_SCORE,

    )

    ax.set_ylabel(

        EFFICIENCY_SCORE,

    )

    ax.set_title(

        "Reliability vs Efficiency",

    )

    fig.tight_layout()

    return fig


# ============================================================
# Score Histogram
# ============================================================

def score_histogram(
    df: pd.DataFrame,
    column: str,
):
    """
    Histogram for a
    selected numeric
    metric.
    """

    require_columns(

        df,

        [

            column,

        ],

    )

    logger.info(

        "Generating histogram for '%s'.",

        column,

    )

    fig, ax = plt.subplots(

        figsize=(10, 6),

    )

    ax.hist(

        df[

            column

        ],

        bins=20,

    )

    ax.set_title(

        column,

    )

    ax.set_xlabel(

        column,

    )

    ax.set_ylabel(

        "Frequency",

    )

    fig.tight_layout()

    return fig

# ============================================================
# Correlation Heatmap
# ============================================================

def correlation_heatmap(
    correlation_df: pd.DataFrame,
):
    """
    Generate a correlation
    heatmap.
    """

    logger.info(

        "Generating Correlation Heatmap."

    )

    fig, ax = plt.subplots(

        figsize=(10, 8),

    )

    image = ax.imshow(

        correlation_df,

        aspect="auto",

    )

    ax.set_xticks(

        range(

            len(

                correlation_df.columns,

            )

        )

    )

    ax.set_xticklabels(

        correlation_df.columns,

        rotation=90,

    )

    ax.set_yticks(

        range(

            len(

                correlation_df.index,

            )

        )

    )

    ax.set_yticklabels(

        correlation_df.index,

    )

    fig.colorbar(

        image,

    )

    fig.tight_layout()

    return fig


# ============================================================
# Portfolio Allocation Chart
# ============================================================

def portfolio_chart(
    portfolio_df: pd.DataFrame,
):
    """
    Generate portfolio
    allocation chart.
    """

    require_columns(

        portfolio_df,

        [

            "Stock",

            WEIGHT,

        ],

    )

    logger.info(

        "Generating Portfolio Allocation chart."

    )

    fig, ax = plt.subplots(

        figsize=(10, 8),

    )

    ax.pie(

        portfolio_df[

            WEIGHT

        ],

        labels=portfolio_df[

            "Stock"

        ],

        autopct="%1.1f%%",

    )

    ax.set_title(

        "Portfolio Allocation",

    )

    fig.tight_layout()

    return fig


# ============================================================
# Export All Charts
# ============================================================

def export_all_charts(
    comparison_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
    correlation_df: pd.DataFrame,
    output_directory: str | Path,
):
    """
    Export all institutional
    charts to disk.
    """

    banner(

        logger,

        "Exporting Charts",

    )

    output_directory = Path(

        output_directory,

    )

    output_directory.mkdir(

        parents=True,

        exist_ok=True,

    )

    charts = {

        "composite_scores.png":

            composite_score_chart(

                comparison_df,

            ),

        "edge_scores.png":

            edge_score_chart(

                comparison_df,

            ),

        "recommendations.png":

            recommendation_chart(

                comparison_df,

            ),

        "expectancy_profit.png":

            expectancy_profit_chart(

                comparison_df,

            ),

        "reliability_efficiency.png":

            reliability_efficiency_chart(

                comparison_df,

            ),

        "correlation_heatmap.png":

            correlation_heatmap(

                correlation_df,

            ),

        "portfolio.png":

            portfolio_chart(

                portfolio_df,

            ),

    }

    for filename, figure in charts.items():

        save_chart(

            figure,

            output_directory

            / filename,

        )

        logger.info(

            "Exported : %s",

            filename,

        )

    logger.info(

        "Total Charts Exported : %d",

        len(

            charts,

        ),

    )

    logger.info(

        "Output Directory : %s",

        output_directory,

    )