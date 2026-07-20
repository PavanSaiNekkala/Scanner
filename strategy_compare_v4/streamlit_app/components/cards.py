"""
Metric Cards
============

Reusable KPI cards for the Institutional Strategy Comparison Platform.
"""

import streamlit as st

# ---------------------------------------------------------
# Generic Metric Card
# ---------------------------------------------------------


def metric_card(
    title: str,
    value,
    delta: str | None = None,
    help_text: str | None = None,
):
    """
    Display a standard metric card.
    """

    st.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text,
    )


# ---------------------------------------------------------
# Colored Status Badge
# ---------------------------------------------------------


def recommendation_badge(recommendation: str):
    """
    Display recommendation badge.
    """

    recommendation = str(recommendation).upper()

    colors = {
        "STRONG BUY": "🟢",
        "BUY": "🔵",
        "WATCH": "🟡",
        "IMPROVE": "🟠",
        "AVOID": "🔴",
        "REJECT": "⚫",
    }

    icon = colors.get(recommendation, "⚪")

    st.markdown(f"### {icon} {recommendation}")


# ---------------------------------------------------------
# Strategy Summary Card
# ---------------------------------------------------------


def strategy_summary_card(df):
    """
    Show summary of strategy dataframe.
    """

    if df is None or df.empty:
        st.info("No strategy data loaded.")

        return

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Strategies",
            df["Strategy"].nunique(),
        )

    with c2:
        metric_card(
            "Stocks",
            df["Stock"].nunique(),
        )

    with c3:
        metric_card(
            "Average Composite",
            round(df["Composite Score"].mean(), 2),
        )

    with c4:
        metric_card(
            "Average Edge",
            round(df["Edge Score"].mean(), 2),
        )


# ---------------------------------------------------------
# Portfolio Summary Card
# ---------------------------------------------------------


def portfolio_summary_card(df):
    """
    Portfolio statistics.
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


# ---------------------------------------------------------
# Robustness Summary Card
# ---------------------------------------------------------


def robustness_card(df):
    """
    Robustness statistics.
    """

    if df is None or df.empty:
        st.info("No robustness analysis.")

        return

    numeric = df.select_dtypes("number")

    if numeric.empty:
        return

    cols = st.columns(min(4, len(numeric.columns)))

    for column, container in zip(numeric.columns[:4], cols, strict=False):
        with container:
            metric_card(
                column,
                round(numeric[column].mean(), 2),
            )


# ---------------------------------------------------------
# Recommendation Distribution
# ---------------------------------------------------------


def recommendation_distribution(df):
    """
    Show recommendation counts.
    """

    if df is None or df.empty or "Recommendation" not in df.columns:
        st.info("Recommendation data unavailable.")

        return

    counts = df["Recommendation"].value_counts().reset_index()

    counts.columns = [
        "Recommendation",
        "Count",
    ]

    st.dataframe(
        counts,
        use_container_width=True,
        hide_index=True,
    )
