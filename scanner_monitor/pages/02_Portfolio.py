"""
pages/02_Portfolio.py
=====================

Institutional Portfolio Dashboard

Provides a consolidated portfolio view for the
Scanner Monitor application.

Features
--------
- Portfolio overview
- KPI dashboard
- Holdings analytics
- Sector exposure
- Risk overview
- Portfolio history
- Report downloads

Author
------
Nekkala Pavan Sai
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import streamlit as st

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
from ui.metrics import (
    dataframe_info,
    portfolio_kpis,
)
from ui.sidebar import (
    render_sidebar,
)
from ui.tables import (
    holdings_table,
    portfolio_table,
)
from ui.theme import (
    THEME,
    apply_theme,
)

LOGGER = logging.getLogger(__name__)

PAGE_TITLE = "Portfolio"

PAGE_ICON = "💼"

LAYOUT = "wide"


@dataclass(slots=True)
class PortfolioConfig:
    """
    Portfolio page configuration.
    """

    page_title: str = PAGE_TITLE

    page_icon: str = PAGE_ICON

    layout: str = LAYOUT

    holdings_height: int = 650

    show_statistics: bool = True

    show_downloads: bool = True

    enable_filters: bool = True

    enable_history: bool = True


CONFIG = PortfolioConfig()


# =============================================================================
# Streamlit Configuration
# =============================================================================

st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout=CONFIG.layout,
)

apply_theme()

inject_card_css()

render_sidebar()


# =============================================================================
# Session State
# =============================================================================


def initialize_session() -> None:
    """
    Initialize Portfolio page session state.
    """

    defaults = {
        "portfolio_loaded": False,
        "selected_symbol": None,
        "selected_sector": "All",
        "portfolio_search": "",
    }

    for key, value in defaults.items():

        st.session_state.setdefault(
            key,
            value,
        )


initialize_session()


# =============================================================================
# Data Loading
# =============================================================================


@st.cache_data(show_spinner=False)
def load_portfolio_data() -> ReportData:
    """
    Load cached portfolio reports.
    """

    LOGGER.info(
        "Loading portfolio reports."
    )

    return load_reports()


reports = load_portfolio_data()

portfolio_summary = reports.portfolio_summary.copy()

holdings = reports.holdings.copy()

risk_summary = reports.risk_summary.copy()

execution_summary = reports.execution_summary.copy()

portfolio_history = reports.portfolio_history.copy()

# =============================================================================
# Validation
# =============================================================================


def validate_reports(
    reports: ReportData,
) -> bool:
    """
    Validate that the required portfolio
    datasets are available.
    """

    required = {

        "Portfolio Summary": reports.portfolio_summary,

        "Holdings": reports.holdings,

    }

    missing: list[str] = []

    for name, dataframe in required.items():

        if dataframe.empty:

            missing.append(name)

    if missing:

        empty_state(

            "Portfolio Reports Not Available",

            (
                "Missing required report(s): "
                + ", ".join(missing)
                + ".\n\n"
                "Run the workflow to generate "
                "the latest portfolio reports."
            ),

        )

        return False

    return True


# =============================================================================
# Derived Data
# =============================================================================


def prepare_holdings(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean and prepare holdings dataset.
    """

    if df.empty:

        return df

    working = df.copy()

    working.columns = [

        str(column).strip()

        for column in working.columns

    ]

    return working


holdings = prepare_holdings(
    holdings,
)


# =============================================================================
# Header
# =============================================================================


section(

    "Portfolio Dashboard",

    (
        "Institutional portfolio overview, "
        "allocation, holdings and exposure."
    ),

)


# =============================================================================
# Portfolio KPIs
# =============================================================================


if validate_reports(reports):

    portfolio_kpis(
        portfolio_summary,
    )

    divider()


# =============================================================================
# Portfolio Summary
# =============================================================================


if CONFIG.show_statistics:

    section(

        "Portfolio Summary",

        (
            "Summary metrics generated "
            "from the latest workflow."
        ),

    )

    portfolio_table(
        portfolio_summary,
    )

    dataframe_info(
        portfolio_summary,
    )

    divider()


# =============================================================================
# Holdings Overview
# =============================================================================


section(

    "Current Holdings",

    (
        "Current active portfolio "
        "positions."
    ),

)

holdings_table(
    holdings,
    key="portfolio_holdings",
)

# =============================================================================
# Portfolio Analytics
# =============================================================================


