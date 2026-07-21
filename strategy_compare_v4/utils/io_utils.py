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
• File validation

=============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

# ============================================================
# Constants
# ============================================================

DEFAULT_PATTERN = "*"

CSV_PATTERN = "**/*.csv"

STATISTICS_PATTERN = "**/*Statistics.xlsx"

DEFAULT_SHEET_NAME = "Sheet1"

MAX_SHEET_NAME = 31


# ============================================================
# Directory Utilities
# ============================================================


def ensure_directory(
    path: str | Path,
) -> Path:
    """
    Create a directory if required.
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
    Return True if file exists.
    """

    return Path(path).is_file()


def directory_exists(
    path: str | Path,
) -> bool:
    """
    Return True if directory exists.
    """

    return Path(path).is_dir()


# ============================================================
# Validation
# ============================================================


def validate_file(
    path: str | Path,
) -> Path:
    """
    Validate file existence.
    """

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return path


def validate_directory(
    path: str | Path,
) -> Path:
    """
    Validate directory existence.
    """

    path = Path(path)

    if not path.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")

    return path


# ============================================================
# Reading Files
# ============================================================


def read_csv(
    file_path: str | Path,
    allow_empty: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Read CSV file.
    """

    file_path = validate_file(
        file_path,
    )

    dataframe = pd.read_csv(
        file_path,
        **kwargs,
    )

    if dataframe.empty and not allow_empty:
        raise ValueError(f"{file_path.name} is empty.")

    return dataframe


def read_excel(
    file_path: str | Path,
    sheet_name: str | int = 0,
    allow_empty: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Read Excel worksheet.
    """

    file_path = validate_file(
        file_path,
    )

    dataframe = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        **kwargs,
    )

    if dataframe.empty and not allow_empty:
        raise ValueError(f"{file_path.name} is empty.")

    return dataframe


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
    Export DataFrame to CSV.
    """

    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise TypeError("Expected pandas DataFrame.")

    file_path = Path(
        file_path,
    )

    ensure_directory(
        file_path.parent,
    )

    df.to_csv(
        file_path,
        index=index,
        **kwargs,
    )


def write_excel(
    data: pd.DataFrame | dict[str, pd.DataFrame],
    file_path: str | Path,
    sheet_name: str = DEFAULT_SHEET_NAME,
    index: bool = False,
    **kwargs: Any,
) -> None:
    """
    Export DataFrame(s)
    to Excel workbook.
    """

    file_path = Path(
        file_path,
    )

    ensure_directory(
        file_path.parent,
    )

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl",
    ) as writer:
        # --------------------------------------
        # Multiple Worksheets
        # --------------------------------------

        if isinstance(
            data,
            dict,
        ):
            written = set()

            exported = False

            for name, dataframe in data.items():
                if (
                    dataframe is None
                    or not isinstance(
                        dataframe,
                        pd.DataFrame,
                    )
                    or dataframe.empty
                ):
                    continue

                sheet = str(name)[:MAX_SHEET_NAME]

                counter = 1

                while sheet in written:
                    suffix = f"_{counter}"

                    sheet = sheet[: MAX_SHEET_NAME - len(suffix)] + suffix

                    counter += 1

                written.add(
                    sheet,
                )

                dataframe.to_excel(
                    writer,
                    sheet_name=sheet,
                    index=index,
                    **kwargs,
                )

                exported = True

            if not exported:
                pd.DataFrame({"Status": ["No Data"]}).to_excel(
                    writer,
                    sheet_name="Summary",
                    index=False,
                )

        # --------------------------------------
        # Single Worksheet
        # --------------------------------------

        elif isinstance(
            data,
            pd.DataFrame,
        ):
            data.to_excel(
                writer,
                sheet_name=sheet_name[:MAX_SHEET_NAME],
                index=index,
                **kwargs,
            )

        else:
            raise TypeError("Expected a DataFrame or a dictionary of DataFrames.")


# ============================================================
# File Discovery
# ============================================================


def list_files(
    directory: str | Path,
    pattern: str = DEFAULT_PATTERN,
    recursive: bool = False,
) -> list[Path]:
    """
    Return files matching
    a pattern.
    """

    directory = validate_directory(
        directory,
    )

    files = directory.rglob(pattern) if recursive else directory.glob(pattern)

    return sorted(path for path in files if path.is_file())


def list_directories(
    directory: str | Path,
) -> list[Path]:
    """
    Return immediate
    sub-directories.
    """

    directory = validate_directory(
        directory,
    )

    return sorted(path for path in directory.iterdir() if path.is_dir())


def find_statistics_files(
    directory: str | Path,
) -> list[Path]:
    """
    Locate Statistics
    workbooks.
    """

    directory = validate_directory(
        directory,
    )

    return sorted(
        directory.glob(
            STATISTICS_PATTERN,
        )
    )


def find_backtest_files(
    directory: str | Path,
) -> list[Path]:
    """
    Locate backtest
    CSV files.
    """

    directory = validate_directory(
        directory,
    )

    return sorted(
        directory.glob(
            CSV_PATTERN,
        )
    )


# ============================================================
# Path Utilities
# ============================================================


def file_stem(
    file_path: str | Path,
) -> str:
    """
    Filename without extension.
    """

    return Path(
        file_path,
    ).stem


def file_name(
    file_path: str | Path,
) -> str:
    """
    Filename including extension.
    """

    return Path(
        file_path,
    ).name


def resolve_path(
    *parts: str | Path,
) -> Path:
    """
    Build an absolute path.
    """

    return Path(
        *parts,
    ).resolve(
        strict=False,
    )


def relative_path(
    path: str | Path,
    start: str | Path = ".",
) -> Path:
    """
    Return relative path.
    """

    return Path(
        path,
    ).relative_to(
        Path(start),
    )


# ============================================================
# Convenience Utilities
# ============================================================


def latest_file(
    directory: str | Path,
    pattern: str = DEFAULT_PATTERN,
) -> Path | None:
    """
    Return the most recently
    modified file.
    """

    files = list_files(
        directory,
        pattern=pattern,
        recursive=True,
    )

    if not files:
        return None

    return max(
        files,
        key=lambda x: x.stat().st_mtime,
    )


def latest_directory(
    directory: str | Path,
) -> Path | None:
    """
    Return the most recently
    modified directory.
    """

    directories = list_directories(
        directory,
    )

    if not directories:
        return None

    return max(
        directories,
        key=lambda x: x.stat().st_mtime,
    )


def unique_filename(
    file_path: str | Path,
) -> Path:
    """
    Generate a unique filename
    if the file already exists.
    """

    file_path = Path(
        file_path,
    )

    if not file_path.exists():
        return file_path

    stem = file_path.stem

    suffix = file_path.suffix

    parent = file_path.parent

    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "ensure_directory",
    "file_exists",
    "directory_exists",
    "validate_file",
    "validate_directory",
    "read_csv",
    "read_excel",
    "write_csv",
    "write_excel",
    "list_files",
    "list_directories",
    "find_statistics_files",
    "find_backtest_files",
    "file_stem",
    "file_name",
    "resolve_path",
    "relative_path",
    "latest_file",
    "latest_directory",
    "unique_filename",
]
