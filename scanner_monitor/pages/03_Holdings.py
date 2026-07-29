"""
pages/03_Holdings.py
====================

Institutional Holdings Dashboard

Displays detailed position-level analytics,
filters, and exposure for the current portfolio.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import streamlit as st

import plotly.express as px

from ui.cards import summary_row

from ui.cards import (
    divider,
    empty_state,
    inject_card_css,
    section,
)

from ui.loader import (
    ReportData,
    load_reports,
)

from ui.sidebar import render_sidebar

from ui.metrics import dataframe_info
from ui.tables import holdings_table

from ui.theme import (
    apply_theme,
)

LOGGER = logging.getLogger(__name__)

PAGE_TITLE = "Holdings"
PAGE_ICON = "📊"
LAYOUT = "wide"


@dataclass(slots=True)
class HoldingsConfig:
    """
    Holdings page configuration.
    """

    page_title: str = PAGE_TITLE
    page_icon: str = PAGE_ICON
    layout: str = LAYOUT

    table_height: int = 700

    enable_filters: bool = True
    enable_downloads: bool = True
    enable_charts: bool = True


CONFIG = HoldingsConfig()


# ---------------------------------------------------------------------
# Streamlit Configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout=CONFIG.layout,
)

apply_theme()
inject_card_css()
render_sidebar()


# ---------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------

def initialize_session() -> None:
    """
    Initialize Holdings page state.
    """

    defaults = {
        "holding_search": "",
        "selected_sector": "All",
        "selected_symbol": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


initialize_session()


# ---------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------

LOGGER.info(
    "Loading holdings reports."
)

reports = load_reports()

holdings = reports.holdings.copy()


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

if holdings.empty:

    empty_state(
        "Holdings Not Available",
        (
            "No holdings were found.\n\n"
            "Run the workflow before opening this page."
        ),
    )

    st.stop()


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

section(
    "Holdings Dashboard",
    (
        "Detailed analysis of all current "
        "portfolio positions."
    ),
)

divider()

# =============================================================================
# Holdings Preparation
# =============================================================================


def prepare_holdings(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize holdings dataframe.
    """

    if df.empty:

        return df

    working = df.copy()

    working.columns = [

        str(column).strip()

        for column in working.columns

    ]

    return working


def first_existing(
    df: pd.DataFrame,
    *columns: str,
) -> str | None:
    """
    Return first matching column.
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
    Safe numeric conversion.
    """

    if column is None:

        return pd.Series(dtype=float)

    return (

        pd.to_numeric(

            df[column],

            errors="coerce",

        )

        .fillna(0.0)

    )


holdings = prepare_holdings(
    holdings,
)

# =============================================================================
# Column Detection
# =============================================================================

symbol_col = first_existing(

    holdings,

    "Symbol",

    "Ticker",

    "Stock",

)

sector_col = first_existing(

    holdings,

    "Sector",

)

industry_col = first_existing(

    holdings,

    "Industry",

)

weight_col = first_existing(

    holdings,

    "Weight",

    "Portfolio Weight",

    "Weight (%)",

)

market_value_col = first_existing(

    holdings,

    "Market Value",

    "Current Value",

    "Value",

    "Position Value",

)

return_col = first_existing(

    holdings,

    "Return %",

    "PnL %",

    "Profit %",

    "Return",

)

quantity_col = first_existing(

    holdings,

    "Quantity",

    "Qty",

    "Shares",

)

# =============================================================================
# Numeric Columns
# =============================================================================

weights = numeric_series(

    holdings,

    weight_col,

)

returns = numeric_series(

    holdings,

    return_col,

)

market_values = numeric_series(

    holdings,

    market_value_col,

)

quantities = numeric_series(

    holdings,

    quantity_col,

)

# =============================================================================
# Derived Statistics
# =============================================================================

total_holdings = len(holdings)

portfolio_value = float(
    market_values.sum()
)

average_weight = float(
    weights.mean()
)

largest_weight = float(
    weights.max()
)

average_return = float(
    returns.mean()
)

winning_positions = int(
    (returns > 0).sum()
)

losing_positions = int(
    (returns < 0).sum()
)

flat_positions = int(
    (returns == 0).sum()
)

# =============================================================================
# Holdings KPIs
# =============================================================================

section(

    "Holdings Overview",

    (
        "Key statistics for the current "
        "portfolio holdings."
    ),

)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:

    st.metric(

        "Total Holdings",

        total_holdings,

    )

