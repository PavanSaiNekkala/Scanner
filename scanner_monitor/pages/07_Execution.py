"""
07_Execution.py
===============

Institutional Execution Dashboard.

Provides order management,
trade monitoring,
execution quality,
rebalance monitoring,
broker analytics,
and compliance reporting.
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
class ExecutionConfig:

    page_title: str = "Execution"

    page_icon: str = "⚡"

    layout: str = "wide"

    orders_file: Path = (
        REPORTS_DIR
        / "latest"
        / "orders.csv"
    )

    trades_file: Path = (
        REPORTS_DIR
        / "latest"
        / "trade_list.csv"
    )

    rebalance_file: Path = (
        REPORTS_DIR
        / "latest"
        / "rebalance_orders.csv"
    )

    execution_file: Path = (
        REPORTS_DIR
        / "history"
        / "execution_history.csv"
    )


CONFIG = ExecutionConfig()

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(

    page_title=CONFIG.page_title,

    page_icon=CONFIG.page_icon,

    layout=CONFIG.layout,

)

apply_theme()

render_sidebar()

dashboard_header()

st.title("⚡ Execution Dashboard")

st.caption(
    "Institutional trade execution, order management and execution analytics."
)

# ==========================================================
# Data Loading
# ==========================================================


orders = load_first_available_csv(
    CONFIG.orders_file,
)

trades = load_first_available_csv(
    CONFIG.trades_file,
)

rebalance = load_first_available_csv(
    CONFIG.rebalance_file,
)

history = load_first_available_csv(
    CONFIG.execution_file,
)

# ==========================================================
# Validation
# ==========================================================

if (

    orders.empty

    and trades.empty

    and rebalance.empty

):

    st.warning(

        "No execution data available."

    )

    st.stop()

# ==========================================================
# Column Detection
# ==========================================================

symbol_col = first_existing(

    trades,

    "Symbol",

    "Ticker",

    "Stock",

)

side_col = first_existing(

    trades,

    "Side",

    "Action",

)

quantity_col = first_existing(

    trades,

    "Quantity",

    "Qty",

)

price_col = first_existing(

    trades,

    "Price",

    "Execution Price",

)

status_col = first_existing(

    trades,

    "Status",

)

broker_col = first_existing(

    trades,

    "Broker",

)

slippage_col = first_existing(

    trades,

    "Slippage",

)

cost_col = first_existing(

    trades,

    "Cost",

    "Execution Cost",

)

time_col = first_existing(

    trades,

    "Execution Time",

    "Timestamp",

)

# ==========================================================
# Numeric Series
# ==========================================================

quantities = numeric_series(

    trades,

    quantity_col,

)

prices = numeric_series(

    trades,

    price_col,

)

costs = numeric_series(

    trades,

    cost_col,

)

slippage = numeric_series(

    trades,

    slippage_col,

)

# ==========================================================
# Execution KPIs
# ==========================================================

total_orders = len(
    trades
)

executed_orders = (

    trades[status_col]

    .eq("Executed")

    .sum()

    if status_col

    else 0

)

pending_orders = (

    trades[status_col]

    .eq("Pending")

    .sum()

    if status_col

    else 0

)

failed_orders = (

    trades[status_col]

    .eq("Failed")

    .sum()

    if status_col

    else 0

)

execution_value = (

    quantities

    * prices

).sum()

summary_row(

    [

        (

            "Orders",

            total_orders,

            None,

        ),

        (

            "Executed",

            executed_orders,

            None,

        ),

        (

            "Pending",

            pending_orders,

            None,

        ),

        (

            "Execution Value",

            f"{execution_value:,.0f}",

            None,

        ),

    ]

)

# ==========================================================
# Executive Summary
# ==========================================================

st.divider()

st.header(
    "Execution Summary",
)

fill_rate = (

    executed_orders

    / total_orders

    * 100

    if total_orders

    else 0

)

average_slippage = (

    slippage.mean()

    if len(slippage)

    else 0

)

average_cost = (

    costs.mean()

    if len(costs)

    else 0

)

execution_score = 100

execution_score -= min(

    failed_orders * 5,

    40,

)

execution_score -= min(

    average_slippage,

    20,

)

execution_score = max(

    execution_score,

    0,

)

left, right = st.columns(
    [
        2,
        1,
    ]
)

with left:

    summary_row(

        [

            (

                "Fill Rate",

                f"{fill_rate:.1f}%",

                None,

            ),

            (

                "Avg Slippage",

                f"{average_slippage:.2f}",

                None,

            ),

            (

                "Avg Cost",

                f"{average_cost:.2f}",

                None,

            ),

            (

                "Execution Score",

                f"{execution_score:.0f}",

                None,

            ),

        ]

    )

with right:

    color = "#16A34A"

    rating = "EXCELLENT"

    if execution_score < 85:

        color = "#65A30D"

        rating = "GOOD"

    if execution_score < 70:

        color = "#F59E0B"

        rating = "AVERAGE"

    if execution_score < 50:

        color = "#DC2626"

        rating = "POOR"

    st.markdown(

        f"""
