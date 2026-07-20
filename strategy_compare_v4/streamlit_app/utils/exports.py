"""
exports.py
==========

Export helpers.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_csv(
    df: pd.DataFrame,
    filename,
):
    """
    Export DataFrame to CSV.
    """

    Path(filename).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        filename,
        index=False,
    )


def export_excel(
    sheets: dict,
    filename,
):
    """
    Export multiple DataFrames
    into one workbook.
    """

    Path(filename).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(filename) as writer:
        for sheet, df in sheets.items():
            df.to_excel(
                writer,
                sheet_name=sheet,
                index=False,
            )


def dataframe_to_bytes(
    df: pd.DataFrame,
) -> bytes:
    """
    Convert DataFrame into CSV bytes
    for Streamlit downloads.
    """

    csv = df.to_csv(index=False)

    return csv.encode("utf-8")