with kpi2:

    st.metric(

        "Portfolio Value",

        f"${portfolio_value:,.2f}",

    )

with kpi3:

    st.metric(

        "Average Return",

        f"{average_return:.2f}%",

    )

with kpi4:

    st.metric(

        "Largest Weight",

        f"{largest_weight:.2f}%",

    )


kpi5, kpi6, kpi7, kpi8 = st.columns(4)

with kpi5:

    st.metric(

        "Winning Positions",

        winning_positions,

    )

with kpi6:

    st.metric(

        "Losing Positions",

        losing_positions,

    )

with kpi7:

    st.metric(

        "Flat Positions",

        flat_positions,

    )

with kpi8:

    st.metric(

        "Average Weight",

        f"{average_weight:.2f}%",

    )

divider()

# =============================================================================
# Position Summary
# =============================================================================

section(

    "Position Summary",

    (
        "High-level summary of the current "
        "portfolio positions."
    ),

)

summary = [

    (

        "Portfolio Value",

        f"${portfolio_value:,.2f}",

        None,

    ),

    (

        "Largest Position",

        f"{largest_weight:.2f}%",

        None,

    ),

    (

        "Average Position",

        f"{average_weight:.2f}%",

        None,

    ),

    (

        "Average Return",

        f"{average_return:.2f}%",

        None,

    ),

]

summary_row(

    summary,

)

divider()

# =============================================================================
# Holdings Filters
# =============================================================================

section(

    "Filters",

    (
        "Filter holdings by symbol, "
        "sector and performance."
    ),

)

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:

    search_text = st.text_input(

        "Search Symbol",

        value="",

        placeholder="RELIANCE",

    )

with filter_col2:

    if sector_col is not None:

        sectors = ["All"] + sorted(

            holdings[sector_col]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

        selected_sector = st.selectbox(

            "Sector",

            sectors,

        )

    else:

        selected_sector = "All"

with filter_col3:

    minimum_return = st.number_input(

        "Minimum Return (%)",

        value=0.0,

        step=1.0,

    )

filtered_holdings = holdings.copy()

if (

    search_text

    and symbol_col is not None

):

    filtered_holdings = filtered_holdings[

        filtered_holdings[symbol_col]

        .astype(str)

        .str.contains(

            search_text,

            case=False,

            na=False,

        )

    ]

if (

    selected_sector != "All"

    and sector_col is not None

):

    filtered_holdings = filtered_holdings[

        filtered_holdings[sector_col]

        == selected_sector

    ]

if return_col is not None:

    filtered_holdings = filtered_holdings[

        pd.to_numeric(

            filtered_holdings[return_col],

            errors="coerce",

        ).fillna(0)

        >= minimum_return

    ]

divider()

# =============================================================================
# Holdings Table
# =============================================================================

section(

    "Current Holdings",

    (
        "Filtered holdings available in the "
        "current portfolio."
    ),

)

if filtered_holdings.empty:

    st.warning(

        "No holdings match the selected filters."

    )

else:

    dataframe_info(

        filtered_holdings,

    )

    holdings_table(

        filtered_holdings,
        key="filtered_holdings",

    )

divider()

# =============================================================================
# Holdings Statistics
# =============================================================================

section(

    "Filtered Statistics",

    (
        "Summary of the currently "
        "filtered holdings."
    ),

)

filtered_weights = numeric_series(

    filtered_holdings,

    weight_col,

)

filtered_returns = numeric_series(

    filtered_holdings,

    return_col,

)

filtered_market_values = numeric_series(

    filtered_holdings,

    market_value_col,

)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Filtered Holdings",

        len(filtered_holdings),

    )

with col2:

    st.metric(

        "Market Value",

        f"${filtered_market_values.sum():,.2f}",

    )

with col3:

    st.metric(

        "Average Return",

        f"{filtered_returns.mean():.2f}%",

    )

with col4:

    st.metric(

        "Average Weight",

        f"{filtered_weights.mean():.2f}%",

    )

divider()

# =============================================================================
# Top Holdings
# =============================================================================

section(

    "Top Holdings",

    (
        "Largest portfolio positions "
        "based on portfolio weight."
    ),

)

if (

    symbol_col is not None

    and weight_col is not None

):

    top_holdings = (

        filtered_holdings

        .sort_values(

            weight_col,

            ascending=False,

        )

        .head(10)

    )

    left, right = st.columns(

        [2, 1],

    )

    with left:

        chart = px.bar(

            top_holdings,

            x=symbol_col,

            y=weight_col,

            text=weight_col,

            title="Top 10 Holdings",

        )

        chart.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside",

        )

        st.plotly_chart(

            chart,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            top_holdings,

            use_container_width=True,

            hide_index=True,

            height=420,

        )

