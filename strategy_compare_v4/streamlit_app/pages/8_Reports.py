"""
Reports Dashboard
=================

Institutional Report Center
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from components.charts import dataframe
from services.loader import get_sheet
from themes import apply_theme

st.set_page_config(
    page_title="Strategies",
    page_icon="📈",
    layout="wide",
)
apply_theme()

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Institutional Report Center")

st.caption("Browse, preview and download generated reports.")

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

if not st.session_state.get("reports_loaded", False):
    st.warning("Please load reports from the Data Load page.")

    st.stop()

# ---------------------------------------------------------
# Workbook Dictionary
# ---------------------------------------------------------

workbooks = {
    "Strategy Comparison": st.session_state.strategy_report,
    "Stock Comparison": st.session_state.stock_report,
    "Leaderboards": st.session_state.leaderboard_report,
    "Correlation": st.session_state.correlation_report,
    "Robustness": st.session_state.robustness_report,
    "Portfolio": st.session_state.portfolio_report,
    "Institutional Final Report": st.session_state.final_report,
}

# ---------------------------------------------------------
# Workbook Selection
# ---------------------------------------------------------

left, right = st.columns([1, 2])

with left:
    workbook = st.selectbox(
        "Workbook",
        list(workbooks.keys()),
    )

with right:
    sheet = st.selectbox(
        "Worksheet",
        list(workbooks[workbook].keys()),
    )

df = get_sheet(
    workbooks[workbook],
    sheet,
)

# ---------------------------------------------------------
# Information
# ---------------------------------------------------------

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Rows",
        len(df),
    )

with c2:
    st.metric(
        "Columns",
        len(df.columns),
    )

with c3:
    memory = round(
        df.memory_usage(deep=True).sum() / 1024,
        2,
    )

    st.metric(
        "Memory (KB)",
        memory,
    )

# ---------------------------------------------------------
# Preview
# ---------------------------------------------------------

st.divider()

st.subheader("Preview")

dataframe(df)

# ---------------------------------------------------------
# Column Explorer
# ---------------------------------------------------------

st.divider()

st.subheader("Column Information")

info = {
    "Column": df.columns,
    "Datatype": df.dtypes.astype(str),
    "Missing Values": df.isna().sum().values,
    "Unique Values": df.nunique().values,
}

st.dataframe(
    info,
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------
# Numeric Summary
# ---------------------------------------------------------

numeric = df.select_dtypes(include="number")

if not numeric.empty:
    st.divider()

    st.subheader("Descriptive Statistics")

    st.dataframe(
        numeric.describe().T,
        use_container_width=True,
    )

# ---------------------------------------------------------
# Search
# ---------------------------------------------------------

st.divider()

search = st.text_input(
    "Search",
)

if search:
    filtered = df[
        df.astype(str)
        .apply(
            lambda x: x.str.contains(
                search,
                case=False,
                na=False,
            )
        )
        .any(axis=1)
    ]

    st.subheader("Search Results")

    dataframe(filtered)

# ---------------------------------------------------------
# Downloads
# ---------------------------------------------------------

st.divider()

csv = df.to_csv(index=False)

st.download_button(
    "📥 Download Current Sheet",
    csv,
    f"{sheet}.csv",
    "text/csv",
)

# ---------------------------------------------------------
# Download Excel Workbook
# ---------------------------------------------------------

output_folder = Path(st.session_state.output_folder)

mapping = {
    "Strategy Comparison": "Strategy_Comparison.xlsx",
    "Stock Comparison": "Stock_Comparison.xlsx",
    "Leaderboards": "Leaderboards.xlsx",
    "Correlation": "Correlation.xlsx",
    "Robustness": "Robustness.xlsx",
    "Portfolio": "Institutional_Portfolio.xlsx",
    "Institutional Final Report": "Institutional_Strategy_Report.xlsx",
}

excel_file = output_folder / mapping[workbook]

if excel_file.exists():
    with open(
        excel_file,
        "rb",
    ) as f:
        st.download_button(
            "📥 Download Excel Workbook",
            data=f,
            file_name=excel_file.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# ---------------------------------------------------------
# Report Summary
# ---------------------------------------------------------

st.divider()

st.subheader("Available Reports")

summary = []

for name, wb in workbooks.items():
    summary.append(
        {
            "Workbook": name,
            "Sheets": len(wb),
            "Status": "Loaded",
        }
    )

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True,
)
