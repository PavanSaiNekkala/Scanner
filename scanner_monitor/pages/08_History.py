"""
pages/08_History.py
===================

Institutional Scanner Monitor

History Dashboard

Displays workflow-generated
historical portfolio reports.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.logger import get_logger
from core.session import (
    initialize as initialize_session,
)
from core.theme import (
    apply_theme,
    inject_card_css,
)

from ui.cards import (
    divider,
    empty_state,
    section,
)

from ui.loader import (
    ReportData,
    load_reports,
)

from ui.metrics import (
    dataframe_info,
    history_kpis,
)

from ui.sidebar import (
    render_sidebar,
)

from ui.tables import (
    holdings_table,
)

LOGGER = get_logger(__name__)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class HistoryConfig:
    """
    History dashboard configuration.
    """

    page_title: str = "History"

    page_icon: str = "📚"

    layout: str = "wide"

    chart_height: int = 420

    preview_rows: int = 25

    max_table_rows: int = 50


CONFIG = HistoryConfig()

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

initialize_session()

# =============================================================================
# Report Loading
# =============================================================================


@st.cache_data(show_spinner=False)
def get_reports() -> ReportData:
    """
    Load workflow-generated reports.
    """

    return load_reports()


try:

    reports = get_reports()

    latest = reports.latest

    history = reports.history

except Exception:

    LOGGER.exception(
        "Unable to load history reports."
    )

    st.error(
        "Unable to load history reports."
    )

    st.stop()

# =============================================================================
# Validation
# =============================================================================


def validate_reports(
    reports: ReportData,
) -> bool:
    """
    Validate required history reports.
    """

    required = {

        "Portfolio History":

            history.get(
                "portfolio_history",
                pd.DataFrame(),
            ),


        "Performance History":

            history.get(
                "performance_history",
                pd.DataFrame(),
            ),

    }

    missing = [

        report

        for report, dataframe

        in required.items()

        if dataframe.empty

    ]

    if not missing:

        return True

    empty_state(

        "History Reports Missing",

        (
            "The following reports "
            "are unavailable:\n\n"

            + "\n".join(
                f"• {report}"
                for report in missing
            )

            + "\n\nRun the workflow "
              "to regenerate reports."

        ),

    )

    return False


if not validate_reports(
    reports,
):

    st.stop()

# =============================================================================
# Working Reports
# =============================================================================

portfolio_history = history.get(
    "portfolio_history",
    pd.DataFrame(),
)

holdings_history = history.get(
    "holdings_history",
    pd.DataFrame(),
)

performance_history = history.get(
    "performance_history",
    pd.DataFrame(),
)

risk_history = history.get(
    "risk_history",
    pd.DataFrame(),
)

execution_history = history.get(
    "execution_history",
    pd.DataFrame(),
)

rebalance_history = history.get(
    "rebalance_history",
    pd.DataFrame(),
)

transaction_history = history.get(
    "transaction_history",
    pd.DataFrame(),
)

signal_history = history.get(
    "signal_history",
    pd.DataFrame(),
)

audit_history = history.get(
    "audit_history",
    pd.DataFrame(),
)

# =============================================================================
# Page Header
# =============================================================================

section(

    "Historical Analytics",

    (
        "Executive overview of the "
        "workflow-generated "
        "historical reports."
    ),

)

history_kpis(

    portfolio_history=portfolio_history,

    performance_history=performance_history,

    risk_history=risk_history,

)

divider()

# =============================================================================
# Executive Historical Summary
# =============================================================================

section(

    "Historical Summary",

    (
        "Summary of historical "
        "portfolio reports generated "
        "by the workflow."
    ),

)

summary = pd.DataFrame(

    [

        (

            "Portfolio History",

            len(portfolio_history),

        ),

        (

            "Performance History",

            len(performance_history),

        ),

        (

            "Risk History",

            len(risk_history),

        ),

        (

            "Execution History",

            len(execution_history),

        ),

        (

            "Transactions",

            len(transaction_history),

        ),

        (

            "Signals",

            len(signal_history),

        ),

        (

            "Audit Records",

            len(audit_history),

        ),

    ],

    columns=[

        "Report",

        "Records",

    ],

)

holdings_table(

    summary,

    key="history_summary",

)

dataframe_info(
    summary,
)

divider()

# =============================================================================
# Historical Overview
# =============================================================================

section(

    "Historical Overview",

    (
        "Timeline view of workflow-"
        "generated historical reports."
    ),

)

# =============================================================================
# Date Filter
# =============================================================================

date_column = None

for dataframe in (

    portfolio_history,

    performance_history,

    risk_history,

    execution_history,

):

    if dataframe.empty:

        continue

    for column in (

        "Date",

        "Trade Date",

        "Timestamp",

        "Scan Date",

    ):

        if column in dataframe.columns:

            date_column = column

            break

    if date_column:

        break

start_date = None

end_date = None

if (

    date_column

    and

    not portfolio_history.empty

):

    dates = pd.to_datetime(

        portfolio_history[
            date_column
        ],

        errors="coerce",

    ).dropna()

    if not dates.empty:

        start_date = dates.min()

        end_date = dates.max()

        selected_dates = st.date_input(

            "Date Range",

            value=(

                start_date,

                end_date,

            ),

        )

divider()

# =============================================================================
# Portfolio Timeline
# =============================================================================

section(

    "Portfolio Timeline",

    (
        "Historical portfolio "
        "records."
    ),

)

if (

    not portfolio_history.empty

):

    value_column = None

    for column in (

        "Portfolio Value",

        "Net Value",

        "Current Value",

    ):

        if column in portfolio_history.columns:

            value_column = column

            break

    if (

        date_column

        and

        value_column

    ):

        figure = px.line(

            portfolio_history,

            x=date_column,

            y=value_column,

            markers=True,

        )

        figure.update_layout(

            height=CONFIG.chart_height,

            xaxis_title="",

            yaxis_title=value_column,

        )

        st.plotly_chart(

            figure,

            use_container_width=True,

        )

    else:

        holdings_table(

            portfolio_history,

            key="portfolio_history",

        )

else:

    st.info(
        "Portfolio history "
        "is unavailable."
    )

divider()

# =============================================================================
# Performance Timeline
# =============================================================================

section(

    "Performance Timeline",

    (
        "Historical performance "
        "records."
    ),

)

if performance_history.empty:

    st.info(
        "Performance history "
        "is unavailable."
    )

else:

    holdings_table(

        performance_history,

        key="performance_history",

    )

divider()

# =============================================================================
# Risk Timeline
# =============================================================================

section(

    "Risk Timeline",

    (
        "Historical risk reports."
    ),

)

if risk_history.empty:

    st.info(
        "Risk history "
        "is unavailable."
    )

else:

    holdings_table(

        risk_history,

        key="risk_history",

    )

divider()

# =============================================================================
# Execution Timeline
# =============================================================================

section(

    "Execution Timeline",

    (
        "Historical execution "
        "records."
    ),

)

if execution_history.empty:

    st.info(
        "Execution history "
        "is unavailable."
    )

else:

    holdings_table(

        execution_history,

        key="execution_history",

    )

divider()

# =============================================================================
# Holdings History
# =============================================================================

section(

    "Holdings History",

    (
        "Historical portfolio "
        "holdings."
    ),

)

if holdings_history.empty:

    st.info(
        "Holdings history "
        "is unavailable."
    )

else:

    holdings_table(

        holdings_history,

        key="holdings_history",

    )

    dataframe_info(

        holdings_history,

    )

divider()

# =============================================================================
# Sector Evolution
# =============================================================================

section(

    "Sector Evolution",

    (
        "Historical sector allocation "
        "from workflow-generated reports."
    ),

)

sector_column = None

for column in (

    "Sector",

    "Sector Name",

):

    if column in holdings_history.columns:

        sector_column = column

        break

weight_column = None

for column in (

    "Portfolio Weight",

    "Weight",

    "Weight (%)",

):

    if column in holdings_history.columns:

        weight_column = column

        break

if (

    not holdings_history.empty

    and

    sector_column

    and

    weight_column

):

    sector_history = (

        holdings_history

        .groupby(

            sector_column,

            dropna=False,

        )[

            weight_column

        ]

        .sum()

        .reset_index()

        .sort_values(

            weight_column,

            ascending=False,

        )

    )

    left, right = st.columns(
        [2, 1],
    )

    with left:

        figure = px.bar(

            sector_history,

            x=sector_column,

            y=weight_column,

            color=weight_column,

            text=weight_column,

        )

        figure.update_layout(

            height=CONFIG.chart_height,

            coloraxis_showscale=False,

        )

        st.plotly_chart(

            figure,

            use_container_width=True,

        )

    with right:

        st.dataframe(

            sector_history,

            use_container_width=True,

            hide_index=True,

        )

else:

    st.info(
        "Sector history "
        "is unavailable."
    )

divider()

# =============================================================================
# Allocation History
# =============================================================================

section(

    "Allocation History",

    (
        "Historical portfolio "
        "allocation."
    ),

)

if holdings_history.empty:

    st.info(
        "Allocation history "
        "is unavailable."
    )

else:

    holdings_table(

        holdings_history,

        key="allocation_history",

    )

divider()

# =============================================================================
# Transaction History
# =============================================================================

section(

    "Transaction History",

    (
        "Historical portfolio "
        "transactions."
    ),

)

if transaction_history.empty:

    st.info(
        "Transaction history "
        "is unavailable."
    )

else:

    holdings_table(

        transaction_history,

        key="transaction_history",

    )

    dataframe_info(
        transaction_history,
    )

divider()

# =============================================================================
# Signal History
# =============================================================================

section(

    "Signal History",

    (
        "Historical scanner "
        "signals."
    ),

)

if signal_history.empty:

    st.info(
        "Signal history "
        "is unavailable."
    )

else:

    holdings_table(

        signal_history,

        key="signal_history",

    )

divider()

# =============================================================================
# Rebalance History
# =============================================================================

section(

    "Rebalance History",

    (
        "Historical portfolio "
        "rebalancing activity."
    ),

)

if rebalance_history.empty:

    st.info(
        "Rebalance history "
        "is unavailable."
    )

else:

    holdings_table(

        rebalance_history,

        key="rebalance_history",

    )

divider()

# =============================================================================
# Audit Trail
# =============================================================================

section(

    "Audit Trail",

    (
        "Workflow audit "
        "history."
    ),

)

if audit_history.empty:

    st.info(
        "Audit trail "
        "is unavailable."
    )

else:

    holdings_table(

        audit_history,

        key="audit_history",

    )

    dataframe_info(
        audit_history,
    )

divider()

# =============================================================================
# Historical Diagnostics
# =============================================================================

section(

    "Historical Diagnostics",

    (
        "Health and completeness of "
        "workflow-generated historical "
        "reports."
    ),

)

diagnostics = pd.DataFrame(

    [

        {

            "Report": "Portfolio History",

            "Records": len(
                portfolio_history,
            ),

            "Status":

                "Available"

                if not portfolio_history.empty

                else "Missing",

        },

        {

            "Report": "Holdings History",

            "Records": len(
                holdings_history,
            ),

            "Status":

                "Available"

                if not holdings_history.empty

                else "Missing",

        },

        {

            "Report": "Performance History",

            "Records": len(
                performance_history,
            ),

            "Status":

                "Available"

                if not performance_history.empty

                else "Missing",

        },

        {

            "Report": "Risk History",

            "Records": len(
                risk_history,
            ),

            "Status":

                "Available"

                if not risk_history.empty

                else "Missing",

        },

        {

            "Report": "Execution History",

            "Records": len(
                execution_history,
            ),

            "Status":

                "Available"

                if not execution_history.empty

                else "Missing",

        },

        {

            "Report": "Transaction History",

            "Records": len(
                transaction_history,
            ),

            "Status":

                "Available"

                if not transaction_history.empty

                else "Missing",

        },

        {

            "Report": "Signal History",

            "Records": len(
                signal_history,
            ),

            "Status":

                "Available"

                if not signal_history.empty

                else "Missing",

        },

        {

            "Report": "Audit History",

            "Records": len(
                audit_history,
            ),

            "Status":

                "Available"

                if not audit_history.empty

                else "Missing",

        },

    ]

)

st.dataframe(

    diagnostics,

    use_container_width=True,

    hide_index=True,

)

divider()

# =============================================================================
# Data Quality
# =============================================================================

section(

    "Data Quality",

    (
        "Overview of the historical "
        "report quality."
    ),

)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Portfolio",

        len(
            portfolio_history,
        ),

    )

with col2:

    st.metric(

        "Performance",

        len(
            performance_history,
        ),

    )

with col3:

    st.metric(

        "Risk",

        len(
            risk_history,
        ),

    )

with col4:

    st.metric(

        "Execution",

        len(
            execution_history,
        ),

    )

divider()

# =============================================================================
# Report Status
# =============================================================================

section(

    "Report Status",

    (
        "Workflow reports loaded "
        "for this dashboard."
    ),

)

status = pd.DataFrame(

    [

        {

            "Report": "Portfolio",

            "Rows": len(
                portfolio_history,
            ),

        },

        {

            "Report": "Holdings",

            "Rows": len(
                holdings_history,
            ),

        },

        {

            "Report": "Performance",

            "Rows": len(
                performance_history,
            ),

        },

        {

            "Report": "Risk",

            "Rows": len(
                risk_history,
            ),

        },

        {

            "Report": "Execution",

            "Rows": len(
                execution_history,
            ),

        },

        {

            "Report": "Transactions",

            "Rows": len(
                transaction_history,
            ),

        },

        {

            "Report": "Signals",

            "Rows": len(
                signal_history,
            ),

        },

        {

            "Report": "Audit",

            "Rows": len(
                audit_history,
            ),

        },

    ]

)

st.dataframe(

    status,

    use_container_width=True,

    hide_index=True,

)

divider()

# =============================================================================
# Explore Reports
# =============================================================================

section(

    "Explore Reports",

    (
        "Navigate through the "
        "Institutional Scanner Monitor."
    ),

)

left, right = st.columns(2)

with left:

    st.info(
        """
📊 **Dashboard**

Executive overview.
"""
    )

    st.info(
        """
📈 **Daily Monitor**

Scanner activity.
"""
    )

    st.info(
        """
🛡️ **Risk**

Portfolio risk reports.
"""
    )

with right:

    st.info(
        """
📉 **Performance**

Performance analytics.
"""
    )

    st.info(
        """
⚡ **Execution**

Execution reports.
"""
    )

    st.info(
        """
📁 **Portfolio**

Portfolio reports.
"""
    )

divider()

# =============================================================================
# Footer
# =============================================================================

st.caption(
    "Institutional Scanner Monitor"
)

st.caption(
    "Historical Dashboard"
)

st.caption(
    (
        "Workflow Report Viewer • "
        "Historical Analytics"
    )
)