<div
style="
background:{color};
padding:24px;
border-radius:14px;
text-align:center;
color:white;
">

<h3>

Execution Rating

</h3>

<h1>

{rating}

</h1>

<h2>

{execution_score:.0f}

</h2>

</div>

""",

        unsafe_allow_html=True,

    )

# ==========================================================
# Order Queue Overview
# ==========================================================

st.divider()

st.header(
    "Order Queue Overview",
)

if status_col:

    status_summary = (

        trades

        .groupby(status_col)

        .size()

        .reset_index(name="Orders")

        .sort_values(

            "Orders",

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

            status_summary,

        )

    with right:

        fig = px.pie(

            status_summary,

            names=status_col,

            values="Orders",

            hole=0.55,

        )

        fig.update_layout(

            height=400,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Pending Orders
# ==========================================================

st.divider()

st.header(
    "Pending Orders",
)

pending_df = pd.DataFrame()

if status_col:

    pending_df = trades.loc[

        trades[status_col]

        .astype(str)

        .str.upper()

        == "PENDING"

    ].copy()

if pending_df.empty:

    st.success(

        "No pending orders."

    )

else:

    holdings_table(

        pending_df,

    )

# ==========================================================
# Executed Orders
# ==========================================================

st.divider()

st.header(
    "Executed Orders",
)

executed_df = pd.DataFrame()

if status_col:

    executed_df = trades.loc[

        trades[status_col]

        .astype(str)

        .str.upper()

        == "EXECUTED"

    ].copy()

if executed_df.empty:

    st.info(

        "No executed orders."

    )

else:

    holdings_table(

        executed_df,

    )

# ==========================================================
# Failed Orders
# ==========================================================

st.divider()

st.header(
    "Failed Orders",
)

failed_df = pd.DataFrame()

if status_col:

    failed_df = trades.loc[

        trades[status_col]

        .astype(str)

        .str.upper()

        == "FAILED"

    ].copy()

if failed_df.empty:

    st.success(

        "No failed orders."

    )

else:

    holdings_table(

        failed_df,

    )

# ==========================================================
# Rebalance Queue
# ==========================================================

st.divider()

st.header(
    "Rebalance Queue",
)

if rebalance.empty:

    st.info(

        "No rebalance recommendations available."

    )

else:

    holdings_table(

        rebalance,

    )

# ==========================================================
# Trade Blotter
# ==========================================================

st.divider()

st.header(
    "Trade Blotter",
)

display_df = trades.copy()

search = st.text_input(

    "Search Symbol",

)

if (

    search

    and symbol_col

):

    display_df = display_df.loc[

        display_df[symbol_col]

        .astype(str)

        .str.contains(

            search,

            case=False,

            na=False,

        )

    ]

if side_col:

    sides = sorted(

        display_df[side_col]

        .dropna()

        .unique()

        .tolist()

    )

    selected_side = st.selectbox(

        "Order Side",

        [

            "All",

            *sides,

        ],

    )

    if selected_side != "All":

        display_df = display_df.loc[

            display_df[side_col]

            == selected_side

        ]

if status_col:

    statuses = sorted(

        display_df[status_col]

        .dropna()

        .unique()

        .tolist()

    )

    selected_status = st.selectbox(

        "Status",

        [

            "All",

            *statuses,

        ],

    )

    if selected_status != "All":

        display_df = display_df.loc[

            display_df[status_col]

            == selected_status

        ]

holdings_table(

    display_df,

)

# ==========================================================
# Live Execution Monitor
# ==========================================================

st.divider()

st.header(
    "Live Execution Monitor",
)

monitor = pd.DataFrame(

    [

        (

            "Total Orders",

            total_orders,

        ),

        (

            "Executed",

            executed_orders,

        ),

        (

            "Pending",

            pending_orders,

        ),

        (

            "Failed",

            failed_orders,

        ),

        (

            "Fill Rate",

            f"{fill_rate:.2f}%",

        ),

        (

            "Average Slippage",

            f"{average_slippage:.2f}",

        ),

        (

            "Execution Score",

            execution_score,

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

left, right = st.columns(

    [

        1,

        2,

    ]

)

with left:

    holdings_table(

        monitor,

    )

with right:

    if status_col:

        fig = px.bar(

            status_summary,

            x=status_col,

            y="Orders",

            text="Orders",

            color="Orders",

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
# Fill Rate Analytics
# ==========================================================

st.divider()

st.header(
    "Fill Rate Analytics",
)

if status_col:

    total = max(
        total_orders,
        1,
    )

    partial_orders = (

        trades[status_col]

        .astype(str)

        .str.upper()

        .eq("PARTIAL")

        .sum()

    )

    cancelled_orders = (

        trades[status_col]

        .astype(str)

        .str.upper()

        .eq("CANCELLED")

        .sum()

    )

    rejected_orders = (

        trades[status_col]

        .astype(str)

        .str.upper()

        .eq("REJECTED")

        .sum()

    )

    fill_metrics = pd.DataFrame(

        [

            (

                "Executed",

                executed_orders,

                executed_orders / total * 100,

            ),

            (

                "Partial",

                partial_orders,

                partial_orders / total * 100,

            ),

            (

                "Pending",

                pending_orders,

                pending_orders / total * 100,

            ),

            (

                "Rejected",

                rejected_orders,

                rejected_orders / total * 100,

            ),

            (

                "Cancelled",

                cancelled_orders,

                cancelled_orders / total * 100,

            ),

        ],

        columns=[

            "Status",

            "Orders",

            "Percentage",

        ],

    )

    left, right = st.columns(
        [1, 2]
    )

    with left:

        holdings_table(
            fill_metrics,
        )

    with right:

        fig = px.bar(

            fill_metrics,

            x="Status",

            y="Percentage",

            text="Percentage",

            color="Percentage",

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
# Slippage Analysis
# ==========================================================

st.divider()

st.header(
    "Slippage Analysis",
)

if len(slippage):

    slippage_summary = pd.DataFrame(

        [

            (

                "Average",

                slippage.mean(),

            ),

            (

                "Median",

                slippage.median(),

            ),

            (

                "Maximum",

                slippage.max(),

            ),

            (

                "Minimum",

                slippage.min(),

            ),

            (

                "Std Dev",

                slippage.std(),

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
            slippage_summary,
        )

    with right:

        fig = px.histogram(

            slippage,

            nbins=25,

        )

        fig.update_layout(

            height=420,

            xaxis_title="Slippage",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

else:

    st.info(
        "Slippage information unavailable."
    )

# ==========================================================
# Execution Cost Analytics
# ==========================================================

st.divider()

st.header(
    "Execution Cost Analysis",
)

if len(costs):

    total_cost = costs.sum()

    average_cost = costs.mean()

    maximum_cost = costs.max()

    minimum_cost = costs.min()

    summary_row(

        [

            (

                "Total Cost",

                f"{total_cost:,.2f}",

                None,

            ),

            (

                "Average Cost",

                f"{average_cost:.2f}",

                None,

            ),

            (

                "Highest Cost",

                f"{maximum_cost:.2f}",

                None,

            ),

            (

                "Lowest Cost",

                f"{minimum_cost:.2f}",

                None,

            ),

        ]

    )

    fig = px.box(

        y=costs,

    )

    fig.update_layout(

        height=400,

        yaxis_title="Execution Cost",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Broker Performance
# ==========================================================

st.divider()

st.header(
    "Broker Performance",
)

if broker_col:

    broker_summary = (

        trades

        .groupby(broker_col)

        .agg(

            Orders=(

                symbol_col,

                "count",

            ),

            Avg_Cost=(

                cost_col,

                "mean",

            ),

            Avg_Slippage=(

                slippage_col,

                "mean",

            ),

        )

        .reset_index()

    )

    holdings_table(
        broker_summary,
    )

    fig = px.bar(

        broker_summary,

        x=broker_col,

        y="Orders",

        color="Avg_Slippage",

        text="Orders",

    )

    fig.update_layout(

        height=420,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Trading Volume Analytics
# ==========================================================

st.divider()

st.header(
    "Trading Volume Analytics",
)

if quantity_col:

    volume_summary = pd.DataFrame(

        [

            (

                "Total Quantity",

                quantities.sum(),

            ),

            (

                "Average Quantity",

                quantities.mean(),

            ),

            (

                "Largest Order",

                quantities.max(),

            ),

            (

                "Median Quantity",

                quantities.median(),

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
            volume_summary,
        )

    with right:

        fig = px.histogram(

            quantities,

            nbins=30,

        )

        fig.update_layout(

            height=420,

            xaxis_title="Order Quantity",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Execution Timeline
# ==========================================================

st.divider()

st.header(
    "Execution Timeline",
)

if (

    time_col

    and

    not history.empty

):

    history[time_col] = pd.to_datetime(

        history[time_col],

        errors="coerce",

    )

    timeline_metric = first_existing(

        history,

        "Executed Orders",

        "Orders",

        "Count",

    )

    if timeline_metric:

        fig = px.line(

            history,

            x=time_col,

            y=timeline_metric,

            markers=True,

        )

        fig.update_layout(

            height=430,

            xaxis_title="",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

else:

    st.info(
        "Execution history unavailable."
    )

# ==========================================================
# Execution Quality Scorecard
# ==========================================================

st.divider()

st.header(
    "Execution Quality Scorecard",
)

quality_score = pd.DataFrame(

    [

        (

            "Fill Rate",

            f"{fill_rate:.2f}%",

        ),

        (

            "Average Slippage",

            f"{average_slippage:.2f}",

        ),

        (

            "Average Cost",

            f"{average_cost:.2f}",

        ),

        (

            "Execution Score",

            execution_score,

        ),

        (

            "Failed Orders",

            failed_orders,

        ),

        (

            "Pending Orders",

            pending_orders,

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

holdings_table(
    quality_score,
)

# ==========================================================
# Compliance Dashboard
# ==========================================================

st.divider()

st.header(
    "Execution Compliance",
)

max_slippage_limit = 0.50
max_order_value = 1_000_000

trade_value = quantities * prices

compliance = []

for i in range(len(trades)):

    violations = []

    if len(slippage) > i:

        if slippage.iloc[i] > max_slippage_limit:

            violations.append("High Slippage")

    if len(trade_value) > i:

        if trade_value.iloc[i] > max_order_value:

            violations.append("Large Order")

    compliance.append(

        ", ".join(violations)

        if violations

        else "PASS"

    )

compliance_df = trades.copy()

compliance_df["Compliance"] = compliance

summary = pd.DataFrame(

    [

        (

            "Pass",

            (

                compliance_df["Compliance"]

                == "PASS"

            ).sum(),

        ),

        (

            "Violations",

            (

                compliance_df["Compliance"]

                != "PASS"

            ).sum(),

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

left, right = st.columns([1, 2])

with left:

    holdings_table(summary)

with right:

    holdings_table(

        compliance_df,

    )

# ==========================================================
# Trade Exceptions
# ==========================================================

st.divider()

st.header(
    "Trade Exceptions",
)

exceptions = compliance_df.loc[

    compliance_df["Compliance"]

    != "PASS"

]

if exceptions.empty:

    st.success(

        "No execution exceptions detected."

    )

else:

    holdings_table(

        exceptions,

    )

# ==========================================================
# Execution Alerts
# ==========================================================

st.divider()

st.header(
    "Execution Alerts",
)

alerts = []

if failed_orders > 0:

    alerts.append(

        f"{failed_orders} failed orders require review."

    )

if pending_orders > 10:

    alerts.append(

        "Large pending order queue."

    )

if average_slippage > max_slippage_limit:

    alerts.append(

        "Average slippage exceeds policy."

    )

if average_cost > costs.median() * 2 if len(costs) else False:

    alerts.append(

        "Execution cost unusually high."

    )

if fill_rate < 95:

    alerts.append(

        "Fill rate below institutional target."

    )

if not alerts:

    st.success(

        "No active execution alerts."

    )

else:

    for message in alerts:

        st.warning(message)

# ==========================================================
# Order Lifecycle
# ==========================================================

st.divider()

st.header(
    "Order Lifecycle",
)

if status_col:

    lifecycle = (

        trades

        .groupby(status_col)

        .size()

        .reset_index(name="Orders")

    )

    fig = px.funnel(

        lifecycle,

        x="Orders",

        y=status_col,

    )

    fig.update_layout(

        height=420,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

    holdings_table(

        lifecycle,

    )


# ==========================================================
# OMS Diagnostics
# ==========================================================

st.divider()

st.header(
    "OMS Diagnostics",
)

diagnostics = pd.DataFrame(

    [

        (

            "Orders",

            total_orders,

        ),

        (

            "Executed",

            executed_orders,

        ),

        (

            "Pending",

            pending_orders,

        ),

        (

            "Failed",

            failed_orders,

        ),

        (

            "Execution Value",

            execution_value,

        ),

        (

            "Average Slippage",

            average_slippage,

        ),

        (

            "Average Cost",

            average_cost,

        ),

        (

            "Fill Rate",

            fill_rate,

        ),

        (

            "Execution Score",

            execution_score,

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

left, right = st.columns([1, 2])

with left:

    holdings_table(

        diagnostics,

    )

with right:

    dataframe_info(

        trades,

    )

# ==========================================================
# Download Center
# ==========================================================

st.divider()

st.header(
    "Execution Reports",
)

download_files = [

    (

        "Orders",

        CONFIG.orders_file,

        "orders.csv",

    ),

    (

        "Trades",

        CONFIG.trades_file,

        "trade_list.csv",

    ),

    (

        "Rebalance",

        CONFIG.rebalance_file,

        "rebalance_orders.csv",

    ),

    (

        "Execution History",

        CONFIG.execution_file,

        "execution_history.csv",

    ),

]

for label, path, filename in download_files:

    if path.exists():

        with open(path, "rb") as f:

            st.download_button(

                f"Download {label}",

                data=f,

                file_name=filename,

                mime="text/csv",

            )


# ==========================================================
# Executive Insights
# ==========================================================

st.divider()

st.header(
    "Execution Insights",
)

insights = []

if fill_rate >= 98:

    insights.append(

        "Execution quality is excellent with a very high fill rate."

    )

elif fill_rate >= 95:

    insights.append(

        "Execution quality is within acceptable institutional limits."

    )

else:

    insights.append(

        "Execution efficiency should be improved to increase fill rates."

    )

if average_slippage <= 0.25:

    insights.append(

        "Market impact remains well controlled."

    )

elif average_slippage <= 0.50:

    insights.append(

        "Slippage is acceptable but should be monitored."

    )

else:

    insights.append(

        "Slippage exceeds acceptable execution thresholds."

    )

if failed_orders == 0:

    insights.append(

        "No failed orders were detected."

    )

if pending_orders > 0:

    insights.append(

        "Pending orders should be monitored until completion."

    )

for insight in insights:

    st.info(insight)


# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(

    "Institutional Scanner Monitor"

)

st.caption(

    "Execution Dashboard • OMS • Rebalancing • Trade Monitoring • Broker Analytics • Compliance"

)