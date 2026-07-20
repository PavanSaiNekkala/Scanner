"""
Strategies Dashboard
====================

Institutional Strategy Analytics Dashboard
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
    page_title="Strategy Analytics",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Strategy Analytics")

st.caption("Institutional comparison of all trading strategies.")

# ---------------------------------------------------------
# Check Reports
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports from the Data Load page.")

    st.stop()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

strategy_df = get_sheet(
    st.session_state.strategy_report,
    "Strategy Rankings",
)

if strategy_df.empty:
    st.error("Strategy Rankings sheet not found.")

    st.stop()

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

strategy_summary_card(strategy_df)

st.divider()

# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

left, right = st.columns(2)

with left:
    recommendations = sorted(strategy_df["Recommendation"].dropna().unique().tolist())

    recommendation = st.selectbox(
        "Recommendation",
        ["All"] + recommendations,
    )

with right:
    top_n = st.slider(
        "Top Strategies",
        5,
        100,
        20,
    )

filtered = strategy_df.copy()

if recommendation != "All":
    filtered = filtered[filtered["Recommendation"] == recommendation]

filtered = filtered.sort_values(
    "Composite Score",
    ascending=False,
).head(top_n)

st.divider()

# ---------------------------------------------------------
# Rankings
# ---------------------------------------------------------

st.subheader("Strategy Rankings")

dataframe(filtered)

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

st.divider()

col1, col2 = st.columns(2)

with col1:
    bar_chart(
        filtered,
        x="Strategy",
        y="Composite Score",
        color="Recommendation",
        title="Composite Score",
    )

with col2:
    bar_chart(
        filtered,
        x="Strategy",
        y="Edge Score",
        color="Recommendation",
        title="Edge Score",
    )

# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    scatter_chart(
        filtered,
        x="Reliability Score",
        y="Efficiency Score",
        color="Recommendation",
        hover="Strategy",
        title="Reliability vs Efficiency",
    )

with col2:
    histogram(
        filtered,
        "Composite Score",
        "Composite Score Distribution",
    )

# ---------------------------------------------------------

st.divider()

recommendation_chart(filtered)

# ---------------------------------------------------------
# Radar Chart
# ---------------------------------------------------------

st.divider()

st.subheader("Strategy Score Radar")

selected = st.selectbox(
    "Select Strategy",
    filtered["Strategy"].tolist(),
)

row = filtered[filtered["Strategy"] == selected].iloc[0]

radar_chart(
    {
        "Composite": row["Composite Score"],
        "Edge": row["Edge Score"],
        "Reliability": row["Reliability Score"],
        "Efficiency": row["Efficiency Score"],
        "Risk": row.get("Risk Score", 0),
        "Return": row.get("Return Score", 0),
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
# Strategy Details
# ---------------------------------------------------------

st.divider()

st.subheader("Strategy Details")

st.dataframe(
    row.to_frame().T,
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = filtered.to_csv(index=False)

st.download_button(
    label="📥 Download Filtered Strategies",
    data=csv,
    file_name="strategy_rankings.csv",
    mime="text/csv",
)
