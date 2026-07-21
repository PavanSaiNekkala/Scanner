"""
Strategies Dashboard
====================

Institutional Strategy Analytics Dashboard
"""

from __future__ import annotations

import streamlit as st
from components.cards import strategy_summary_card
from components.charts import (
    bar_chart,
    dataframe,
    histogram,
    radar_chart,
)
from services.loader import get_sheet
from themes import apply_theme

st.set_page_config(
    page_title="Strategies",
    page_icon="📈",
    layout="wide",
)
apply_theme()

st.set_page_config(
    page_title="Strategy Analytics",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Strategy Analytics")

st.caption("Institutional comparison of all trading strategies.")

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

if not st.session_state.get(
    "reports_loaded",
    False,
):
    st.warning("Please load reports from the Data Load page.")
    st.stop()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

strategy_df = get_sheet(
    st.session_state.strategy_report,
    "Strategy Ranking",
)

if strategy_df.empty:
    st.error("Strategy Ranking sheet not found.")
    st.stop()

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

strategy_summary_card(strategy_df)

st.divider()

# ---------------------------------------------------------
# Filter
# ---------------------------------------------------------

top_n = st.slider(
    "Top Strategies",
    1,
    len(strategy_df),
    min(
        10,
        len(strategy_df),
    ),
)

filtered = (
    strategy_df.sort_values(
        "Composite Score",
        ascending=False,
    )
    .head(top_n)
    .reset_index(drop=True)
)

# ---------------------------------------------------------
# Ranking Table
# ---------------------------------------------------------

st.subheader("Strategy Ranking")

dataframe(filtered)

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

st.divider()

c1, c2 = st.columns(2)

with c1:
    bar_chart(
        filtered,
        x="Strategy Rank",
        y="Composite Score",
        title="Composite Score",
    )

with c2:
    bar_chart(
        filtered,
        x="Strategy Rank",
        y="Expectancy",
        title="Expectancy",
    )

# ---------------------------------------------------------

c1, c2 = st.columns(2)

with c1:
    histogram(
        filtered,
        "Composite Score",
        "Composite Score Distribution",
    )

with c2:
    histogram(
        filtered,
        "Profit Factor",
        "Profit Factor Distribution",
    )

# ---------------------------------------------------------
# Radar
# ---------------------------------------------------------

st.divider()

st.subheader("Strategy Radar")

selected = st.selectbox(
    "Strategy Rank",
    filtered["Strategy Rank"].tolist(),
)

row = filtered[filtered["Strategy Rank"] == selected].iloc[0]

radar_chart(
    {
        "Composite": row["Composite Score"],
        "Expectancy": row["Expectancy"],
        "Profit Factor": row["Profit Factor"],
        "Reward Risk": row["Reward Risk"],
        "Trades": row["Trades"],
    },
    str(selected),
)

# ---------------------------------------------------------
# Details
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

csv = filtered.to_csv(
    index=False,
)

st.download_button(
    label="📥 Download Strategy Ranking",
    data=csv,
    file_name="strategy_ranking.csv",
    mime="text/csv",
)
