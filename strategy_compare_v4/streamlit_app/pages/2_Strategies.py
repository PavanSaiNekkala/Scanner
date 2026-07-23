"""
Strategies Dashboard
====================

Institutional Strategy Analytics Dashboard
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from components.cards import strategy_summary_card
from components.charts import (
    bar_chart,
    dataframe,
    histogram,
    radar_chart,
)
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Strategy Analytics",
    page_icon="📈",
    layout="wide",
)

apply_theme()

# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "📈 Strategy Analytics"

PAGE_CAPTION = "Institutional comparison of all trading strategies."

SHEET_NAME = "Strategy Ranking"

DEFAULT_TOP_N = 10

# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render page header.
    """

    st.title(PAGE_TITLE)

    st.caption(PAGE_CAPTION)

    st.divider()


# ============================================================
# Validation
# ============================================================


def validate_session() -> None:
    """
    Validate whether reports have been loaded.
    """

    if not st.session_state.get(
        "reports_loaded",
        False,
    ):
        st.warning("Please load reports from the Data Load page.")

        st.stop()


# ============================================================
# Data Loading
# ============================================================


@st.cache_data(show_spinner=False)
def load_strategy_data(
    refresh_token=None,
) -> pd.DataFrame:
    """
    Load the Strategy Ranking worksheet.
    """

    return get_sheet(
        st.session_state.strategy_report,
        SHEET_NAME,
    )


def validate_strategy_data(
    df: pd.DataFrame,
) -> None:
    """
    Validate loaded strategy data.
    """

    if df is None or df.empty:
        st.error(f"'{SHEET_NAME}' worksheet was not found or is empty.")

        st.stop()


# ============================================================
# Summary
# ============================================================


def render_summary(
    df: pd.DataFrame,
) -> None:
    """
    Render strategy summary metrics.
    """

    strategy_summary_card(df)

    st.divider()


def render_top_strategy(
    df: pd.DataFrame,
) -> None:
    """
    Display best performing strategy.
    """

    if df.empty:
        return

    if "Adjusted Strategy Score" not in df.columns:
        return

    best = df.sort_values(
        "Adjusted Strategy Score",
        ascending=False,
    ).iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Best Strategy",
            best["Strategy"],
        )

    with c2:
        st.metric(
            "Adjusted Strategy Score",
            round(
                best["Adjusted Strategy Score"],
                2,
            ),
        )

    with c3:
        st.metric(
            "Weighted Expectancy",
            round(
                best["Weighted Expectancy"],
                4,
            ),
        )


# ============================================================
# Filters
# ============================================================


