"""
Metric Cards
============

Reusable KPI cards for the Institutional Strategy Comparison Platform.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

# ============================================================
# Constants
# ============================================================

RECOMMENDATION_ICONS = {
    "STRONG BUY": "🟢",
    "BUY": "🔵",
    "WATCH": "🟡",
    "IMPROVE": "🟠",
    "AVOID": "🔴",
    "REJECT": "⚫",
}

DEFAULT_ICON = "⚪"

DEFAULT_DECIMALS = 2

# ============================================================
# Helper Functions
# ============================================================


def format_metric(
    value,
    decimals: int = DEFAULT_DECIMALS,
):
    """
    Format numeric values.
    """

    if isinstance(value, (int, float)):
        return round(
            value,
            decimals,
        )

    return value


def summary_metric(
    title: str,
    value,
) -> None:
    """
    Render a formatted KPI metric.
    """

    metric_card(
        title,
        format_metric(value),
    )


# ============================================================
# Generic Metric Card
# ============================================================


def metric_card(
    title: str,
    value,
    delta: str | None = None,
    help_text: str | None = None,
) -> None:
    """
    Display a standard KPI metric.
    """

    st.metric(
        label=title,
        value=format_metric(value),
        delta=delta,
        help=help_text,
    )


# ============================================================
# Recommendation Badge
# ============================================================


def recommendation_badge(
    recommendation: str,
) -> None:
    """
    Display recommendation badge.
    """

    recommendation = str(
        recommendation,
    ).upper()

    icon = RECOMMENDATION_ICONS.get(
        recommendation,
        DEFAULT_ICON,
    )

    st.markdown(f"### {icon} {recommendation}")


# ============================================================
# Strategy Summary Card
# ============================================================


def strategy_summary_card(
    df: pd.DataFrame | None,
) -> None:
    """
    Display summary cards for strategy or stock datasets.
    """

    if df is None or df.empty:
        st.info("No data loaded.")
        return

    c1, c2, c3, c4 = st.columns(4)

    # --------------------------------------------------------
    # Strategy Dataset
    # --------------------------------------------------------

    if "Strategy" in df.columns or "Strategy Rank" in df.columns:
        with c1:
            strategies = (
                df["Strategy"].nunique() if "Strategy" in df.columns else len(df)
            )

            metric_card(
                "Strategies",
                strategies,
            )

        with c2:
            if "Stock" in df.columns:
                metric_card(
                    "Stocks",
                    df["Stock"].nunique(),
                )

            else:
                metric_card(
                    "Records",
                    len(df),
                )

        with c3:
            if "Composite Score" in df.columns:
                summary_metric(
                    "Avg Composite",
                    df["Composite Score"].mean(),
                )

        with c4:
            if "Edge Score" in df.columns:
                summary_metric(
                    "Avg Edge",
                    df["Edge Score"].mean(),
                )

            elif "Profit Factor" in df.columns:
                summary_metric(
                    "Avg Profit Factor",
                    df["Profit Factor"].mean(),
                )

        return

    # --------------------------------------------------------
    # Stock Dataset
    # --------------------------------------------------------

    if "Stock" in df.columns:
        with c1:
            metric_card(
                "Stocks",
                df["Stock"].nunique(),
            )

        with c2:
            if "Strategies" in df.columns:
                metric_card(
                    "Strategies",
                    df["Strategies"].nunique(),
                )

        with c3:
            if "Institutional Score" in df.columns:
                summary_metric(
                    "Avg Score",
                    df["Institutional Score"].mean(),
                )

        with c4:
            if "Recommendation" in df.columns:
                metric_card(
                    "Recommendations",
                    df["Recommendation"].nunique(),
                )


# ============================================================
# Portfolio Summary Card
# ============================================================


def portfolio_summary_card(
    df: pd.DataFrame | None,
) -> None:
    """
    Display portfolio summary.
    """

    if df is None or df.empty:
        st.info("Portfolio not available.")

        return

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Holdings",
            len(df),
        )

    with c2:
        if "Weight %" in df.columns:
            metric_card(
                "Total Weight",
                f"{df['Weight %'].sum():.2f} %",
            )

    with c3:
        if "Expected Return %" in df.columns:
            metric_card(
                "Expected Return",
                f"{df['Expected Return %'].mean():.2f} %",
            )


# ============================================================
# Robustness Summary Card
# ============================================================


def robustness_card(
    df: pd.DataFrame | None,
) -> None:
    """
    Display robustness summary.
    """

    if df is None or df.empty:
        st.info("No robustness analysis.")

        return

    numeric = df.select_dtypes(
        include="number",
    )

    if numeric.empty:
        return

    columns = st.columns(
        min(
            4,
            len(numeric.columns),
        )
    )

    for container, column in zip(
        columns,
        numeric.columns[:4],
        strict=False,
    ):
        with container:
            summary_metric(
                column,
                numeric[column].mean(),
            )


# ============================================================
# Recommendation Distribution
# ============================================================


def recommendation_distribution(
    df: pd.DataFrame | None,
) -> None:
    """
    Display recommendation counts.
    """

    if df is None or df.empty or "Recommendation" not in df.columns:
        st.info("Recommendation data unavailable.")

        return

    counts = (
        df["Recommendation"]
        .value_counts()
        .rename_axis("Recommendation")
        .reset_index(name="Count")
    )

    st.dataframe(
        counts,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "metric_card",
    "recommendation_badge",
    "strategy_summary_card",
    "portfolio_summary_card",
    "robustness_card",
    "recommendation_distribution",
]
