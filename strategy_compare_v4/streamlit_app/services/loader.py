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
from strategy_compare_v4.utils.logger import get_logger

logger = get_logger(__name__)

# ============================================================
# Report Configuration
# ============================================================

REPORT_FILES: dict[str, str] = {
    "strategy_report": "Strategy_Comparison.xlsx",
    "stock_report": "Stock_Comparison.xlsx",
    "leaderboard_report": "Leaderboards.xlsx",
    "correlation_report": "Correlation.xlsx",
    "robustness_report": "Robustness.xlsx",
    "portfolio_report": "Institutional_Portfolio.xlsx",
    "final_report": "Institutional_Strategy_Report.xlsx",
}

# ============================================================
# Cache Excel Reads
# ============================================================


@st.cache_data(show_spinner=False)
def load_excel(
    file: Path,
) -> dict[str, pd.DataFrame]:
    """
    Load every worksheet from an Excel workbook.
    """

    if not file.exists():
        raise FileNotFoundError(file)

    logger.info(
        "Loading workbook: %s",
        file.name,
    )

    xls = pd.ExcelFile(file)

    sheets = {
        str(sheet): pd.read_excel(
            xls,
            sheet_name=sheet,
        )
        for sheet in xls.sheet_names
    }

    if not sheets:
        raise ValueError(f"{file.name} contains no worksheets.")

    return sheets


# ============================================================
# Cache CSV Reads
# ============================================================


@st.cache_data(show_spinner=False)
def load_csv(
    file: Path,
) -> pd.DataFrame:
    """
    Read CSV file.
    """

    if not file.exists():
        raise FileNotFoundError(file)

    logger.info(
        "Loading CSV: %s",
        file.name,
    )

    return pd.read_csv(
        file,
        low_memory=False,
    )


# ============================================================
# Output Folder Validation
# ============================================================


def validate_output_folder(
    folder: Path,
) -> list[str]:
    """
    Return missing required report files.
    """

    return [
        report for report in REPORT_FILES.values() if not (folder / report).exists()
    ]


# ============================================================
# Load All Reports
# ============================================================


def load_reports(
    output_folder: str | Path,
) -> None:
    """
    Load all generated reports into Session State.
    """

    folder = Path(output_folder)

    missing = validate_output_folder(folder)

    if missing:
        raise FileNotFoundError("Missing required reports:\n" + "\n".join(missing))

    logger.info(
        "Loading reports from %s",
        folder,
    )

    for session_key, filename in REPORT_FILES.items():
        st.session_state[session_key] = load_excel(
            folder / filename,
        )

    st.session_state.output_folder = str(folder)

    st.session_state.reports_loaded = True

    logger.info(
        "Successfully loaded %d reports.",
        len(REPORT_FILES),
    )


# ============================================================
# Workbook Helpers
# ============================================================


def get_sheet(
    workbook: dict[str, pd.DataFrame] | None,
    sheet: str,
) -> pd.DataFrame:
    """
    Safely return a worksheet.
    """

    if workbook is None:
        return pd.DataFrame()

    return workbook.get(
        sheet,
        pd.DataFrame(),
    )


def workbook_sheets(
    workbook: dict[str, pd.DataFrame] | None,
) -> list[str]:
    """
    Return available worksheet names.
    """

    if workbook is None:
        return []

    return sorted(workbook.keys())


# ============================================================
# Session Management
# ============================================================


def clear_session() -> None:
    """
    Reset loaded reports.
    """

    for key in [
        *REPORT_FILES.keys(),
        "reports_loaded",
        "output_folder",
    ]:
        st.session_state.pop(
            key,
            None,
        )

    logger.info("Session cleared.")


# ============================================================
# Report Summary
# ============================================================


def report_summary() -> dict[str, object]:
    """
    Return current report loading status.
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
        "Reports Loaded": sum(1 for key in REPORT_FILES if key in st.session_state),
    }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "REPORT_FILES",
    "load_excel",
    "load_csv",
    "validate_output_folder",
    "load_reports",
    "get_sheet",
    "workbook_sheets",
    "clear_session",
    "report_summary",
]