def safe_column(
    df: pd.DataFrame,
    *columns: str,
) -> str | None:
    """
    Return the first matching column.
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
    Return numeric series.
    """

    if column is None:

        return pd.Series(dtype=float)

    return pd.to_numeric(

        df[column],

        errors="coerce",

    ).fillna(0.0)


market_value_col = safe_column(

    holdings,

    "Market Value",

    "Current Value",

    "Value",

    "Position Value",

)

weight_col = safe_column(

    holdings,

    "Weight",

    "Portfolio Weight",

    "Weight (%)",

)

return_col = safe_column(

    holdings,

    "Return %",

    "PnL %",

    "Profit %",

    "Return",

)

sector_col = safe_column(

    holdings,

    "Sector",

)

symbol_col = safe_column(

    holdings,

    "Symbol",

    "Ticker",

    "Stock",

)

market_values = numeric_series(

    holdings,

    market_value_col,

)

weights = numeric_series(

    holdings,

    weight_col,

)

returns = numeric_series(

    holdings,

    return_col,

)

total_value = float(

    market_values.sum(),

)

average_weight = float(

    weights.mean(),

)

largest_weight = float(

    weights.max(),

)

average_return = float(

    returns.mean(),

)

positive_positions = int(

    (returns > 0).sum(),

)

negative_positions = int(

    (returns < 0).sum(),

)


section(

    "Portfolio Analytics",

    (
        "High-level portfolio allocation "
        "and exposure statistics."
    ),

)

analytics = [

    (

        "Portfolio Value",

        f"${total_value:,.2f}",

        None,

    ),

    (

        "Average Weight",

        f"{average_weight:.2f}%",

        None,

    ),

    (

        "Largest Position",

        f"{largest_weight:.2f}%",

        None,

    ),

    (

        "Average Return",

        f"{average_return:.2f}%",

        None,

    ),

]

from ui.cards import summary_row

summary_row(

    analytics,

)

divider()


# =============================================================================
# Portfolio Breadth
# =============================================================================


col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Winning Positions",

        positive_positions,

    )

with col2:

    st.metric(

        "Losing Positions",

        negative_positions,

    )

with col3:

    st.metric(

        "Net Winners",

        positive_positions - negative_positions,

    )

# =============================================================================
# Sector Allocation
# =============================================================================

import plotly.express as px

section(

    "Sector Allocation",

    (
        "Portfolio diversification by sector."
    ),

)