else:

    st.info(

        "Holding weight information unavailable."

    )

divider()

# =============================================================================
# Position Concentration
# =============================================================================

section(

    "Position Concentration",

    (
        "Portfolio concentration based "
        "on filtered holdings."
    ),

)

filtered_weights = numeric_series(

    filtered_holdings,

    weight_col,

)

if not filtered_weights.empty:

    top5 = float(

        filtered_weights.nlargest(5).sum()

    )

    top10 = float(

        filtered_weights.nlargest(10).sum()

    )

    median_weight = float(

        filtered_weights.median()

    )

    minimum_weight = float(

        filtered_weights.min()

    )

    maximum_weight = float(

        filtered_weights.max()

    )

    metric_columns = st.columns(5)

    metrics = [

        ("Top 5", f"{top5:.2f}%"),

        ("Top 10", f"{top10:.2f}%"),

        ("Median", f"{median_weight:.2f}%"),

        ("Minimum", f"{minimum_weight:.2f}%"),

        ("Maximum", f"{maximum_weight:.2f}%"),

    ]

    for column, metric in zip(

        metric_columns,

        metrics,

    ):

        with column:

            st.metric(

                metric[0],

                metric[1],

            )

    histogram = px.histogram(

        x=filtered_weights,

        nbins=20,

        title="Weight Distribution",

    )

    histogram.update_layout(

        xaxis_title="Weight (%)",

        yaxis_title="Number of Holdings",

    )

    st.plotly_chart(

        histogram,

        use_container_width=True,

    )

else:

    st.info(

        "Weight data unavailable."

    )

divider()

# =============================================================================
# Sector Exposure
# =============================================================================

section(

    "Sector Exposure",

    (
        "Portfolio allocation grouped "
        "by sector."
    ),

)

if (

    sector_col is not None

    and weight_col is not None

):

    sector_summary = (

        filtered_holdings

        .groupby(

            sector_col,

            dropna=False,

        )[weight_col]

        .sum()

        .reset_index()

        .sort_values(

            weight_col,

            ascending=False,

        )

    )

    left, right = st.columns(

        [2, 1],

    )

    with left:

        sector_chart = px.pie(

            sector_summary,

            names=sector_col,

            values=weight_col,

            hole=0.45,

            title="Sector Allocation",

        )

        sector_chart.update_traces(

            textposition="inside",

            textinfo="percent+label",

        )

        st.plotly_chart(

            sector_chart,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            sector_summary,

            use_container_width=True,

            hide_index=True,

            height=420,

        )

else:

    st.info(

        "Sector information unavailable."

    )

divider()

# =============================================================================
# Industry Exposure
# =============================================================================

section(

    "Industry Exposure",

    (
        "Portfolio allocation grouped "
        "by industry."
    ),

)

if (

    industry_col is not None

    and weight_col is not None

):

    industry_summary = (

        filtered_holdings

        .groupby(

            industry_col,

            dropna=False,

        )[weight_col]

        .sum()

        .reset_index()

        .sort_values(

            weight_col,

            ascending=False,

        )

    )

    left, right = st.columns(

        [2, 1],

    )

    with left:

        industry_chart = px.bar(

            industry_summary,

            x=industry_col,

            y=weight_col,

            text=weight_col,

            title="Industry Allocation",

        )

        industry_chart.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside",

        )

        industry_chart.update_layout(

            xaxis_title="Industry",

            yaxis_title="Weight (%)",

        )

        st.plotly_chart(

            industry_chart,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            industry_summary,

            use_container_width=True,

            hide_index=True,

            height=420,

        )

else:

    st.info(

        "Industry information unavailable."

    )

divider()


# =============================================================================
# Diversification Metrics
# =============================================================================

section(

    "Diversification",

    (
        "Portfolio diversification "
        "statistics."
    ),

)

sector_count = (

    filtered_holdings[sector_col].nunique()

    if sector_col is not None

    else 0

)

industry_count = (

    filtered_holdings[industry_col].nunique()

    if industry_col is not None

    else 0

)

largest_sector = (

    sector_summary.iloc[0][sector_col]

    if (

        sector_col is not None

        and not sector_summary.empty

    )

    else "-"

)

