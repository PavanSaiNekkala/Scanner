"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    utils/io_utils.py

Purpose:
    Common input/output utilities.

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


###############################################################################
# Directory
###############################################################################

def ensure_directory(path):
    """
    Create directory if it does not exist.
    """

    path = Path(path)

    path.mkdir(

        parents=True,

        exist_ok=True

    )

    return path


###############################################################################
# File Exists
###############################################################################

def file_exists(path):
    """
    Check whether file exists.
    """

    return Path(path).is_file()


###############################################################################
# Directory Exists
###############################################################################

def directory_exists(path):
    """
    Check whether directory exists.
    """

    return Path(path).is_dir()


###############################################################################
# Read CSV
###############################################################################

def read_csv(

    file_path,

    **kwargs

):
    """
    Read CSV file.
    """

    return pd.read_csv(

        file_path,

        **kwargs

    )


###############################################################################
# Read Excel
###############################################################################

def read_excel(

    file_path,

    sheet_name=0,

    **kwargs

):
    """
    Read Excel worksheet.
    """

    return pd.read_excel(

        file_path,

        sheet_name=sheet_name,

        **kwargs

    )


###############################################################################
# Write CSV
###############################################################################

def write_csv(

    df,

    file_path,

    index=False,

    **kwargs

):
    """
    Export dataframe to CSV.
    """

    df.to_csv(

        file_path,

        index=index,

        **kwargs

    )


###############################################################################
# Write Excel
###############################################################################

def write_excel(

    df,

    file_path,

    sheet_name="Sheet1",

    index=False,

    **kwargs

):
    """
    Export dataframe to Excel.
    """

    with pd.ExcelWriter(

        file_path,

        engine="openpyxl"

    ) as writer:

        df.to_excel(

            writer,

            sheet_name=sheet_name,

            index=index,

            **kwargs

        )


###############################################################################
# List Files
###############################################################################

def list_files(

    directory,

    pattern="*"

):
    """
    List files matching pattern.
    """

    return sorted(

        Path(directory).glob(pattern)

    )


###############################################################################
# List Directories
###############################################################################

def list_directories(

    directory

):
    """
    Return sub-directories.
    """

    return sorted(

        [

            p

            for p in Path(directory).iterdir()

            if p.is_dir()

        ]

    )


###############################################################################
# Find Statistics Files
###############################################################################

def find_statistics_files(

    directory

):
    """
    Find strategy statistics workbooks.
    """

    return sorted(

        Path(directory).glob(

            "**/*Statistics.xlsx"

        )

    )


###############################################################################
# Find Backtest CSV Files
###############################################################################

def find_backtest_files(

    directory

):
    """
    Find all backtest CSV files.
    """

    return sorted(

        Path(directory).glob(

            "**/*.csv"

        )

    )


###############################################################################
# File Stem
###############################################################################

def file_stem(

    file_path

):
    """
    Filename without extension.
    """

    return Path(

        file_path

    ).stem


###############################################################################
# File Name
###############################################################################

def file_name(

    file_path

):
    """
    Filename with extension.
    """

    return Path(

        file_path

    ).name


###############################################################################
# Resolve Path
###############################################################################

def resolve_path(

    *parts

):
    """
    Build absolute path.
    """

    return Path(

        *parts

    ).resolve()


###############################################################################
# Relative Path
###############################################################################

def relative_path(

    path,

    start="."

):
    """
    Return relative path.
    """

    return Path(

        path

    ).relative_to(

        Path(start)

    )