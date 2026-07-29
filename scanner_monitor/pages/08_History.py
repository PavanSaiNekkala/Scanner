"""
08_History.py
=============

Institutional History Dashboard.

Provides historical portfolio analytics,
audit trail, portfolio evolution,
allocation history,
historical performance,
risk evolution,
and execution history.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.config import REPORTS_DIR
from core.helpers import first_existing
from core.helpers import numeric_series
from core.theme import apply_theme

from ui.cards import dashboard_header
from ui.cards import summary_row

from ui.sidebar import render_sidebar

from ui.tables import dataframe_info
from ui.tables import holdings_table

from ui.loader import load_first_available_csv


# ==========================================================
# Configuration
# ==========================================================

@dataclass(slots=True)
class HistoryConfig:

    page_title: str = "History"

    page_icon: str = "📚"

    layout: str = "wide"

    portfolio_history: Path = (
        REPORTS_DIR
        / "history"
        / "portfolio_history.csv"
    )

    holdings_history: Path = (
        REPORTS_DIR
        / "history"
        / "holdings_history.csv"
    )

    performance_history: Path = (
        REPORTS_DIR
        / "history"
        / "performance_history.csv"
    )

    risk_history: Path = (
        REPORTS_DIR
        / "history"
        / "risk_history.csv"
    )

    execution_history: Path = (
        REPORTS_DIR
        / "history"
        / "execution_history.csv"
    )

    rebalance_history: Path = (
        REPORTS_DIR
        / "history"
        / "rebalance_history.csv"
    )

    signal_history: Path = (
        REPORTS_DIR
        / "history"
        / "signal_history.csv"
    )

    transaction_history: Path = (
        REPORTS_DIR
        / "history"
        / "transactions.csv"
    )

    audit_history: Path = (
        REPORTS_DIR
        / "history"
        / "audit_log.csv"
    )


CONFIG = HistoryConfig()

# ==========================================================
# Page
# ==========================================================

st.set_page_config(

    page_title=CONFIG.page_title,

    page_icon=CONFIG.page_icon,

    layout=CONFIG.layout,

)

apply_theme()

render_sidebar()

dashboard_header()

st.title(
    "📚 Historical Analytics Dashboard"
)

st.caption(
    "Institutional historical analytics, audit trail and portfolio evolution."
)


# ==========================================================
# Load Historical Data
# ==========================================================

portfolio = load_first_available_csv(
    CONFIG.portfolio_history,
)

holdings = load_first_available_csv(
    CONFIG.holdings_history,
)

performance = load_first_available_csv(
    CONFIG.performance_history,
)

risk = load_first_available_csv(
    CONFIG.risk_history,
)

execution = load_first_available_csv(
    CONFIG.execution_history,
)

rebalance = load_first_available_csv(
    CONFIG.rebalance_history,
)

signals = load_first_available_csv(
    CONFIG.signal_history,
)

transactions = load_first_available_csv(
    CONFIG.transaction_history,
)

audit = load_first_available_csv(
    CONFIG.audit_history,
)

# ==========================================================
# Validation
# ==========================================================

datasets = [

    portfolio,

    holdings,

    performance,

    risk,

    execution,

    rebalance,

    signals,

    transactions,

]

if all(

    df.empty

    for df in datasets

):

    st.warning(

        "Historical datasets are not available."

    )

    st.stop()

# ==========================================================
# Column Detection
# ==========================================================

date_col = first_existing(

    performance,

    "Date",

    "Timestamp",

)

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

return_col = first_existing(

    performance,

    "Return",

    "Daily Return",

)

portfolio_value_col = first_existing(

    performance,

    "Portfolio Value",

    "Equity",

    "NAV",

)

risk_col = first_existing(

    risk,

    "Risk Score",

    "Portfolio Health",

)

# ==========================================================
# Executive KPIs
# ==========================================================

history_records = sum(

    len(df)

    for df in datasets

)

date_range = 0

if (

    date_col

    and

    not performance.empty

):

    performance[date_col] = pd.to_datetime(

        performance[date_col],

        errors="coerce",

    )

    date_range = (

        performance[date_col].max()

        -

        performance[date_col].min()

    ).days

portfolio_records = len(portfolio)

performance_records = len(performance)

risk_records = len(risk)

summary_row(

    [

        (

            "Historical Records",

            history_records,

            None,

        ),

        (

            "Tracking Days",

            date_range,

            None,

        ),

        (

            "Performance Records",

            performance_records,

            None,

        ),

        (

            "Risk Records",

            risk_records,

            None,

        ),

    ]

)

# ==========================================================
# Executive Summary
# ==========================================================

st.divider()

st.header(
    "Historical Summary",
)

coverage_score = 100

missing_data = sum(

    df.isna().sum().sum()

    for df in datasets

)

coverage_score -= min(

    missing_data,

    50,

)

coverage_score = max(

    coverage_score,

    0,

)

left, right = st.columns(
    [2, 1]
)

with left:

    summary_row(

        [

            (

                "Portfolio History",

                portfolio_records,

                None,

            ),

            (

                "Transactions",

                len(transactions),

                None,

            ),

            (

                "Signals",

                len(signals),

                None,

            ),

            (

                "Coverage",

                f"{coverage_score:.0f}%",

                None,

            ),

        ]

    )

with right:

    if coverage_score >= 90:

        rating = "EXCELLENT"

        color = "#16A34A"

    elif coverage_score >= 75:

        rating = "GOOD"

        color = "#65A30D"

    elif coverage_score >= 60:

        rating = "AVERAGE"

        color = "#F59E0B"

    else:

        rating = "POOR"

        color = "#DC2626"

    st.markdown(

        f"""