largest_sector_weight = (

    float(

        sector_summary.iloc[0][weight_col]

    )

    if (

        sector_col is not None

        and not sector_summary.empty

    )

    else 0.0

)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(

        "Sectors",

        sector_count,

    )

with c2:

    st.metric(

        "Industries",

        industry_count,

    )

with c3:

    st.metric(

        "Largest Sector",

        largest_sector,

    )

with c4:

    st.metric(

        "Sector Weight",

        f"{largest_sector_weight:.2f}%",

    )

divider()


# =============================================================================
# Winners vs Losers
# =============================================================================

section(

    "Performance Leaders",

    (
        "Best and worst performing "
        "positions in the filtered holdings."
    ),

)

if (

    symbol_col is not None

    and return_col is not None

):

    ranked = filtered_holdings.copy()

    ranked[return_col] = pd.to_numeric(

        ranked[return_col],

        errors="coerce",

    ).fillna(0.0)

    winners = (

        ranked

        .sort_values(

            return_col,

            ascending=False,

        )

        .head(10)

    )

    losers = (

        ranked

        .sort_values(

            return_col,

            ascending=True,

        )

        .head(10)

    )

    left, right = st.columns(2)

    with left:

        st.subheader(

            "Top Winners",

        )

        st.dataframe(

            winners,

            use_container_width=True,

            hide_index=True,

            height=380,

        )

    with right:

        st.subheader(

            "Top Losers",

        )

        st.dataframe(

            losers,

            use_container_width=True,

            hide_index=True,

            height=380,

        )

else:

    st.info(

        "Performance data unavailable."

    )

divider()

# =============================================================================
# Return Distribution
# =============================================================================

section(

    "Return Distribution",

    (
        "Distribution of returns across "
        "the filtered holdings."
    ),

)

if not filtered_returns.empty:

    left, right = st.columns(

        [2, 1],

    )

    with left:

        histogram = px.histogram(

            x=filtered_returns,

            nbins=30,

            title="Holding Returns",

        )

        histogram.update_layout(

            xaxis_title="Return (%)",

            yaxis_title="Number of Holdings",

        )

        st.plotly_chart(

            histogram,

            use_container_width=True,

        )

    with right:

        st.metric(

            "Average",

            f"{filtered_returns.mean():.2f}%",

        )

        st.metric(

            "Median",

            f"{filtered_returns.median():.2f}%",

        )

        st.metric(

            "Best",

            f"{filtered_returns.max():.2f}%",

        )

        st.metric(

            "Worst",

            f"{filtered_returns.min():.2f}%",

        )

else:

    st.info(

        "Return information unavailable."

    )

divider()

# =============================================================================
# Performance Breakdown
# =============================================================================

section(

    "Performance Breakdown",

    (
        "Classification of holdings by "
        "performance."
    ),

)

positive = int(

    (filtered_returns > 0).sum()

)

negative = int(

    (filtered_returns < 0).sum()

)

neutral = int(

    (filtered_returns == 0).sum()

)

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(

        "Positive",

        positive,

    )

with c2:

    st.metric(

        "Negative",

        negative,

    )

with c3:

    st.metric(

        "Neutral",

        neutral,

    )

divider()

# =============================================================================
# Holding Detail
# =============================================================================

section(

    "Holding Detail",

    (
        "Inspect an individual holding "
        "from the filtered portfolio."
    ),

)

if (

    symbol_col is not None

    and not filtered_holdings.empty

):

    symbols = (

        filtered_holdings[symbol_col]

        .dropna()

        .astype(str)

        .sort_values()

        .tolist()

    )

    selected_symbol = st.selectbox(

        "Select Holding",

        symbols,

    )

    holding = filtered_holdings[

        filtered_holdings[symbol_col]

        == selected_symbol

    ]

    if not holding.empty:

        row = holding.iloc[0]

        info1, info2, info3, info4 = st.columns(4)

        with info1:

            st.metric(

                "Symbol",

                str(row[symbol_col]),

            )

        with info2:

            if sector_col is not None:

                st.metric(

                    "Sector",

                    str(row[sector_col]),

                )

        with info3:

            if weight_col is not None:

                st.metric(

                    "Weight",

                    f"{float(row[weight_col]):.2f}%",

                )

        with info4:

            if return_col is not None:

                st.metric(

                    "Return",

                    f"{float(row[return_col]):.2f}%",

                )

        st.dataframe(

            holding,

            use_container_width=True,

            hide_index=True,

        )

else:

    st.info(

        "Holding details unavailable."

    )

divider()

