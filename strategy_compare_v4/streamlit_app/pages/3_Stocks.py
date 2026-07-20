"""
Stocks Dashboard
================

Institutional Stock Analytics Dashboard
"""

from __future__ import annotations

import streamlit as st
from components.cards import (
    recommendation_badge,
    strategy_summary_card,
)
from components.charts import (
    bar_chart,
    dataframe,
    histogram,
    radar_chart,
    recommendation_chart,
    scatter_chart,
)
from services.loader import get_sheet

st.set_page_config(
    page_title="Stock Analytics",
    page_icon="🏢",
    layout="wide",
)

st.title("🏢 Institutional Stock Analytics")

st.caption("Institutional ranking and analysis of all stocks.")

# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports first.")

    st.stop()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

stock_df = get_sheet(
    st.session_state.stock_report,
    "Stock Rankings",
)

if stock_df.empty:
    st.error("Stock Rankings sheet not found.")

    st.stop()

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

strategy_summary_card(stock_df)

st.divider()

# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

left, center, right = st.columns(3)

with left:
    recommendation = st.selectbox(
        "Recommendation", ["All"] + sorted(stock_df["Recommendation"].dropna().unique())
    )

with center:
    top_n = st.slider(
        "Top Stocks",
        5,
        200,
        25,
    )

with right:
    search = st.text_input(
        "Search Stock",
        "",
    )

filtered = stock_df.copy()

if recommendation != "All":
    filtered = filtered[filtered["Recommendation"] == recommendation]

if search:
    filtered = filtered[
        filtered["Stock"].str.contains(
            search,
            case=False,
            na=False,
        )
    ]

filtered = filtered.sort_values(
    "Institutional Score",
    ascending=False,
).head(top_n)

# ---------------------------------------------------------
# Table
# ---------------------------------------------------------

st.subheader("Stock Rankings")

dataframe(filtered)

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

st.divider()

c1, c2 = st.columns(2)

with c1:
    bar_chart(
        filtered,
        x="Stock",
        y="Institutional Score",
        color="Recommendation",
        title="Institutional Score",
    )

with c2:
    bar_chart(
        filtered,
        x="Stock",
        y="Edge Score",
        color="Recommendation",
        title="Edge Score",
    )

# ---------------------------------------------------------

c1, c2 = st.columns(2)

with c1:
    scatter_chart(
        filtered,
        x="Reliability Score",
        y="Efficiency Score",
        color="Recommendation",
        hover="Stock",
        title="Reliability vs Efficiency",
    )

with c2:
    histogram(
        filtered,
        "Institutional Score",
        "Institutional Score Distribution",
    )

# ---------------------------------------------------------

st.divider()

recommendation_chart(filtered)

# ---------------------------------------------------------
# Radar
# ---------------------------------------------------------

st.divider()

st.subheader("Stock Radar")

selected = st.selectbox(
    "Select Stock",
    filtered["Stock"].tolist(),
)

row = filtered[filtered["Stock"] == selected].iloc[0]

radar_chart(
    {
        "Institutional": row["Institutional Score"],
        "Edge": row["Edge Score"],
        "Reliability": row["Reliability Score"],
        "Efficiency": row["Efficiency Score"],
        "Risk": row.get("Risk Score", 0),
        "Return": row.get("Return Score", 0),
        "Opportunity": row.get("Opportunity Score", 0),
    },
    selected,
)

# ---------------------------------------------------------
# Recommendation
# ---------------------------------------------------------

st.divider()

st.subheader("Institutional Recommendation")

recommendation_badge(row["Recommendation"])

# ---------------------------------------------------------
# Stock Details
# ---------------------------------------------------------

st.divider()

st.subheader("Selected Stock")

st.dataframe(
    row.to_frame().T,
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------
# Key Metrics
# ---------------------------------------------------------

st.divider()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Composite",
        f"{row['Institutional Score']:.2f}",
    )

with m2:
    st.metric(
        "Edge",
        f"{row['Edge Score']:.2f}",
    )

with m3:
    st.metric(
        "Reliability",
        f"{row['Reliability Score']:.2f}",
    )

with m4:
    st.metric(
        "Efficiency",
        f"{row['Efficiency Score']:.2f}",
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = filtered.to_csv(index=False)

st.download_button(
    "📥 Download Stock Rankings",
    csv,
    "stock_rankings.csv",
    "text/csv",
)
