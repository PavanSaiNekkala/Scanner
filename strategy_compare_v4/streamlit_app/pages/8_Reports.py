"""
Reports Dashboard
=================

Institutional Report Center
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from components.charts import dataframe
from services.loader import get_sheet
from themes import apply_theme

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
)

apply_theme()


# ============================================================
# Constants
# ============================================================

PAGE_TITLE = "📄 Institutional Report Center"

PAGE_CAPTION = "Browse, preview and download generated reports."


WORKBOOK_FILES = {
    "Strategy Comparison": "Strategy_Comparison.xlsx",
    "Stock Comparison": "Stock_Comparison.xlsx",
    "Leaderboards": "Leaderboards.xlsx",
    "Correlation": "Correlation.xlsx",
    "Robustness": "Robustness.xlsx",
    "Portfolio": "Institutional_Portfolio.xlsx",
    "Institutional Final Report": "Institutional_Strategy_Report.xlsx",
}


# ============================================================
# Header
# ============================================================


def render_header() -> None:
    """
    Render page header.
    """

    st.title(PAGE_TITLE)

    st.caption(PAGE_CAPTION)

    st.divider()


# ============================================================
# Validation
# ============================================================


def validate_session() -> None:
    """
    Validate loaded reports.
    """

    if not st.session_state.get(
        "reports_loaded",
        False,
    ):
        st.warning("Please load reports from the Data Load page.")

        st.stop()


# ============================================================
# Workbook Loader
# ============================================================


def get_workbooks() -> dict:
    """
    Return available workbooks.
    """

    return {
        "Strategy Comparison": st.session_state.strategy_report,
        "Stock Comparison": st.session_state.stock_report,
        "Leaderboards": st.session_state.leaderboard_report,
        "Correlation": st.session_state.correlation_report,
        "Robustness": st.session_state.robustness_report,
        "Portfolio": st.session_state.portfolio_report,
        "Institutional Final Report": st.session_state.final_report,
    }


# ============================================================
# Workbook Selector
# ============================================================


def render_selector(
    workbooks: dict,
) -> tuple[str, str, pd.DataFrame]:
    """
    Select workbook and worksheet.
    """

    left, right = st.columns(
        [1, 2],
    )

    with left:
        workbook = st.selectbox(
            "Workbook",
            list(workbooks.keys()),
        )

    with right:
        sheets = list(workbooks[workbook].keys())

        sheet = st.selectbox(
            "Worksheet",
            sheets,
        )

    df = get_sheet(
        workbooks[workbook],
        sheet,
    )

    return workbook, sheet, df


# ============================================================
# Dataset Information
# ============================================================


def render_information(
    df: pd.DataFrame,
) -> None:
    """
    Render dataframe statistics.
    """

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
            df.memory_usage(
                deep=True,
            ).sum()
            / 1024,
            2,
        )

        st.metric(
            "Memory (KB)",
            memory,
        )


# ============================================================
# Preview
# ============================================================


def render_preview(
    df: pd.DataFrame,
) -> None:
    """
    Preview dataframe.
    """

    st.divider()

    st.subheader("Preview")

    dataframe(
        df,
    )


# ============================================================
# Column Explorer
# ============================================================


def render_columns(
    df: pd.DataFrame,
) -> None:
    """
    Display column information.
    """

    st.divider()

    st.subheader("Column Information")

    info = pd.DataFrame(
        {
            "Column": df.columns,
            "Datatype": df.dtypes.astype(str),
            "Missing Values": df.isna().sum().values,
            "Unique Values": df.nunique().values,
        }
    )

    st.dataframe(
        info,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Statistics
# ============================================================


def render_statistics(
    df: pd.DataFrame,
) -> None:
    """
    Display numerical statistics.
    """

    numeric = df.select_dtypes(
        include="number",
    )

    if numeric.empty:
        return

    st.divider()

    st.subheader("Descriptive Statistics")

    st.dataframe(
        numeric.describe().T,
        use_container_width=True,
    )


# ============================================================
# Search
# ============================================================


def render_search(
    df: pd.DataFrame,
) -> None:
    """
    Search dataframe rows.
    """

    st.divider()

    search = st.text_input(
        "Search",
    )

    if not search:
        return

    mask = (
        df.astype(str)
        .apply(
            lambda column: column.str.contains(
                search,
                case=False,
                na=False,
            )
        )
        .any(axis=1)
    )

    filtered = df[mask]

    st.subheader("Search Results")

    dataframe(
        filtered,
    )


# ============================================================
# Downloads
# ============================================================


def render_downloads(
    workbook: str,
    sheet: str,
    df: pd.DataFrame,
) -> None:
    """
    Render download buttons.
    """

    st.divider()

    st.download_button(
        label="📥 Download Current Sheet",
        data=df.to_csv(index=False),
        file_name=f"{sheet}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    output_folder = Path(st.session_state.output_folder)

    excel_file = output_folder / WORKBOOK_FILES[workbook]

    if excel_file.exists():
        with open(
            excel_file,
            "rb",
        ) as file:
            st.download_button(
                label="📥 Download Excel Workbook",
                data=file,
                file_name=excel_file.name,
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )


# ============================================================
# Report Summary
# ============================================================


def render_report_summary(
    workbooks: dict,
) -> None:
    """
    Display report availability.
    """

    st.divider()

    st.subheader("Available Reports")

    summary = []

    for name, workbook in workbooks.items():
        summary.append(
            {
                "Workbook": name,
                "Sheets": len(workbook),
                "Status": "Loaded",
            }
        )

    st.dataframe(
        pd.DataFrame(summary),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Render report center.
    """

    render_header()

    validate_session()

    workbooks = get_workbooks()

    workbook, sheet, df = render_selector(
        workbooks,
    )

    if df.empty:
        st.warning("Selected worksheet contains no data.")

        return

    render_information(
        df,
    )

    render_preview(
        df,
    )

    render_columns(
        df,
    )

    render_statistics(
        df,
    )

    render_search(
        df,
    )

    render_downloads(
        workbook,
        sheet,
        df,
    )

    render_report_summary(
        workbooks,
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()

else:
    main()