# =============================================================================
# Position Diagnostics
# =============================================================================

section(

    "Position Diagnostics",

    (
        "Quality checks for the filtered "
        "holdings dataset."
    ),

)

diagnostics = pd.DataFrame(

    {

        "Metric": [

            "Rows",

            "Columns",

            "Duplicate Symbols",

            "Missing Symbols",

            "Missing Returns",

            "Missing Weights",

        ],

        "Value": [

            len(filtered_holdings),

            len(filtered_holdings.columns),

            (

                filtered_holdings[symbol_col]

                .duplicated()

                .sum()

                if symbol_col is not None

                else 0

            ),

            (

                filtered_holdings[symbol_col]

                .isna()

                .sum()

                if symbol_col is not None

                else 0

            ),

            (

                filtered_holdings[return_col]

                .isna()

                .sum()

                if return_col is not None

                else 0

            ),

            (

                filtered_holdings[weight_col]

                .isna()

                .sum()

                if weight_col is not None

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
# Downloads
# =============================================================================

from ui.tables import download_buttons

section(

    "Downloads",

    (
        "Export the filtered holdings "
        "for further analysis."
    ),

)

download_tabs = st.tabs(

    [

        "Filtered Holdings",

        "Top Holdings",

        "Sector Exposure",

    ]

)

with download_tabs[0]:

    download_buttons(

        filtered_holdings,

        filename="filtered_holdings",

    )

with download_tabs[1]:

    if (

        symbol_col is not None

        and weight_col is not None

    ):

        download_buttons(

            top_holdings,

            filename="top_holdings",

        )

    else:

        st.info(

            "Top holdings unavailable."

        )

with download_tabs[2]:

    if (

        sector_col is not None

        and weight_col is not None

    ):

        download_buttons(

            sector_summary,

            filename="sector_summary",

        )

    else:

        st.info(

            "Sector summary unavailable."

        )

divider()

# =============================================================================
# Data Quality
# =============================================================================

section(

    "Data Quality",

    (
        "Validation summary of the "
        "filtered holdings."
    ),

)

quality = pd.DataFrame(

    {

        "Dataset": [

            "Filtered Holdings",

            "Top Holdings",

            "Sector Summary",

            "Industry Summary",

        ],

        "Rows": [

            len(filtered_holdings),

            len(top_holdings)

            if "top_holdings" in locals()

            else 0,

            len(sector_summary)

            if "sector_summary" in locals()

            else 0,

            len(industry_summary)

            if "industry_summary" in locals()

            else 0,

        ],

        "Columns": [

            len(filtered_holdings.columns),

            len(top_holdings.columns)

            if "top_holdings" in locals()

            else 0,

            len(sector_summary.columns)

            if "sector_summary" in locals()

            else 0,

            len(industry_summary.columns)

            if "industry_summary" in locals()

            else 0,

        ],

        "Empty": [

            filtered_holdings.empty,

            (

                top_holdings.empty

                if "top_holdings" in locals()

                else True

            ),

            (

                sector_summary.empty

                if "sector_summary" in locals()

                else True

            ),

            (

                industry_summary.empty

                if "industry_summary" in locals()

                else True

            ),

        ],

    }

)

st.dataframe(

    quality,

    use_container_width=True,

    hide_index=True,

)

divider()


# =============================================================================
# Holdings Insights
# =============================================================================

section(

    "Portfolio Insights",

    (
        "Automatically generated "
        "observations from the filtered "
        "holdings."
    ),

)

insights: list[str] = []

if not filtered_weights.empty:

    if filtered_weights.max() > 15:

        insights.append(

            f"• Largest holding represents {filtered_weights.max():.2f}% of the portfolio."

        )

    if filtered_weights.nlargest(10).sum() > 70:

        insights.append(

            f"• Top 10 holdings represent {filtered_weights.nlargest(10).sum():.2f}% of total allocation."

        )

if not filtered_returns.empty:

    if filtered_returns.mean() > 0:

        insights.append(

            f"• Average holding return is {filtered_returns.mean():.2f}%."

        )

    if positive > negative:

        insights.append(

            "• More holdings are profitable than unprofitable."

        )

if not insights:

    insights.append(

        "No significant portfolio observations."

    )

for item in insights:

    st.success(

        item,

    )

divider()

# =============================================================================
# Footer
# =============================================================================

st.caption(

    "Institutional Scanner Monitor"

)

st.caption(

    "Holdings Dashboard"

)

st.caption(

    "Generated from the latest workflow reports."

)