def render_filters(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Render dashboard filters and return the filtered dataset.
    """

    st.subheader("Filters")

    left, right = st.columns([1, 3])

    # --------------------------------------------------------
    # Top N
    # --------------------------------------------------------

    with left:
        top_n = st.slider(
            "Top Strategies",
            min_value=1,
            max_value=len(df),
            value=min(
                DEFAULT_TOP_N,
                len(df),
            ),
            help="Display the highest ranked strategies.",
        )

    # --------------------------------------------------------
    # Search Strategy
    # --------------------------------------------------------

    with right:
        available_strategies = sorted(df["Strategy"].dropna().unique().tolist())

        selected_strategies = st.multiselect(
            "Select Strategies",
            options=available_strategies,
            default=available_strategies,
        )

    # --------------------------------------------------------
    # Filtering
    # --------------------------------------------------------

    filtered = df.copy()

    if selected_strategies:
        filtered = filtered[filtered["Strategy"].isin(selected_strategies)]

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    if "Adjusted Strategy Score" in filtered.columns:
        filtered = (
            filtered.sort_values(
                "Adjusted Strategy Score",
                ascending=False,
            )
            .head(top_n)
            .reset_index(
                drop=True,
            )
        )

    st.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** strategies.")

    st.divider()

    return filtered


# ============================================================
# Strategy Ranking
# ============================================================


def render_strategy_table(
    df: pd.DataFrame,
) -> None:
    """
    Render the filtered strategy ranking table.
    """

    st.subheader(
        "Institutional Strategy Ranking"
    )


    display_columns = [
        "Strategy",
        "Adjusted Strategy Score",
        "Weighted Expectancy",
        "Weighted Profit Factor",
        "Weighted Reward Risk",
        "Total Trades",
        "Positive Weighted Expectancy %",
        "Strategy Rank",
    ]


    available_columns = [
        column
        for column in display_columns
        if column in df.columns
    ]


    dataframe(
        df[available_columns],
    )

    st.divider()


# ============================================================
# Charts
# ============================================================


def render_charts(
    df: pd.DataFrame,
) -> None:
    """
    Render strategy analytics charts.
    """

    if df.empty:
        return

    st.subheader("Strategy Analytics")

    # --------------------------------------------------------
    # Bar Charts
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:
        if "Strategy Rank" in df.columns and "Weighted Expectancy" in df.columns:
            bar_chart(
                df,
                x="Strategy Rank",
                y="Weighted Expectancy",
                title="Adjusted Strategy Score",
            )

    with right:
        if "Strategy Rank" in df.columns and "Weighted Expectancy" in df.columns:
            bar_chart(
                df,
                x="Strategy Rank",
                y="Weighted Expectancy",
                title="Weighted Expectancy",
            )

    # --------------------------------------------------------
    # Histograms
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:
        if "Adjusted Strategy Score" in df.columns:
            histogram(
                df,
                "Adjusted Strategy Score",
                "Adjusted Strategy Score Distribution",
            )

    with right:
        if "Weighted Profit Factor" in df.columns:
            histogram(
                df,
                "Weighted Profit Factor",
                "Weighted Profit Factor Distribution",
            )

    st.divider()


# ============================================================
# Strategy Radar
# ============================================================


def render_strategy_radar(
    df: pd.DataFrame,
) -> None:
    """
    Render radar chart for a selected strategy.
    """

    if df.empty:
        return

    required_columns = [
        "Strategy Rank",
        "Adjusted Strategy Score",
        "Weighted Expectancy",
        "Weighted Profit Factor",
        "Weighted Reward Risk",
        "Total Trades",
    ]

    if not all(column in df.columns for column in required_columns):
        return

    st.subheader("Strategy Radar")

    strategy_options = (
        df[
            [
                "Strategy Rank",
                "Strategy",
            ]
        ]
        .sort_values(
            "Strategy Rank"
        )
    )


    selected_rank = st.selectbox(
        "Select Strategy Rank",
        options=strategy_options["Strategy Rank"].tolist(),
        key="radar_strategy",
    )


    selected_strategy = (
        strategy_options
        .loc[
            strategy_options["Strategy Rank"]
            ==
            selected_rank,
            "Strategy",
        ]
        .iloc[0]
    )


    strategy_df = df.loc[
        df["Strategy"].astype(str).str.strip()
        ==
        str(selected_strategy).strip()
    ]

    if strategy_df.empty:
        st.warning(
            f"No strategy data found for {selected_strategy}"
        )
        return


    strategy = strategy_df.iloc[0]


    radar_values = {
        "Adjusted Strategy": strategy["Adjusted Strategy Score"],

        "Weighted Expectancy": (
            strategy["Weighted Expectancy"] * 100
        ),

        "Profit Factor": (
            strategy["Weighted Profit Factor"] * 50
        ),

        "Reward Risk": (
            strategy["Weighted Reward Risk"] * 50
        ),

        "Trade Reliability": min(
            strategy["Total Trades"] / 100,
            100,
        ),
    }


    radar_chart(
        radar_values,
        str(selected_strategy),
    )

    st.divider()


# ============================================================
# Strategy Details
# ============================================================


def render_strategy_details(
    df: pd.DataFrame,
) -> None:
    """
    Display detailed information for a selected strategy.
    """

    if df.empty:
        return

    if "Strategy Rank" not in df.columns:
        return

    st.subheader("Strategy Details")

    df["Strategy"] = (
        df["Strategy"]
        .astype(str)
        .str.strip()
    )

    selected_strategy = st.selectbox(
        "Select Strategy",
        options=df["Strategy"].tolist(),
        key="strategy_details",
    )

    strategy = df.loc[df["Strategy"] == selected_strategy]

    st.dataframe(
        strategy,
        use_container_width=True,
        hide_index=True,
        height=200,
    )

    st.divider()


# ============================================================
# Downloads
# ============================================================


def render_downloads(
    df: pd.DataFrame,
) -> None:
    """
    Render download section.
    """

    if df.empty:
        return

    st.subheader("Export")

    csv = df.to_csv(
        index=False,
    )

    st.download_button(
        label="📥 Download Strategy Ranking (CSV)",
        data=csv,
        file_name="strategy_ranking.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Empty State
# ============================================================


def render_empty_state() -> None:
    """
    Render empty state when no strategy data is available.
    """

    st.info("""
### 📈 Strategy Analytics

This dashboard provides institutional analysis of all
generated trading strategies.

Features included:

- Strategy Rankings
- KPI Summary
- Adjusted Strategy Score Analysis
- Weighted Expectancy Analysis
- Profit Factor Distribution
- Radar Comparison
- Strategy Details
- CSV Export

Load reports from the **Data Load** page to begin.
""")


# ============================================================
# Footer
# ============================================================


def render_footer() -> None:
    """
    Render page footer.
    """

    st.divider()

    left, right = st.columns([3, 1])

    with left:
        st.caption("Institutional Strategy Comparison Platform")

    with right:
        st.caption("Version 4.0")


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Render Strategy Analytics dashboard.
    """

    render_header()

    validate_session()

    refresh_token = Path(
        st.session_state.output_folder
    ).stat().st_mtime


    strategy_df = load_strategy_data(
        refresh_token,
    )

    validate_strategy_data(
        strategy_df,
    )

    if strategy_df.empty:
        render_empty_state()

        return

    render_summary(
        strategy_df,
    )

    render_top_strategy(
        strategy_df,
    )

    filtered_df = render_filters(
        strategy_df,
    )

    render_strategy_table(
        filtered_df,
    )

    render_charts(
        filtered_df,
    )

    render_strategy_radar(
        filtered_df,
    )

    render_strategy_details(
        filtered_df,
    )

    render_downloads(
        filtered_df,
    )

    render_footer()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
