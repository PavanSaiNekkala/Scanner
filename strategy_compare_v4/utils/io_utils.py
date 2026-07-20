"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
utils/io_utils.py

Purpose
-------
Common file and directory utilities used across the
Institutional Strategy Comparison Platform.

Provides
--------
• Directory management
• File discovery
• CSV / Excel I/O
• Path utilities

=============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

# ============================================================
# Directory Utilities
# ============================================================


def ensure_directory(
    path: str | Path,
) -> Path:
    """
    Create a directory if it does not already exist.
    """

    directory = Path(path)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def file_exists(
    path: str | Path,
) -> bool:
    """
    Return True if the file exists.
    """

    return Path(path).is_file()


def directory_exists(
    path: str | Path,
) -> bool:
    """
    Return True if the directory exists.
    """

    return Path(path).is_dir()


# ============================================================
# Reading Files
# ============================================================


def read_csv(
    file_path: str | Path,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Read a CSV file.
    """

    return pd.read_csv(file_path, **kwargs)


def read_excel(
    file_path: str | Path,
    sheet_name: str | int = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Read an Excel worksheet.
    """

    return pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        **kwargs,
    )


# ============================================================
# Writing Files
# ============================================================


def write_csv(
    df: pd.DataFrame,
    file_path: str | Path,
    index: bool = False,
    **kwargs: Any,
) -> None:
    """
    Export a DataFrame to CSV.
    """

    file_path = Path(file_path)

    ensure_directory(file_path.parent)

    df.to_csv(
        file_path,
        index=index,
        **kwargs,
    )


def write_excel(
    data: pd.DataFrame | dict[str, pd.DataFrame],
    file_path: str | Path,
    sheet_name: str = "Sheet1",
    index: bool = False,
    **kwargs: Any,
) -> None:
    """
    Export either:

    • A single DataFrame
    • A dictionary of DataFrames
      {sheet_name: dataframe}

    to an Excel workbook.
    """

    file_path = Path(file_path)

    ensure_directory(file_path.parent)

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl",
    ) as writer:
        # -------------------------------
        # Multiple worksheets
        # -------------------------------

        if isinstance(
            data,
            dict,
        ):
            written = False

            for name, df in data.items():
                if df is None or not isinstance(df, pd.DataFrame) or df.empty:
                    continue

                df.to_excel(
                    writer,
                    sheet_name=str(name)[:31],
                    index=index,
                    **kwargs,
                )

                written = True

            if not written:
                pd.DataFrame({"Status": ["No Data"]}).to_excel(
                    writer,
                    sheet_name="Summary",
                    index=False,
                )
        # -------------------------------
        # Single worksheet
        # -------------------------------

        else:
            data.to_excel(
                writer,
                sheet_name=sheet_name,
                index=index,
                **kwargs,
            )


# ============================================================
# File Discovery
# ============================================================


def list_files(
    directory: str | Path,
    pattern: str = "*",
) -> list[Path]:
    """
    Return files matching a pattern.
    """

    return sorted(Path(directory).glob(pattern))


def list_directories(
    directory: str | Path,
) -> list[Path]:
    """
    Return all immediate sub-directories.
    """

    return sorted(path for path in Path(directory).iterdir() if path.is_dir())


def find_statistics_files(
    directory: str | Path,
) -> list[Path]:
    """
    Return all statistics workbooks.
    """

    return sorted(Path(directory).glob("**/*Statistics.xlsx"))


def find_backtest_files(
    directory: str | Path,
) -> list[Path]:
    """
    Return all backtest CSV files.
    """

    return sorted(Path(directory).glob("**/*.csv"))


# ============================================================
# Path Utilities
# ============================================================


def file_stem(
    file_path: str | Path,
) -> str:
    """
    Return filename without extension.
    """

    return Path(file_path).stem


def file_name(
    file_path: str | Path,
) -> str:
    """
    Return filename including extension.
    """

    return Path(file_path).name


def resolve_path(
    *parts: str | Path,
) -> Path:
    """
    Build an absolute path.
    """

    return Path(*parts).resolve()


def relative_path(
    path: str | Path,
    start: str | Path = ".",
) -> Path:
    """
    Return the relative path.
    """

    return Path(path).relative_to(Path(start))