<div style="
background:{color};
padding:24px;
border-radius:14px;
text-align:center;
color:white;
">

<h3>

History Quality

</h3>

<h1>

{rating}

</h1>

<h2>

{coverage_score:.0f}

</h2>

</div>
""",

        unsafe_allow_html=True,

    )

# ==========================================================
# Historical Analytics
# ==========================================================

st.divider()

st.header(
    "Historical Analytics",
)

# ----------------------------------------------------------
# Date Filter
# ----------------------------------------------------------

if (

    date_col

    and

    not performance.empty

):

    history = performance.copy()

    history[date_col] = pd.to_datetime(

        history[date_col],

        errors="coerce",

    )

    history = history.dropna(

        subset=[date_col]

    )

    min_date = history[date_col].min()

    max_date = history[date_col].max()

    selected_range = st.date_input(

        "Select Date Range",

        value=(

            min_date.date(),

            max_date.date(),

        ),

    )

    if (

        isinstance(

            selected_range,

            tuple,

        )

        and

        len(selected_range) == 2

    ):

        start_date, end_date = selected_range

        history = history.loc[

            (

                history[date_col]

                >= pd.Timestamp(start_date)

            )

            &

            (

                history[date_col]

                <= pd.Timestamp(end_date)

            )

        ]

else:

    history = performance.copy()

# ----------------------------------------------------------
# Historical Equity Curve
# ----------------------------------------------------------

st.divider()

st.header(
    "Historical Equity Curve",
)

if (

    not history.empty

    and

    portfolio_value_col

):

    fig = px.line(

        history,

        x=date_col,

        y=portfolio_value_col,

        markers=True,

    )

    fig.update_layout(

        height=450,

        xaxis_title="",

        yaxis_title="Portfolio Value",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

else:

    st.info(

        "Portfolio value history unavailable."

    )

# ----------------------------------------------------------
# Portfolio Timeline
# ----------------------------------------------------------

st.divider()

st.header(
    "Portfolio Timeline",
)

if (

    not history.empty

    and

    portfolio_value_col

):

    summary_row(

        [

            (

                "Starting Value",

                f"{history[portfolio_value_col].iloc[0]:,.2f}",

                None,

            ),

            (

                "Latest Value",

                f"{history[portfolio_value_col].iloc[-1]:,.2f}",

                None,

            ),

            (

                "Highest Value",

                f"{history[portfolio_value_col].max():,.2f}",

                None,

            ),

            (

                "Lowest Value",

                f"{history[portfolio_value_col].min():,.2f}",

                None,

            ),

        ]

    )

# ----------------------------------------------------------
# Historical Performance
# ----------------------------------------------------------

st.divider()

st.header(
    "Performance Timeline",
)

if (

    not history.empty

    and

    return_col

):

    fig = px.bar(

        history,

        x=date_col,

        y=return_col,

        color=return_col,

    )

    fig.update_layout(

        height=420,

        xaxis_title="",

        coloraxis_showscale=False,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ----------------------------------------------------------
# Cumulative Return
# ----------------------------------------------------------

if (

    not history.empty

    and

    return_col

):

    cumulative = history.copy()

    cumulative["Cumulative Return"] = (

        (

            1

            +

            cumulative[return_col]

            / 100

        )

        .cumprod()

        - 1

    ) * 100

    fig = px.area(

        cumulative,

        x=date_col,

        y="Cumulative Return",

    )

    fig.update_layout(

        height=420,

        xaxis_title="",

        yaxis_title="Cumulative Return (%)",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ----------------------------------------------------------
# Historical Risk Evolution
# ----------------------------------------------------------

st.divider()

st.header(
    "Risk Evolution",
)

if (

    not risk.empty

    and

    risk_col

):

    risk_date = first_existing(

        risk,

        "Date",

        "Timestamp",

    )

    if risk_date:

        risk[risk_date] = pd.to_datetime(

            risk[risk_date],

            errors="coerce",

        )

        fig = px.line(

            risk,

            x=risk_date,

            y=risk_col,

            markers=True,

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

            yaxis_title="Risk Score",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ----------------------------------------------------------
# Historical Holdings
# ----------------------------------------------------------

st.divider()

st.header(
    "Historical Holdings",
)

if holdings.empty:

    st.info(

        "Historical holdings unavailable."

    )

else:

    holdings_table(

        holdings,

    )

# ----------------------------------------------------------
# Sector Evolution
# ----------------------------------------------------------

st.divider()

st.header(
    "Sector Evolution",
)

if (

    sector_col

    and

    not holdings.empty

):

    sector_count = (

        holdings

        .groupby(

            sector_col

        )

        .size()

        .reset_index(

            name="Holdings"

        )

        .sort_values(

            "Holdings",

            ascending=False,

        )

    )

    left, right = st.columns(

        [

            1,

            2,

        ]

    )

    with left:

        holdings_table(

            sector_count,

        )

    with right:

        fig = px.bar(

            sector_count,

            x=sector_col,

            y="Holdings",

            color="Holdings",

            text="Holdings",

        )

        fig.update_layout(

            height=420,

            coloraxis_showscale=False,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ----------------------------------------------------------
# Allocation History
# ----------------------------------------------------------

st.divider()

st.header(
    "Allocation History",
)

weight_col = first_existing(

    holdings,

    "Weight",

    "Portfolio Weight",

)

if (

    weight_col

    and

    sector_col

):

    allocation = (

        holdings

        .groupby(

            sector_col

        )[

            weight_col

        ]

        .sum()

        .reset_index()

        .sort_values(

            weight_col,

            ascending=False,

        )

    )

    left, right = st.columns(

        [

            1,

            2,

        ]

    )

    with left:

        holdings_table(

            allocation,

        )

    with right:

        fig = px.treemap(

            allocation,

            path=[

                sector_col,

            ],

            values=weight_col,

            color=weight_col,

        )

        fig.update_layout(

            height=450,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Rolling Performance
# ==========================================================

st.divider()

st.header(
    "Rolling Performance Analytics",
)

if (

    not history.empty

    and

    return_col

):

    rolling = history.copy()

    rolling["20D Rolling Return"] = (

        (

            1

            +

            rolling[return_col]

            / 100

        )

        .rolling(20)

        .apply(

            np.prod,

            raw=True,

        )

        - 1

    ) * 100

    rolling["20D Volatility"] = (

        rolling[return_col]

        .rolling(20)

        .std()

    )

    left, right = st.columns(
        2
    )

    with left:

        fig = px.line(

            rolling,

            x=date_col,

            y="20D Rolling Return",

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

            yaxis_title="Rolling Return (%)",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    with right:

        fig = px.line(

            rolling,

            x=date_col,

            y="20D Volatility",

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

            yaxis_title="Rolling Volatility",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Drawdown History
# ==========================================================

st.divider()

st.header(
    "Drawdown History",
)

if (

    portfolio_value_col

    and

    not history.empty

):

    drawdown = history.copy()

    drawdown["Running Max"] = (

        drawdown[portfolio_value_col]

        .cummax()

    )

    drawdown["Drawdown"] = (

        drawdown[portfolio_value_col]

        /

        drawdown["Running Max"]

        - 1

    ) * 100

    left, right = st.columns(
        [2, 1]
    )

    with left:

        fig = px.area(

            drawdown,

            x=date_col,

            y="Drawdown",

        )

        fig.update_layout(

            height=430,

            xaxis_title="",

            yaxis_title="Drawdown (%)",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    with right:

        summary_row(

            [

                (

                    "Current",

                    f"{drawdown['Drawdown'].iloc[-1]:.2f}%",

                    None,

                ),

                (

                    "Maximum",

                    f"{drawdown['Drawdown'].min():.2f}%",

                    None,

                ),

                (

                    "Average",

                    f"{drawdown['Drawdown'].mean():.2f}%",

                    None,

                ),

                (

                    "Median",

                    f"{drawdown['Drawdown'].median():.2f}%",

                    None,

                ),

            ]

        )

# ==========================================================
# Transaction Timeline
# ==========================================================

st.divider()

st.header(
    "Transaction Timeline",
)

if not transactions.empty:

    transaction_date = first_existing(

        transactions,

        "Date",

        "Timestamp",

    )

    transaction_amount = first_existing(

        transactions,

        "Amount",

        "Value",

        "Trade Value",

    )

    if (

        transaction_date

        and

        transaction_amount

    ):

        transactions[transaction_date] = pd.to_datetime(

            transactions[transaction_date],

            errors="coerce",

        )

        daily_transactions = (

            transactions

            .groupby(

                transaction_date

            )[

                transaction_amount

            ]

            .sum()

            .reset_index()

        )

        fig = px.bar(

            daily_transactions,

            x=transaction_date,

            y=transaction_amount,

        )

        fig.update_layout(

            height=430,

            xaxis_title="",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Rebalance History
# ==========================================================

st.divider()

st.header(
    "Historical Rebalances",
)

if rebalance.empty:

    st.info(

        "No rebalance history available."

    )

else:

    holdings_table(

        rebalance,

    )

# ==========================================================
# Signal Timeline
# ==========================================================

st.divider()

st.header(
    "Signal Timeline",
)

if not signals.empty:

    signal_date = first_existing(

        signals,

        "Date",

        "Timestamp",

    )

    if signal_date:

        signals[signal_date] = pd.to_datetime(

            signals[signal_date],

            errors="coerce",

        )

        signal_counts = (

            signals

            .groupby(

                signal_date

            )

            .size()

            .reset_index(

                name="Signals"

            )

        )

        fig = px.line(

            signal_counts,

            x=signal_date,

            y="Signals",

            markers=True,

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Historical Attribution
# ==========================================================

st.divider()

st.header(
    "Historical Attribution",
)

if (

    sector_col

    and

    weight_col

    and

    not holdings.empty

):

    contribution_col = first_existing(

        holdings,

        "Contribution",

        "Return Contribution",

    )

    if contribution_col:

        attribution = (

            holdings

            .groupby(

                sector_col

            )[

                contribution_col

            ]

            .sum()

            .reset_index()

            .sort_values(

                contribution_col,

                ascending=False,

            )

        )

        fig = go.Figure(

            go.Waterfall(

                x=attribution[sector_col],

                y=attribution[contribution_col],

                measure=[

                    "relative"

                ]

                * len(attribution),

            )

        )

        fig.update_layout(

            height=430,

            showlegend=False,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

        holdings_table(

            attribution,

        )

# ==========================================================
# Monthly Calendar Heatmap
# ==========================================================

st.divider()

st.header(
    "Monthly Return Heatmap",
)

if (

    not history.empty

    and

    return_col

):

    calendar = history.copy()

    calendar["Year"] = calendar[date_col].dt.year

    calendar["Month"] = calendar[date_col].dt.strftime("%b")

    monthly = (

        calendar

        .groupby(

            [

                "Year",

                "Month",

            ]

        )[

            return_col

        ]

        .sum()

        .reset_index()

    )

    heatmap = monthly.pivot(

        index="Year",

        columns="Month",

        values=return_col,

    )

    fig = px.imshow(

        heatmap,

        text_auto=".1f",

        aspect="auto",

    )

    fig.update_layout(

        height=450,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Audit Trail
# ==========================================================

st.divider()

st.header(
    "Audit Trail",
)

if audit.empty:

    st.info(
        "Audit history is unavailable."
    )

else:

    audit_date_col = first_existing(
        audit,
        "Timestamp",
        "Date",
        "Created At",
    )

    audit_user_col = first_existing(
        audit,
        "User",
        "Modified By",
        "Owner",
    )

    audit_module_col = first_existing(
        audit,
        "Module",
        "Component",
    )

    audit_action_col = first_existing(
        audit,
        "Action",
        "Operation",
    )

    audit_status_col = first_existing(
        audit,
        "Status",
    )

    display_audit = audit.copy()

    search = st.text_input(
        "Search Audit Log",
        key="audit_search",
    )

    if search:

        mask = pd.Series(
            False,
            index=display_audit.index,
        )

        for column in display_audit.columns:

            mask |= (

                display_audit[column]

                .astype(str)

                .str.contains(

                    search,

                    case=False,

                    na=False,

                )

            )

        display_audit = display_audit.loc[mask]

    holdings_table(
        display_audit,
    )

# ==========================================================
# Change Log Summary
# ==========================================================

st.divider()

st.header(
    "Change Log Summary",
)

if (

    not audit.empty

    and

    audit_action_col

):

    action_summary = (

        audit

        .groupby(

            audit_action_col

        )

        .size()

        .reset_index(

            name="Count"

        )

        .sort_values(

            "Count",

            ascending=False,

        )

    )

    left, right = st.columns(
        [1, 2]
    )

    with left:

        holdings_table(
            action_summary,
        )

    with right:

        fig = px.bar(

            action_summary,

            x=audit_action_col,

            y="Count",

            color="Count",

            text="Count",

        )

        fig.update_layout(

            height=420,

            coloraxis_showscale=False,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Historical Diagnostics
# ==========================================================

st.divider()

st.header(
    "Historical Diagnostics",
)

diagnostics = pd.DataFrame(

    [

        (

            "Portfolio Records",

            len(portfolio),

        ),

        (

            "Holdings Records",

            len(holdings),

        ),

        (

            "Performance Records",

            len(performance),

        ),

        (

            "Risk Records",

            len(risk),

        ),

        (

            "Execution Records",

            len(execution),

        ),

        (

            "Rebalance Records",

            len(rebalance),

        ),

        (

            "Transaction Records",

            len(transactions),

        ),

        (

            "Audit Records",

            len(audit),

        ),

        (

            "Signal Records",

            len(signals),

        ),

        (

            "Tracking Days",

            date_range,

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

left, right = st.columns(
    [1, 2]
)

with left:

    holdings_table(
        diagnostics,
    )

with right:

    dataframe_info(
        performance,
    )

# ==========================================================
# Historical Data Quality
# ==========================================================

st.divider()

st.header(
    "Data Quality",
)

quality = pd.DataFrame(

    [

        (

            "Missing Values",

            sum(

                df.isna().sum().sum()

                for df in datasets

            ),

        ),

        (

            "Duplicate Holdings",

            holdings.duplicated().sum(),

        ),

        (

            "Duplicate Transactions",

            transactions.duplicated().sum(),

        ),

        (

            "Duplicate Signals",

            signals.duplicated().sum(),

        ),

        (

            "Duplicate Audit Records",

            audit.duplicated().sum(),

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

holdings_table(
    quality,
)

# ==========================================================
# Download Center
# ==========================================================

st.divider()

st.header(
    "Historical Downloads",
)

downloads = [

    (

        "Portfolio History",

        CONFIG.portfolio_history,

        "portfolio_history.csv",

    ),

    (

        "Performance History",

        CONFIG.performance_history,

        "performance_history.csv",

    ),

    (

        "Risk History",

        CONFIG.risk_history,

        "risk_history.csv",

    ),

    (

        "Execution History",

        CONFIG.execution_history,

        "execution_history.csv",

    ),

    (

        "Transaction History",

        CONFIG.transaction_history,

        "transactions.csv",

    ),

    (

        "Audit Log",

        CONFIG.audit_history,

        "audit_log.csv",

    ),

    (

        "Signal History",

        CONFIG.signal_history,

        "signal_history.csv",

    ),

    (

        "Rebalance History",

        CONFIG.rebalance_history,

        "rebalance_history.csv",

    ),

]

for label, path, filename in downloads:

    if path.exists():

        with open(

            path,

            "rb",

        ) as file:

            st.download_button(

                label=f"Download {label}",

                data=file,

                file_name=filename,

                mime="text/csv",

            )

# ==========================================================
# Executive Insights
# ==========================================================

st.divider()

st.header(
    "Historical Insights",
)

insights = []

if date_range >= 365:

    insights.append(
        "More than one year of historical data is available for long-term trend analysis."
    )

if len(transactions) > 1000:

    insights.append(
        "High trading activity detected across the historical period."
    )

if len(rebalance) > 0:

    insights.append(
        "Portfolio rebalancing history is available for allocation analysis."
    )

if coverage_score >= 90:

    insights.append(
        "Historical data coverage is excellent."
    )

elif coverage_score >= 75:

    insights.append(
        "Historical data coverage is good with limited missing information."
    )

else:

    insights.append(
        "Historical data quality should be improved before performing advanced analytics."
    )

if len(audit):

    insights.append(
        "Audit trail is available for governance and compliance reviews."
    )

for message in insights:

    st.info(
        message,
    )

# ==========================================================
# Executive Summary
# ==========================================================

st.divider()

st.header(
    "Executive Summary",
)

summary = pd.DataFrame(

    [

        (

            "History Rating",

            rating,

        ),

        (

            "Coverage Score",

            f"{coverage_score:.0f}%",

        ),

        (

            "Historical Records",

            history_records,

        ),

        (

            "Tracking Period (Days)",

            date_range,

        ),

        (

            "Transactions",

            len(transactions),

        ),

        (

            "Signals",

            len(signals),

        ),

        (

            "Audit Records",

            len(audit),

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

holdings_table(
    summary,
)

# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(
    "Institutional Scanner Monitor"
)

st.caption(
    "History Dashboard • Portfolio Evolution • Audit Trail • Transactions • Rebalances • Historical Analytics"
)