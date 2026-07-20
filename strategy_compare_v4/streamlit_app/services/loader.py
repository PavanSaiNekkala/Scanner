"""
loader.py
=========

Centralized data loading service for the
Institutional Strategy Comparison Platform.

Loads generated Excel reports into Streamlit
Session State.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

# -------------------------------------------------------
# Cache Excel Reads
# -------------------------------------------------------


@st.cache_data(show_spinner=False)
def load_excel(file: Path) -> dict[str, pd.DataFrame]:
    """
    Load every sheet from an Excel workbook.
    """

    if not file.exists():
        raise FileNotFoundError(file)

    xls = pd.ExcelFile(file)

    sheets = {}

    for sheet in xls.sheet_names:
        sheets[sheet] = pd.read_excel(
            xls,
            sheet_name=sheet,
        )

    return {str(k): v for k, v in sheets.items()}


# -------------------------------------------------------
# Cache CSV Reads
# -------------------------------------------------------


@st.cache_data(show_spinner=False)
def load_csv(file: Path) -> pd.DataFrame:
    """
    Read CSV file.
    """

    if not file.exists():
        raise FileNotFoundError(file)

    return pd.read_csv(file)


# -------------------------------------------------------
# Output Folder Validation
# -------------------------------------------------------


def validate_output_folder(
    folder: Path,
) -> bool:
    """
    Verify required reports exist.
    """

    required = [
        "Strategy_Comparison.xlsx",
        "Stock_Comparison.xlsx",
        "Leaderboards.xlsx",
        "Correlation.xlsx",
        "Robustness.xlsx",
        "Institutional_Portfolio.xlsx",
        "Institutional_Strategy_Report.xlsx",
    ]

    return all((folder / report).exists() for report in required)


# -------------------------------------------------------
# Load All Reports
# -------------------------------------------------------


def load_reports(
    output_folder: str,
):
    """
    Load all generated reports.
    """

    folder = Path(output_folder)

    if not validate_output_folder(folder):
        raise FileNotFoundError("Required reports missing.")

    st.session_state.strategy_report = load_excel(folder / "Strategy_Comparison.xlsx")

    st.session_state.stock_report = load_excel(folder / "Stock_Comparison.xlsx")

    st.session_state.leaderboard_report = load_excel(folder / "Leaderboards.xlsx")

    st.session_state.correlation_report = load_excel(folder / "Correlation.xlsx")

    st.session_state.robustness_report = load_excel(folder / "Robustness.xlsx")

    st.session_state.portfolio_report = load_excel(
        folder / "Institutional_Portfolio.xlsx"
    )

    st.session_state.final_report = load_excel(
        folder / "Institutional_Strategy_Report.xlsx"
    )

    st.session_state.output_folder = str(folder)

    st.session_state.reports_loaded = True


# -------------------------------------------------------
# Get Single Sheet
# -------------------------------------------------------


def get_sheet(
    workbook: dict,
    sheet: str,
) -> pd.DataFrame:
    """
    Safely return a sheet.
    """

    if workbook is None:
        return pd.DataFrame()

    return workbook.get(
        sheet,
        pd.DataFrame(),
    )


# -------------------------------------------------------
# Reset Session
# -------------------------------------------------------


def clear_session():
    """
    Reset loaded reports.
    """

    keys = [
        "strategy_report",
        "stock_report",
        "leaderboard_report",
        "correlation_report",
        "robustness_report",
        "portfolio_report",
        "final_report",
        "reports_loaded",
        "output_folder",
    ]

    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


# -------------------------------------------------------
# Report Summary
# -------------------------------------------------------


def report_summary() -> dict:
    """
    Returns information about loaded reports.
    """

    return {
        "Loaded": st.session_state.get(
            "reports_loaded",
            False,
        ),
        "Output Folder": st.session_state.get(
            "output_folder",
            "Not Loaded",
        ),
    }
