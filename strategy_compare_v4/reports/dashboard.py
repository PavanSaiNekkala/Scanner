"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    reports/dashboard.py

Purpose:
    Interactive dashboard for institutional strategy
    comparison.

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from reports.charts import (
    composite_score_chart,
    edge_score_chart,
    recommendation_chart,
    expectancy_profit_chart,
    reliability_efficiency_chart,
    portfolio_chart,
)


###############################################################################
# Page Configuration
###############################################################################

def configure_page():
    """
    Configure Streamlit page.
    """

    st.set_page_config(
        page_title="Institutional Strategy Comparison",
        page_icon="📈",
        layout="wide",
    )


###############################################################################
# Load Data
###############################################################################

@st.cache_data
def load_data(file_path):
    """
    Load comparison data.
    """

    file_path = Path(file_path)

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)

    return pd.read_excel(file_path)


###############################################################################
# KPI Cards
###############################################################################

def show_kpis(df):
    """
    Display KPI summary.
    """

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Strategies",
        len(df)
    )

    c2.metric(
        "Average Composite",
        round(df["Composite Score"].mean(), 2)
    )

    c3.metric(
        "Average Edge",
        round(df["Edge Score"].mean(), 2)
    )

    c4.metric(
        "Average Reliability",
        round(df["Reliability Score"].mean(), 2)
    )


###############################################################################
# Recommendation Summary
###############################################################################

def show_recommendations(df):
    """
    Recommendation statistics.
    """

    st.subheader("Recommendation Summary")

    st.dataframe(

        df["Recommendation"]

        .value_counts()

        .rename_axis("Recommendation")

        .reset_index(name="Count"),

        use_container_width=True

    )


###############################################################################
# Top Strategies
###############################################################################

def show_top_strategies(df, top_n=20):
    """
    Display highest ranked strategies.
    """

    st.subheader("Top Strategies")

    st.dataframe(

        df.nlargest(

            top_n,

            "Composite Score"

        ),

        use_container_width=True

    )


###############################################################################
# Charts
###############################################################################

def show_charts(df):
    """
    Display all charts.
    """

    st.subheader("Charts")

    left, right = st.columns(2)

    with left:

        st.pyplot(

            composite_score_chart(df)

        )

        st.pyplot(

            recommendation_chart(df)

        )

        st.pyplot(

            expectancy_profit_chart(df)

        )

    with right:

        st.pyplot(

            edge_score_chart(df)

        )

        st.pyplot(

            reliability_efficiency_chart(df)

        )


###############################################################################
# Portfolio
###############################################################################

def show_portfolio(portfolio_df):
    """
    Portfolio allocation.
    """

    st.subheader("Portfolio")

    st.dataframe(

        portfolio_df,

        use_container_width=True

    )

    st.pyplot(

        portfolio_chart(portfolio_df)

    )


###############################################################################
# Download
###############################################################################

def download_data(df):
    """
    Download processed results.
    """

    st.download_button(

        label="Download CSV",

        data=df.to_csv(index=False),

        file_name="strategy_comparison.csv",

        mime="text/csv"

    )


###############################################################################
# Dashboard
###############################################################################

def run_dashboard():

    configure_page()

    st.title(

        "Institutional Strategy Comparison Platform"

    )

    uploaded = st.file_uploader(

        "Upload Comparison Report",

        type=[

            "csv",

            "xlsx"

        ]

    )

    if uploaded is None:

        st.info(

            "Upload a comparison report to continue."

        )

        return

    df = load_data(uploaded)

    show_kpis(df)

    show_recommendations(df)

    show_top_strategies(df)

    show_charts(df)

    download_data(df)


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":

    run_dashboard()