if (

    sector_col is not None

    and weight_col is not None

):

    sector_summary = (

        holdings

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

    col1, col2 = st.columns(

        [2, 1],

    )

    with col1:

        fig = px.pie(

            sector_summary,

            names=sector_col,

            values=weight_col,

            hole=0.45,

            title="Portfolio Allocation",

        )

        fig.update_traces(

            textposition="inside",

            textinfo="percent+label",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    with col2:

        st.dataframe(

            sector_summary,

            use_container_width=True,

            hide_index=True,

            height=420,

        )

else:

    st.info(

        "Sector information not available."

    )

divider()


# =============================================================================
# Largest Holdings
# =============================================================================

section(

    "Top Holdings",

    (
        "Largest portfolio positions by weight."
    ),

)

if (

    symbol_col is not None

    and weight_col is not None

):

    top_holdings = (

        holdings

        .sort_values(

            weight_col,

            ascending=False,

        )

        .head(10)

    )

    st.dataframe(

        top_holdings,

        use_container_width=True,

        hide_index=True,

        height=420,

    )

    fig = px.bar(

        top_holdings,

        x=symbol_col,

        y=weight_col,

        text=weight_col,

        title="Top 10 Holdings",

    )

    fig.update_traces(

        texttemplate="%{text:.2f}",

        textposition="outside",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

else:

    st.info(

        "Unable to determine holding weights."

    )

divider()


# =============================================================================
# Portfolio Concentration
# =============================================================================

section(

    "Portfolio Concentration",

    (
        "Institutional concentration analysis."
    ),

)

if not weights.empty:

    top5 = float(

        weights.nlargest(5).sum()

    )

    top10 = float(

        weights.nlargest(10).sum()

    )

    median_weight = float(

        weights.median()

    )

    minimum_weight = float(

        weights.min()

    )

    maximum_weight = float(

        weights.max()

    )

    cols = st.columns(5)

    metrics = [

        (

            "Top 5",

            f"{top5:.2f}%",

        ),

        (

            "Top 10",

            f"{top10:.2f}%",

        ),

        (

            "Median",

            f"{median_weight:.2f}%",

        ),

        (

            "Minimum",

            f"{minimum_weight:.2f}%",

        ),

        (

            "Maximum",

            f"{maximum_weight:.2f}%",

        ),

    ]

    for column, metric in zip(

        cols,

        metrics,

    ):

        with column:

            st.metric(

                metric[0],

                metric[1],

            )

    histogram = px.histogram(

        x=weights,

        nbins=20,

        title="Position Weight Distribution",

    )

    histogram.update_layout(

        xaxis_title="Weight (%)",

        yaxis_title="Number of Positions",

    )

    st.plotly_chart(

        histogram,

        use_container_width=True,

    )

else:

    st.info(

        "Position weight data unavailable."

    )

divider()


# =============================================================================
# Performance Analysis
# =============================================================================

section(

    "Performance Analysis",

    (
        "Portfolio return distribution "
        "and performance overview."
    ),

)

if not returns.empty:

    col1, col2 = st.columns([2, 1])

    with col1:

        performance_fig = px.histogram(

            x=returns,

            nbins=30,

            title="Return Distribution",

        )

        performance_fig.update_layout(

            xaxis_title="Return (%)",

            yaxis_title="Positions",

        )

        st.plotly_chart(

            performance_fig,

            use_container_width=True,

        )

    with col2:

        st.metric(

            "Average Return",

            f"{returns.mean():.2f}%",

        )

        st.metric(

            "Median Return",

            f"{returns.median():.2f}%",

        )

        st.metric(

            "Best Position",

            f"{returns.max():.2f}%",

        )

        st.metric(

            "Worst Position",

            f"{returns.min():.2f}%",

        )

else:

    st.info(

        "Performance information unavailable."

    )

divider()


# =============================================================================
# Best / Worst Performers
# =============================================================================

section(

    "Top Performers",

    (
        "Best and worst performing "
        "portfolio positions."
    ),

)

if (

    symbol_col is not None

    and return_col is not None

):

    ranked = holdings.copy()

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

            height=360,

        )

    with right:

        st.subheader(

            "Top Losers",

        )

        st.dataframe(

            losers,

            use_container_width=True,

            hide_index=True,

            height=360,

        )

else:

    st.info(

        "Unable to identify portfolio returns."

    )

divider()


# =============================================================================
# Historical Portfolio Summary
# =============================================================================

section(

    "Portfolio History",

    (
        "Historical portfolio reports "
        "generated by the workflow."
    ),

)

if not portfolio_history.empty:

    dataframe_info(

        portfolio_history,

    )

    st.dataframe(

        portfolio_history,

        use_container_width=True,

        hide_index=True,

        height=450,

    )

else:

    st.info(

        "Portfolio history not available."

    )

divider()


# =============================================================================
# Risk Summary
# =============================================================================

section(

    "Risk Summary",

    (
        "Latest portfolio risk metrics."
    ),

)

if not risk_summary.empty:

    dataframe_info(

        risk_summary,

    )

    st.dataframe(

        risk_summary,

        use_container_width=True,

        hide_index=True,

    )

else:

    st.info(

        "Risk report unavailable."

    )

divider()

# =============================================================================
# Execution Summary
# =============================================================================

section(

    "Execution Summary",

    (
        "Latest execution metrics and "
        "workflow output."
    ),

)

if not execution_summary.empty:

    dataframe_info(
        execution_summary,
    )

    st.dataframe(

        execution_summary,

        use_container_width=True,

        hide_index=True,

        height=320,

    )

else:

    st.info(

        "Execution summary unavailable."

    )

divider()


# =============================================================================
# Portfolio Report Metadata
# =============================================================================

section(

    "Report Metadata",

    (
        "Information about the latest "
        "generated portfolio reports."
    ),

)

metadata = [

    (

        "Portfolio Summary",

        len(portfolio_summary),

    ),

    (

        "Holdings",

        len(holdings),

    ),

    (

        "Risk Records",

        len(risk_summary),

    ),

    (

        "Execution Records",

        len(execution_summary),

    ),

    (

        "History Records",

        len(portfolio_history),

    ),

]

metadata_columns = st.columns(len(metadata))

for column, item in zip(

    metadata_columns,

    metadata,

):

    with column:

        st.metric(

            item[0],

            item[1],

        )

divider()


# =============================================================================
# Downloads
# =============================================================================

if CONFIG.show_downloads:

    section(

        "Downloads",

        (
            "Export portfolio datasets "
            "for external analysis."
        ),

    )

    download_tabs = st.tabs(

        [

            "Holdings",

            "Portfolio",

            "Risk",

            "Execution",

        ]

    )

    with download_tabs[0]:

        from ui.tables import download_buttons

        download_buttons(

            holdings,
            filename="holdings",
            key="holdings_download",

        )

    with download_tabs[1]:

        download_buttons(

            portfolio_summary,
            filename="portfolio_summary",
            key="portfolio_summary_download",

        )

    with download_tabs[2]:

        download_buttons(

            risk_summary,
            filename="risk_summary",
            key="risk_summary_download",

        )

    with download_tabs[3]:

        download_buttons(

            execution_summary,
            filename="execution_summary",
            key="execution_summary_download",

        )

divider()


# =============================================================================
# Report Diagnostics
# =============================================================================

section(

    "Data Quality",

    (
        "Quick validation of loaded "
        "portfolio datasets."
    ),

)

quality = pd.DataFrame(

    {

        "Dataset": [

            "Portfolio Summary",

            "Holdings",

            "Risk Summary",

            "Execution Summary",

            "Portfolio History",

        ],

        "Rows": [

            len(portfolio_summary),

            len(holdings),

            len(risk_summary),

            len(execution_summary),

            len(portfolio_history),

        ],

        "Columns": [

            len(portfolio_summary.columns),

            len(holdings.columns),

            len(risk_summary.columns),

            len(execution_summary.columns),

            len(portfolio_history.columns),

        ],

        "Empty": [

            portfolio_summary.empty,

            holdings.empty,

            risk_summary.empty,

            execution_summary.empty,

            portfolio_history.empty,

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
# Portfolio Report JSON
# =============================================================================

section(

    "Portfolio Report",

    (
        "Summary extracted from the "
        "generated Portfolio_Report.json."
    ),

)

report_json = reports.report_json

if report_json:

    json_keys = sorted(

        report_json.keys()

    )

    overview = pd.DataFrame(

        {

            "Field": json_keys,

            "Value": [

                str(

                    report_json[key]

                )

                for key in json_keys

            ],

        }

    )

    st.dataframe(

        overview,

        use_container_width=True,

        hide_index=True,

        height=400,

    )

    with st.expander(

        "View Raw JSON",

        expanded=False,

    ):

        st.json(

            report_json,

            expanded=False,

        )

else:

    st.info(

        "Portfolio_Report.json not available."

    )

divider()


# =============================================================================
# Workflow Health
# =============================================================================

section(

    "Workflow Health",

    (
        "Status of the datasets loaded "
        "for this dashboard."
    ),

)

health = [

    (

        "Portfolio Summary",

        not portfolio_summary.empty,

    ),

    (

        "Holdings",

        not holdings.empty,

    ),

    (

        "Risk Summary",

        not risk_summary.empty,

    ),

    (

        "Execution Summary",

        not execution_summary.empty,

    ),

    (

        "Portfolio History",

        not portfolio_history.empty,

    ),

]

status_df = pd.DataFrame(

    {

        "Dataset": [

            item[0]

            for item in health

        ],

        "Status": [

            "Loaded"

            if item[1]

            else "Missing"

            for item in health

        ],

    }

)

st.dataframe(

    status_df,

    use_container_width=True,

    hide_index=True,

)

divider()


# =============================================================================
# Portfolio Insights
# =============================================================================

section(

    "Portfolio Insights",

    (
        "Automatically generated "
        "portfolio observations."
    ),

)

insights: list[str] = []

if not weights.empty:

    if largest_weight > 15:

        insights.append(

            (
                f"• Largest position is "
                f"{largest_weight:.2f}% "
                "of the portfolio."
            )

        )

    if top10 > 70:

        insights.append(

            (
                f"• Top 10 holdings account "
                f"for {top10:.2f}% "
                "of portfolio exposure."
            )

        )

if not returns.empty:

    if average_return > 0:

        insights.append(

            (
                f"• Average holding return "
                f"is {average_return:.2f}%."
            )

        )

    if positive_positions > negative_positions:

        insights.append(

            (
                "• Winning positions "
                "currently exceed losing "
                "positions."
            )

        )

if not insights:

    insights.append(

        "No portfolio insights available."

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

    "Portfolio Dashboard"

)

st.caption(

    "Generated from the latest workflow reports."

)