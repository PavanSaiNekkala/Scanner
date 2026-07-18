"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
reports/dashboard.py

Purpose
-------
Interactive Streamlit dashboard for
Institutional Strategy Comparison.

Features
--------
• KPI Dashboard
• Strategy Ranking
• Recommendation Summary
• Interactive Charts
• Portfolio Allocation
• CSV Download

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    EDGE_SCORE,
    RELIABILITY_SCORE,
    RECOMMENDATION,
)

from strategy_compare_v4.utils.helpers import (
    require_columns,
)

from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)

from reports.charts import (
    composite_score_chart,
    edge_score_chart,
    recommendation_chart,
    expectancy_profit_chart,
    reliability_efficiency_chart,
    portfolio_chart,
)

logger = get_logger(__name__)


# ============================================================
# Configure Page
# ============================================================

def configure_page():
    """
    Configure the Streamlit page.
    """

    banner(

        logger,

        "Dashboard Startup",

    )

    st.set_page_config(

        page_title="Institutional Strategy Comparison",

        page_icon="📈",

        layout="wide",

    )

    logger.info(

        "Dashboard page configured."

    )


# ============================================================
# Load Data
# ============================================================

@st.cache_data(show_spinner=False)
def load_data(
    file_path,
) -> pd.DataFrame:
    """
    Load comparison data.
    """

    file_path = Path(

        file_path,

    )

    logger.info(

        "Loading file : %s",

        file_path,

    )

    if file_path.suffix.lower() == ".csv":

        dataframe = pd.read_csv(

            file_path,

        )

    else:

        dataframe = pd.read_excel(

            file_path,

        )

    require_columns(

        dataframe,

        [

            COMPOSITE_SCORE,

            EDGE_SCORE,

            RELIABILITY_SCORE,

            RECOMMENDATION,

        ],

    )

    logger.info(

        "Loaded %d strategies.",

        len(

            dataframe,

        ),

    )

    return dataframe


# ============================================================
# KPI Cards
# ============================================================

def show_kpis(
    df: pd.DataFrame,
):
    """
    Display dashboard KPI cards.
    """

    require_columns(

        df,

        [

            COMPOSITE_SCORE,

            EDGE_SCORE,

            RELIABILITY_SCORE,

        ],

    )

    logger.info(

        "Displaying KPI cards."

    )

    c1, c2, c3, c4 = st.columns(

        4,

    )

    c1.metric(

        "Strategies",

        len(df),

    )

    c2.metric(

        "Average Composite",

        round(

            df[

                COMPOSITE_SCORE

            ].mean(),

            2,

        ),

    )

    c3.metric(

        "Average Edge",

        round(

            df[

                EDGE_SCORE

            ].mean(),

            2,

        ),

    )

    c4.metric(

        "Average Reliability",

        round(

            df[

                RELIABILITY_SCORE

            ].mean(),

            2,

        ),

    )

# ============================================================
# Recommendation Summary
# ============================================================

def show_recommendations(
    df: pd.DataFrame,
):
    """
    Display recommendation
    summary statistics.
    """

    require_columns(

        df,

        [

            RECOMMENDATION,

        ],

    )

    logger.info(

        "Displaying recommendation summary."

    )

    st.subheader(

        "Recommendation Summary",

    )

    summary = (

        df[

            RECOMMENDATION

        ]

        .value_counts()

        .rename_axis(

            RECOMMENDATION,

        )

        .reset_index(

            name="Count",

        )

    )

    st.dataframe(

        summary,

        use_container_width=True,

    )


# ============================================================
# Top Strategies
# ============================================================

def show_top_strategies(
    df: pd.DataFrame,
    top_n: int = 20,
):
    """
    Display highest-ranked
    strategies.
    """

    require_columns(

        df,

        [

            COMPOSITE_SCORE,

        ],

    )

    logger.info(

        "Displaying top %d strategies.",

        top_n,

    )

    st.subheader(

        "Top Strategies",

    )

    st.dataframe(

        df.nlargest(

            top_n,

            COMPOSITE_SCORE,

        ),

        use_container_width=True,

    )


# ============================================================
# Charts
# ============================================================

def show_charts(
    df: pd.DataFrame,
):
    """
    Display dashboard
    charts.
    """

    logger.info(

        "Rendering dashboard charts."

    )

    st.subheader(

        "Charts",

    )

    left, right = st.columns(

        2,

    )

    with left:

        st.pyplot(

            composite_score_chart(

                df,

            ),

        )

        st.pyplot(

            recommendation_chart(

                df,

            ),

        )

        st.pyplot(

            expectancy_profit_chart(

                df,

            ),

        )

    with right:

        st.pyplot(

            edge_score_chart(

                df,

            ),

        )

        st.pyplot(

            reliability_efficiency_chart(

                df,

            ),

        )


# ============================================================
# Portfolio
# ============================================================

def show_portfolio(
    portfolio_df: pd.DataFrame,
):
    """
    Display portfolio
    allocation.
    """

    logger.info(

        "Displaying portfolio allocation."

    )

    st.subheader(

        "Portfolio",

    )

    st.dataframe(

        portfolio_df,

        use_container_width=True,

    )

    st.pyplot(

        portfolio_chart(

            portfolio_df,

        ),

    )

# ============================================================
# Download Results
# ============================================================

def download_data(
    df: pd.DataFrame,
):
    """
    Provide processed
    comparison results
    for download.
    """

    logger.info(

        "Preparing CSV download."

    )

    csv_data = df.to_csv(

        index=False,

    ).encode(

        "utf-8",

    )

    st.download_button(

        label="Download CSV",

        data=csv_data,

        file_name="strategy_comparison.csv",

        mime="text/csv",

    )

    logger.info(

        "Download button rendered."

    )


# ============================================================
# Dashboard Runner
# ============================================================

def run_dashboard():
    """
    Execute the complete
    Institutional Strategy
    Comparison Dashboard.
    """

    banner(

        logger,

        "Institutional Dashboard",

    )

    configure_page()

    st.title(

        "Institutional Strategy Comparison Platform"

    )

    uploaded = st.file_uploader(

        "Upload Comparison Report",

        type=[

            "csv",

            "xlsx",

        ],

    )

    if uploaded is None:

        logger.info(

            "Waiting for user upload."

        )

        st.info(

            "Upload a comparison report to continue."

        )

        return

    try:

        df = load_data(

            uploaded,

        )

        logger.info(

            "Comparison report loaded successfully."

        )

        show_kpis(

            df,

        )

        show_recommendations(

            df,

        )

        show_top_strategies(

            df,

        )

        show_charts(

            df,

        )

        download_data(

            df,

        )

        logger.info(

            "Dashboard rendered successfully."

        )

    except Exception:

        logger.exception(

            "Dashboard execution failed."

        )

        st.error(

            "Unable to load the comparison report."

        )

        raise


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    logger.info(

        "Launching Institutional Dashboard."

    )

    run_dashboard()