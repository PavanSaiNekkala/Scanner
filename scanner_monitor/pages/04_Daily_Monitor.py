"""
04_Daily_Monitor.py
===================

Institutional Scanner Monitor

Daily monitoring dashboard providing
real-time visibility into scanner activity,
signal generation, market health,
data freshness, and operational status.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from core.config import (DATA_DIR, LATEST_REPORTS_DIR)
from core.theme import apply_theme
from ui.cards import summary_row
from ui.components import (
    divider,
    section,
)
from ui.sidebar import render_sidebar

from ui.metrics import dataframe_info

from ui.loader import load_first_available_csv

from ui.tables import (
    download_buttons,
    holdings_table,
)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True)
class DailyMonitorConfig:
    """
    Dashboard configuration.
    """

    title: str = "Daily Monitor"

    icon: str = "📈"

    layout: str = "wide"

    scanner_file: str = "scanner_monitor.csv"

    portfolio_file: str = "portfolio.csv"

    holdings_file: str = "holdings.csv"

    signal_file: str = "signals.csv"

    refresh_seconds: int = 60


CONFIG = DailyMonitorConfig()

# =============================================================================
# Streamlit
# =============================================================================

st.set_page_config(

    page_title=CONFIG.title,

    page_icon=CONFIG.icon,

    layout=CONFIG.layout,

)

apply_theme()

render_sidebar()

# =============================================================================
# Session State
# =============================================================================

st.session_state.setdefault(

    "daily_monitor_loaded",

    False,

)

st.session_state.setdefault(

    "last_refresh",

    None,

)

st.session_state.setdefault(

    "selected_sector",

    "All",

)

st.session_state.setdefault(

    "selected_signal",

    "All",

)



scanner_df = load_first_available_csv(
    LATEST_REPORTS_DIR / CONFIG.scanner_file,
    DATA_DIR / CONFIG.scanner_file,
)

portfolio_df = load_first_available_csv(
    LATEST_REPORTS_DIR / CONFIG.portfolio_file,
    DATA_DIR / CONFIG.portfolio_file,
)

holdings_df = load_first_available_csv(
    LATEST_REPORTS_DIR / CONFIG.holdings_file,
    DATA_DIR / CONFIG.holdings_file,
)

signals_df = load_first_available_csv(
    LATEST_REPORTS_DIR / CONFIG.signal_file,
    DATA_DIR / CONFIG.signal_file,
)

# =============================================================================
# Validation
# =============================================================================

datasets = {

    "Scanner": scanner_df,

    "Portfolio": portfolio_df,

    "Holdings": holdings_df,

    "Signals": signals_df,

}

missing = [

    name

    for name, df in datasets.items()

    if df.empty

]

if len(missing) == len(datasets):

    st.error(

        "No monitoring datasets were found."

    )

    st.stop()

# =============================================================================
# Dashboard Header
# =============================================================================

section(

    "Daily Monitor",

    (
        "Operational dashboard for "
        "today's scanner activity, "
        "signals, portfolio monitoring, "
        "and market health."
    ),

)

left, right = st.columns(

    [3, 1],

)

with left:

    st.caption(

        f"Last Refresh: {datetime.now():%d %b %Y %H:%M:%S}"

    )

with right:

    st.button(

        "Refresh",

        use_container_width=True,

    )

# =============================================================================
# Today's KPIs
# =============================================================================

section(

    "Today's Activity",

    (
        "Real-time scanner statistics "
        "and operational overview."
    ),

)


def first_existing(

    df: pd.DataFrame,

    *columns: str,

) -> str | None:
    """
    Return the first existing column.
    """

    for column in columns:

        if column in df.columns:

            return column

    return None


def numeric_series(

    df: pd.DataFrame,

    column: str | None,

) -> pd.Series:
    """
    Safely convert a column to numeric.
    """

    if (

        column is None

        or column not in df.columns

    ):

        return pd.Series(

            dtype=float,

        )

    return pd.to_numeric(

        df[column],

        errors="coerce",

    ).fillna(

        0.0,

    )


# =============================================================================
# Column Detection
# =============================================================================

signal_col = first_existing(

    signals_df,

    "Signal",

    "Recommendation",

    "Action",

)

score_col = first_existing(

    signals_df,

    "Score",

    "Composite Score",

    "Final Score",

)

sector_col = first_existing(

    signals_df,

    "Sector",

)

symbol_col = first_existing(

    signals_df,

    "Symbol",

    "Ticker",

)

price_col = first_existing(

    signals_df,

    "Price",

    "CMP",

    "Current Price",

)

target_col = first_existing(

    signals_df,

    "Target",

    "Target Price",

)

# =============================================================================
# Numeric Series
# =============================================================================

scores = numeric_series(

    signals_df,

    score_col,

)

# =============================================================================
# Scanner Statistics
# =============================================================================

stocks_scanned = len(

    signals_df,

)

portfolio_positions = len(

    holdings_df,

)

signals_generated = len(

    signals_df,

)

unique_sectors = (

    signals_df[sector_col]

    .nunique()

    if sector_col is not None

    else 0

)

# =============================================================================
# Signal Counts
# =============================================================================

if signal_col is not None:

    signal_counts = (

        signals_df[signal_col]

        .astype(str)

        .str.upper()

        .value_counts()

    )

else:

    signal_counts = pd.Series(

        dtype=int,

    )

strong_buy_count = int(

    signal_counts.get(

        "STRONG BUY",

        0,

    )

)

buy_count = int(

    signal_counts.get(

        "BUY",

        0,

    )

)

watch_count = int(

    signal_counts.get(

        "WATCH",

        0,

    )

)

avoid_count = int(

    signal_counts.get(

        "AVOID",

        0,

    )

)

sell_count = int(

    signal_counts.get(

        "SELL",

        0,

    )

)

# =============================================================================
# KPI Cards
# =============================================================================

row1 = st.columns(

    4,

)

with row1[0]:

    st.metric(

        "Stocks Scanned",

        f"{stocks_scanned:,}",

    )

with row1[1]:

    st.metric(

        "Signals",

        f"{signals_generated:,}",

    )

with row1[2]:

    st.metric(

        "Portfolio",

        f"{portfolio_positions:,}",

    )

with row1[3]:

    st.metric(

        "Sectors",

        unique_sectors,

    )

row2 = st.columns(

    5,

)

with row2[0]:

    st.metric(

        "Strong Buy",

        strong_buy_count,

    )

with row2[1]:

    st.metric(

        "Buy",

        buy_count,

    )

with row2[2]:

    st.metric(

        "Watch",

        watch_count,

    )

with row2[3]:

    st.metric(

        "Avoid",

        avoid_count,

    )

with row2[4]:

    st.metric(

        "Sell",

        sell_count,

    )

divider()

# =============================================================================
# Scanner Summary
# =============================================================================

summary = [

    (
        "Signals",
        f"{signals_generated:,}",
        None,
    ),

    (
        "Avg Score",
        (
            f"{scores.mean():.2f}"
            if not scores.empty
            else "-"
        ),
        None,
    ),

    (
        "Highest Score",
        (
            f"{scores.max():.2f}"
            if not scores.empty
            else "-"
        ),
        None,
    ),

    (
        "Coverage",
        f"{unique_sectors} Sectors",
        None,
    ),

]

summary_row(summary)

summary_row(

    summary,

)

divider()

# =============================================================================
# Live Scanner
# =============================================================================

section(

    "Live Scanner",

    (
        "Browse today's scanner output "
        "with interactive filtering."
    ),

)

filter1, filter2, filter3 = st.columns(

    3,

)

with filter1:

    search_symbol = st.text_input(

        "Search Symbol",

        placeholder="Enter symbol...",

    )

with filter2:

    if signal_col is not None:

        signal_options = [

            "All",

            *sorted(

                signals_df[signal_col]

                .dropna()

                .astype(str)

                .unique()

            ),

        ]

    else:

        signal_options = [

            "All",

        ]

    selected_signal = st.selectbox(

        "Signal",

        signal_options,

    )

with filter3:

    if sector_col is not None:

        sector_options = [

            "All",

            *sorted(

                signals_df[sector_col]

                .dropna()

                .astype(str)

                .unique()

            ),

        ]

    else:

        sector_options = [

            "All",

        ]

    selected_sector = st.selectbox(

        "Sector",

        sector_options,

    )

filtered_signals = signals_df.copy()

if (

    symbol_col is not None

    and search_symbol

):

    filtered_signals = filtered_signals[

        filtered_signals[symbol_col]

        .astype(str)

        .str.contains(

            search_symbol,

            case=False,

            na=False,

        )

    ]

if (

    signal_col is not None

    and selected_signal != "All"

):

    filtered_signals = filtered_signals[

        filtered_signals[signal_col]

        .astype(str)

        == selected_signal

    ]

if (

    sector_col is not None

    and selected_sector != "All"

):

    filtered_signals = filtered_signals[

        filtered_signals[sector_col]

        .astype(str)

        == selected_sector

    ]

dataframe_info(

    filtered_signals,

)

holdings_table(

    filtered_signals,
    key="filtered_signals",

)

divider()

# =============================================================================
# Live Scanner Statistics
# =============================================================================

section(

    "Filtered Statistics",

    (
        "Summary statistics for the "
        "current scanner view."
    ),

)

filtered_scores = numeric_series(

    filtered_signals,

    score_col,

)

filtered_count = len(

    filtered_signals,

)

avg_score = (

    filtered_scores.mean()

    if not filtered_scores.empty

    else 0.0

)

best_score = (

    filtered_scores.max()

    if not filtered_scores.empty

    else 0.0

)

worst_score = (

    filtered_scores.min()

    if not filtered_scores.empty

    else 0.0

)

c1, c2, c3, c4 = st.columns(

    4,

)

with c1:

    st.metric(

        "Visible Stocks",

        filtered_count,

    )

with c2:

    st.metric(

        "Average Score",

        f"{avg_score:.2f}",

    )

with c3:

    st.metric(

        "Highest Score",

        f"{best_score:.2f}",

    )

with c4:

    st.metric(

        "Lowest Score",

        f"{worst_score:.2f}",

    )

divider()

# =============================================================================
# Today's Top Opportunities
# =============================================================================

section(

    "Today's Top Opportunities",

    (
        "Highest-ranked opportunities "
        "identified by today's scan."
    ),

)

if (

    score_col is not None

    and not filtered_signals.empty

):

    top_opportunities = (

        filtered_signals

        .sort_values(

            score_col,

            ascending=False,

        )

        .head(

            20,

        )

    )

    left, right = st.columns(

        [

            2,

            1,

        ]

    )

    with left:

        chart = px.bar(

            top_opportunities,

            x=symbol_col,

            y=score_col,

            text=score_col,

            title="Top Scores",

        )

        chart.update_traces(

            texttemplate="%{text:.1f}",

            textposition="outside",

        )

        st.plotly_chart(

            chart,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            top_opportunities,

            use_container_width=True,

            hide_index=True,

            height=520,

        )

else:

    st.info(

        "No scoring information available."

    )

divider()

# =============================================================================
# Market Breadth
# =============================================================================

section(

    "Market Breadth",

    (
        "Overall health of today's "
        "scanner universe."
    ),

)

if signal_col is not None:

    signal_upper = (

        filtered_signals[signal_col]

        .astype(str)

        .str.upper()

    )

    bullish = int(

        signal_upper.isin(

            [

                "STRONG BUY",

                "BUY",

            ]

        ).sum()

    )

    bearish = int(

        signal_upper.isin(

            [

                "SELL",

                "AVOID",

            ]

        ).sum()

    )

    neutral = int(

        signal_upper.eq(

            "WATCH",

        ).sum()

    )

else:

    bullish = 0

    bearish = 0

    neutral = 0

total = max(

    bullish + bearish + neutral,

    1,

)

bullish_pct = bullish / total * 100

bearish_pct = bearish / total * 100

neutral_pct = neutral / total * 100

c1, c2, c3 = st.columns(

    3,

)

with c1:

    st.metric(

        "Bullish",

        bullish,

        f"{bullish_pct:.1f}%",

    )

with c2:

    st.metric(

        "Neutral",

        neutral,

        f"{neutral_pct:.1f}%",

    )

with c3:

    st.metric(

        "Bearish",

        bearish,

        f"{bearish_pct:.1f}%",

    )

divider()

# =============================================================================
# Signal Distribution
# =============================================================================

section(

    "Signal Distribution",

    (
        "Distribution of today's "
        "recommendations."
    ),

)

if (

    signal_col is not None

    and not filtered_signals.empty

):

    distribution = (

        filtered_signals

        .groupby(

            signal_col,

            dropna=False,

        )

        .size()

        .reset_index(

            name="Count",

        )

    )

    left, right = st.columns(

        [

            2,

            1,

        ]

    )

    with left:

        fig = px.pie(

            distribution,

            names=signal_col,

            values="Count",

            hole=0.45,

            title="Signal Mix",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            distribution,

            use_container_width=True,

            hide_index=True,

            height=420,

        )

else:

    st.info(

        "Signal information unavailable."

    )

divider()

# =============================================================================
# Sector Activity
# =============================================================================

section(

    "Sector Activity",

    (
        "Signal generation by sector."
    ),

)

if (

    sector_col is not None

    and not filtered_signals.empty

):

    sector_activity = (

        filtered_signals

        .groupby(

            sector_col,

            dropna=False,

        )

        .size()

        .reset_index(

            name="Signals",

        )

        .sort_values(

            "Signals",

            ascending=False,

        )

    )

    left, right = st.columns(

        [

            2,

            1,

        ]

    )

    with left:

        chart = px.bar(

            sector_activity,

            x=sector_col,

            y="Signals",

            text="Signals",

            title="Signals by Sector",

        )

        chart.update_traces(

            textposition="outside",

        )

        st.plotly_chart(

            chart,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            sector_activity,

            use_container_width=True,

            hide_index=True,

            height=450,

        )

else:

    st.info(

        "Sector data unavailable."

    )

divider()

# =============================================================================
# Score Distribution
# =============================================================================

section(

    "Score Distribution",

    (
        "Distribution of composite "
        "scanner scores."
    ),

)

if not filtered_scores.empty:

    left, right = st.columns(

        [

            2,

            1,

        ]

    )

    with left:

        histogram = px.histogram(

            x=filtered_scores,

            nbins=30,

            title="Composite Scores",

        )

        histogram.update_layout(

            xaxis_title="Score",

            yaxis_title="Stocks",

        )

        st.plotly_chart(

            histogram,

            use_container_width=True,

        )

    with right:

        st.metric(

            "Average",

            f"{filtered_scores.mean():.2f}",

        )

        st.metric(

            "Median",

            f"{filtered_scores.median():.2f}",

        )

        st.metric(

            "Std Dev",

            f"{filtered_scores.std():.2f}",

        )

        st.metric(

            "Maximum",

            f"{filtered_scores.max():.2f}",

        )

else:

    st.info(

        "Score data unavailable."

    )

divider()


# =============================================================================
# New Signals
# =============================================================================

section(

    "New Signals",

    (
        "Highest-priority opportunities "
        "identified during today's scan."
    ),

)

if (

    signal_col is not None

    and not filtered_signals.empty

):

    new_signals = filtered_signals.copy()

    priority = [

        "STRONG BUY",

        "BUY",

        "WATCH",

        "AVOID",

        "SELL",

    ]

    new_signals["__priority__"] = (

        new_signals[signal_col]

        .astype(str)

        .str.upper()

        .map(

            {

                value: index

                for index, value

                in enumerate(priority)

            }

        )

        .fillna(

            len(priority),

        )

    )

    if score_col is not None:

        new_signals = (

            new_signals

            .sort_values(

                [

                    "__priority__",

                    score_col,

                ],

                ascending=[

                    True,

                    False,

                ],

            )

        )

    else:

        new_signals = (

            new_signals

            .sort_values(

                "__priority__",

            )

        )

    new_signals = (

        new_signals

        .drop(

            columns="__priority__",

        )

        .head(

            25,

        )

    )

    dataframe_info(

        new_signals,

    )

    holdings_table(

        new_signals,
        key="new_signals",

    )

else:

    st.info(

        "No signal data available."

    )

divider()


# =============================================================================
# Strong Buy Watchlist
# =============================================================================

section(

    "Strong Buy Watchlist",

    (
        "Highest conviction ideas "
        "generated today."
    ),

)

if (

    signal_col is not None

):

    strong_buy_df = (

        filtered_signals[

            filtered_signals[signal_col]

            .astype(str)

            .str.upper()

            == "STRONG BUY"

        ]

        .copy()

    )

    if (

        score_col is not None

    ):

        strong_buy_df = (

            strong_buy_df

            .sort_values(

                score_col,

                ascending=False,

            )

        )

    left, right = st.columns(

        [

            2,

            1,

        ]

    )

    with left:

        holdings_table(

            strong_buy_df,
            key="strong_buy_df",

        )

    with right:

        st.metric(

            "Strong Buy",

            len(

                strong_buy_df,

            ),

        )

        if (

            score_col is not None

            and not strong_buy_df.empty

        ):

            st.metric(

                "Average Score",

                f"{strong_buy_df[score_col].mean():.2f}",

            )

            st.metric(

                "Highest Score",

                f"{strong_buy_df[score_col].max():.2f}",

            )

else:

    st.info(

        "No Strong Buy signals."

    )

divider()

# =============================================================================
# Price vs Target
# =============================================================================

section(

    "Price vs Target",

    (
        "Potential upside based on "
        "current price and target."
    ),

)

if (

    price_col is not None

    and target_col is not None

):

    comparison = (

        filtered_signals.copy()

    )

    comparison[price_col] = pd.to_numeric(

        comparison[price_col],

        errors="coerce",

    )

    comparison[target_col] = pd.to_numeric(

        comparison[target_col],

        errors="coerce",

    )

    comparison = comparison.dropna(

        subset=[

            price_col,

            target_col,

        ]

    )

    if not comparison.empty:

        comparison["Upside %"] = (

            (

                comparison[target_col]

                -

                comparison[price_col]

            )

            /

            comparison[price_col]

        ) * 100

        comparison = comparison.sort_values(

            "Upside %",

            ascending=False,

        )

        left, right = st.columns(

            [

                2,

                1,

            ]

        )

        with left:

            fig = px.scatter(

                comparison,

                x=price_col,

                y=target_col,

                hover_name=symbol_col,

                size="Upside %",

                title="Price vs Target",

            )

            st.plotly_chart(

                fig,

                use_container_width=True,

            )

        with right:

            st.dataframe(

                comparison.head(

                    20,

                ),

                use_container_width=True,

                hide_index=True,

                height=520,

            )

    else:

        st.info(

            "Price/Target information unavailable."

        )

else:

    st.info(

        "Price or target columns not found."

    )

divider()

# =============================================================================
# Execution Queue
# =============================================================================

section(

    "Execution Queue",

    (
        "Recommended trades requiring "
        "review before execution."
    ),

)

if (

    signal_col is not None

):

    execution_queue = filtered_signals[

        filtered_signals[signal_col]

        .astype(str)

        .str.upper()

        .isin(

            [

                "STRONG BUY",

                "BUY",

            ]

        )

    ]

    dataframe_info(

        execution_queue,

    )

    holdings_table(

        execution_queue,
        key="execution_queue",

    )

else:

    st.info(

        "Execution queue unavailable."

    )

divider()

# =============================================================================
# Risk Alerts
# =============================================================================

section(

    "Risk Alerts",

    (
        "Potential issues requiring "
        "attention."
    ),

)

alerts = []

if not filtered_scores.empty:

    if filtered_scores.max() > 95:

        alerts.append(

            "Extremely high scoring securities detected."

        )

    if filtered_scores.min() < 20:

        alerts.append(

            "Very low scoring securities remain in today's universe."

        )

if bullish < bearish:

    alerts.append(

        "Bearish signals exceed bullish signals."

    )

if len(filtered_signals) == 0:

    alerts.append(

        "Scanner produced no actionable signals."

    )

if not alerts:

    st.success(

        "No operational alerts detected."

    )

else:

    for alert in alerts:

        st.warning(

            alert,

        )

divider()

# =============================================================================
# Data Freshness
# =============================================================================

section(

    "Data Freshness",

    (
        "Monitor dataset freshness and "
        "pipeline execution status."
    ),

)

freshness = pd.DataFrame(

    {

        "Dataset": [

            "Scanner",

            "Signals",

            "Portfolio",

            "Holdings",

        ],

        "Rows": [

            len(scanner_df),

            len(signals_df),

            len(portfolio_df),

            len(holdings_df),

        ],

        "Loaded": [

            not scanner_df.empty,

            not signals_df.empty,

            not portfolio_df.empty,

            not holdings_df.empty,

        ],

    }

)

left, right = st.columns(

    [

        2,

        1,

    ]

)

with left:

    st.dataframe(

        freshness,

        use_container_width=True,

        hide_index=True,

        height=260,

    )

with right:

    healthy = int(

        freshness["Loaded"].sum()

    )

    st.metric(

        "Healthy Datasets",

        f"{healthy}/4",

    )

    st.metric(

        "Refresh Interval",

        f"{CONFIG.refresh_seconds}s",

    )

    st.metric(

        "Last Refresh",

        datetime.now().strftime(

            "%H:%M:%S",

        ),

    )

divider()

# =============================================================================
# Download Center
# =============================================================================

section(

    "Download Center",

    (
        "Export scanner results and "
        "daily monitoring reports."
    ),

)

download_tabs = st.tabs(

    [

        "Signals",

        "Strong Buy",

        "Execution",

        "Scanner",

    ]

)

with download_tabs[0]:

    download_buttons(

        filtered_signals,

        filename="daily_signals",

    )

with download_tabs[1]:

    download_buttons(

        strong_buy_df

        if "strong_buy_df" in locals()

        else pd.DataFrame(),

        filename="strong_buy",

    )

with download_tabs[2]:

    download_buttons(

        execution_queue

        if "execution_queue" in locals()

        else pd.DataFrame(),

        filename="execution_queue",

    )

with download_tabs[3]:

    download_buttons(

        scanner_df,

        filename="scanner_snapshot",

    )

divider()

# =============================================================================
# Operational Diagnostics
# =============================================================================

section(

    "Operational Diagnostics",

    (
        "Health summary for today's "
        "scanner execution."
    ),

)

diagnostics = pd.DataFrame(

    {

        "Metric": [

            "Scanner Rows",

            "Signal Rows",

            "Portfolio Rows",

            "Holdings Rows",

            "Visible Signals",

            "Visible Strong Buy",

        ],

        "Value": [

            len(scanner_df),

            len(signals_df),

            len(portfolio_df),

            len(holdings_df),

            len(filtered_signals),

            (

                len(strong_buy_df)

                if "strong_buy_df" in locals()

                else 0

            ),

        ],

    }

)

st.dataframe(

    diagnostics,

    use_container_width=True,

    hide_index=True,

)

divider()

# =============================================================================
# Daily Insights
# =============================================================================

section(

    "Daily Insights",

    (
        "Automatically generated "
        "observations from today's scan."
    ),

)

insights: list[str] = []

if bullish > bearish:

    insights.append(

        f"Market breadth is positive ({bullish_pct:.1f}% bullish)."

    )

if bearish > bullish:

    insights.append(

        f"Market breadth is negative ({bearish_pct:.1f}% bearish)."

    )

if not filtered_scores.empty:

    insights.append(

        f"Average scanner score is {filtered_scores.mean():.2f}."

    )

    if filtered_scores.max() >= 90:

        insights.append(

            "High-conviction opportunities were identified."

        )

if (

    "strong_buy_df" in locals()

    and len(strong_buy_df) > 0

):

    insights.append(

        f"{len(strong_buy_df)} Strong Buy opportunities require review."

    )

if (

    "execution_queue" in locals()

    and len(execution_queue) > 0

):

    insights.append(

        f"{len(execution_queue)} securities are ready for execution."

    )

if not insights:

    insights.append(

        "No notable observations were generated today."

    )

for insight in insights:

    st.success(

        insight,

    )

divider()

# =============================================================================
# System Status
# =============================================================================

section(

    "System Status",

    (
        "Operational health of the "
        "daily monitoring platform."
    ),

)

status = {

    "Scanner":

        "Online"

        if not scanner_df.empty

        else "Offline",

    "Signals":

        "Online"

        if not signals_df.empty

        else "Offline",

    "Portfolio":

        "Online"

        if not portfolio_df.empty

        else "Offline",

    "Holdings":

        "Online"

        if not holdings_df.empty

        else "Offline",

}

summary_row(

    status,

)

divider()

# =============================================================================
# Footer
# =============================================================================

st.caption(

    "Institutional Scanner Monitor"

)

st.caption(

    "Daily Monitor Dashboard"

)

st.caption(

    f"Generated: {datetime.now():%d %b %Y %H:%M:%S}"

)

st.caption(

    "Production Build • Version 1.0"

)