"""
pages/01_Dashboard.py
=====================

Institutional Scanner Monitor

Executive Dashboard

Displays a high-level overview of the
latest generated workflow reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from core.logger import get_logger
from ui.loader import (
    ReportData,
    load_reports,
)

LOGGER = get_logger(__name__)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class DashboardConfig:
    """
    Dashboard configuration.
    """

    page_title: str = "Dashboard"

    page_icon: str = "🏠"

    layout: str = "wide"

    preview_rows: int = 5


CONFIG = DashboardConfig()

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout=CONFIG.layout,
)

# =============================================================================
# Data Loading
# =============================================================================


@st.cache_data(show_spinner=False)
def get_reports() -> ReportData:
    """
    Load all workflow reports.
    """

    return load_reports()


try:

    reports = get_reports()

    latest = reports.latest

    history = reports.history

except Exception:

    LOGGER.exception(
        "Unable to load dashboard reports."
    )

    st.error(
        "Unable to load reports."
    )

    st.stop()

# =============================================================================
# Helper Functions
# =============================================================================


def safe_len(
    dataframe: pd.DataFrame,
) -> int:
    """
    Safely return dataframe length.
    """

    if dataframe is None:

        return 0

    try:

        return len(dataframe)

    except Exception:

        return 0


def report_status(
    dataframe: pd.DataFrame,
) -> str:
    """
    Return report status icon.
    """

    if dataframe is None:

        return "❌ Missing"

    if dataframe.empty:

        return "⚠ Empty"

    return "✅ Available"


def report_modified(
    dataframe: pd.DataFrame,
) -> str:
    """
    Return latest timestamp if available.
    """

    if dataframe.empty:

        return "-"

    return datetime.now().strftime(
        "%d %b %Y %H:%M"
    )


def preview_section(
    title: str,
    dataframe: pd.DataFrame,
) -> None:
    """
    Display report preview.
    """

    st.subheader(title)

    if dataframe.empty:

        st.info(
            f"{title} not available."
        )

        return

    st.dataframe(
        dataframe.head(
            CONFIG.preview_rows,
        ),
        use_container_width=True,
        hide_index=True,
    )

    if len(dataframe) > CONFIG.preview_rows:

        st.caption(
            f"Showing first "
            f"{CONFIG.preview_rows} of "
            f"{len(dataframe):,} rows."
        )

    st.divider()


def trade_statistics() -> tuple[int, int]:
    """
    Return target hit and stop loss statistics.
    """

    dataframe = latest.get(
        "daily_monitor",
        pd.DataFrame(),
    )

    if dataframe.empty:

        return 0, 0


    if (
        "trade_status"
        not in dataframe.columns
    ):

        return 0, 0


    status = (

        dataframe["trade_status"]

        .astype(str)

        .str.upper()

    )


    target_hits = int(

        (

            status

            ==

            "TARGET HIT"

        ).sum()

    )


    stop_losses = int(

        (

            status

            ==

            "STOP LOSS"

        ).sum()

    )


    return (

        target_hits,

        stop_losses,

    )

# =============================================================================
# Executive Metrics
# =============================================================================

portfolio_df = latest.get(
    "portfolio_summary",
    pd.DataFrame(),
)

holdings_df = latest.get(
    "holdings",
    pd.DataFrame(),
)

daily_monitor_df = latest.get(
    "daily_monitor",
    pd.DataFrame(),
)

risk_df = latest.get(
    "risk_summary",
    pd.DataFrame(),
)

execution_df = latest.get(
    "execution_summary",
    pd.DataFrame(),
)


holdings = safe_len(
    holdings_df,
)


daily_monitor = safe_len(
    daily_monitor_df,
)


portfolio = safe_len(
    portfolio_df,
)


risk = safe_len(
    risk_df,
)


execution = safe_len(
    execution_df,
)


target_hits, stop_losses = (
    trade_statistics()
)

# =============================================================================
# Dashboard Header
# =============================================================================

st.title(
    "🏠 Executive Dashboard"
)

st.caption(
    "Institutional Scanner Monitor"
)

st.caption(
    "Executive overview of the latest "
    "generated workflow reports."
)

st.divider()

# =============================================================================
# Executive KPIs
# =============================================================================

row1 = st.columns(3)

with row1[0]:

    st.metric(
        "Portfolio",
        holdings,
    )

with row1[1]:

    st.metric(
        "Daily Monitor",
        daily_monitor,
    )

with row1[2]:

    st.metric(
        "Target Hits",
        target_hits,
    )

row2 = st.columns(3)

with row2[0]:

    st.metric(
        "Risk Reports",
        risk,
    )

with row2[1]:

    st.metric(
        "Execution",
        execution,
    )

with row2[2]:

    st.metric(
        "Stop Losses",
        stop_losses,
    )

st.divider()
# =============================================================================
# Workflow Status
# =============================================================================

st.subheader(
    "Workflow Status"
)


status = pd.DataFrame(

    [

        {
            "Report": "Portfolio Summary",

            "Rows": safe_len(
                portfolio_df,
            ),

            "Status": report_status(
                portfolio_df,
            ),

            "Updated": report_modified(
                portfolio_df,
            ),
        },


        {
            "Report": "Holdings",

            "Rows": safe_len(
                holdings_df,
            ),

            "Status": report_status(
                holdings_df,
            ),

            "Updated": report_modified(
                holdings_df,
            ),
        },


        {
            "Report": "Daily Monitor",

            "Rows": safe_len(
                daily_monitor_df,
            ),

            "Status": report_status(
                daily_monitor_df,
            ),

            "Updated": report_modified(
                daily_monitor_df,
            ),
        },


        {
            "Report": "Risk Summary",

            "Rows": safe_len(
                risk_df,
            ),

            "Status": report_status(
                risk_df,
            ),

            "Updated": report_modified(
                risk_df,
            ),
        },


        {
            "Report": "Execution Summary",

            "Rows": safe_len(
                execution_df,
            ),

            "Status": report_status(
                execution_df,
            ),

            "Updated": report_modified(
                execution_df,
            ),
        },

    ]

)


st.dataframe(

    status,

    use_container_width=True,

    hide_index=True,

)


st.divider()

# =============================================================================
# Report Previews
# =============================================================================

preview_section(
    "Portfolio Summary",
    portfolio_df,
)


preview_section(
    "Current Holdings",
    holdings_df,
)


preview_section(
    "Daily Monitor",
    daily_monitor_df,
)


preview_section(
    "Risk Summary",
    risk_df,
)


preview_section(
    "Execution Summary",
    execution_df,
)

# =============================================================================
# Quick Navigation
# =============================================================================

st.subheader(
    "Quick Navigation"
)

nav1, nav2, nav3 = st.columns(3)

with nav1:

    st.info(
        """
📁 **Portfolio**

View portfolio summary,
allocation and holdings.
"""
    )

    st.info(
        """
📈 **Daily Monitor**

Today's scanner output,
signals and opportunities.
"""
    )

with nav2:

    st.info(
        """
🛡️ **Risk**

Portfolio risk,
drawdown and exposure.
"""
    )

    st.info(
        """
📊 **Performance**

Performance metrics,
returns and attribution.
"""
    )

with nav3:

    st.info(
        """
⚙️ **Execution**

Execution summary
and trade history.
"""
    )

    st.info(
        """
📥 **Downloads**

Export generated
workflow reports.
"""
    )

st.divider()

# =============================================================================
# Footer
# =============================================================================

st.caption(
    "Institutional Scanner Monitor"
)

st.caption(
    "Executive reporting dashboard "
    "for workflow-generated reports."
)