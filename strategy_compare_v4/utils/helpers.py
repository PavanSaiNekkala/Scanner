"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    utils/helpers.py

Purpose:
    Common helper functions used across the platform.

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


###############################################################################
# Column Validation
###############################################################################

def require_columns(

    df: pd.DataFrame,

    required_columns

):

    """
    Validate required dataframe columns.
    """

    missing = [

        col

        for col in required_columns

        if col not in df.columns

    ]

    if missing:

        raise ValueError(

            "Missing required columns:\n"

            +

            "\n".join(missing)

        )


###############################################################################
# DataFrame Copy
###############################################################################

def copy_dataframe(

    df: pd.DataFrame

):

    """
    Return defensive copy.
    """

    return df.copy(deep=True)


###############################################################################
# Empty DataFrame
###############################################################################

def is_empty(

    df: pd.DataFrame

):

    """
    Check dataframe is empty.
    """

    return (

        df is None

        or

        df.empty

    )


###############################################################################
# Ensure Output Directory
###############################################################################

def ensure_directory(

    directory

):

    """
    Create directory if needed.
    """

    path = Path(directory)

    path.mkdir(

        parents=True,

        exist_ok=True

    )

    return path


###############################################################################
# Sort DataFrame
###############################################################################

def sort_dataframe(

    df,

    column,

    ascending=False

):

    """
    Safe dataframe sorting.
    """

    if column not in df.columns:

        return df

    return (

        df

        .sort_values(

            column,

            ascending=ascending

        )

        .reset_index(

            drop=True

        )

    )


###############################################################################
# Move Column
###############################################################################

def move_column(

    df,

    column,

    position

):

    """
    Move column to desired position.
    """

    if column not in df.columns:

        return df

    columns = list(df.columns)

    columns.remove(column)

    columns.insert(

        position,

        column

    )

    return df[columns]


###############################################################################
# First Available Column
###############################################################################

def first_existing_column(

    df,

    candidates

):

    """
    Return first matching column.
    """

    for column in candidates:

        if column in df.columns:

            return column

    return None


###############################################################################
# Safe Rename
###############################################################################

def safe_rename(

    df,

    mapping

):

    """
    Rename only existing columns.
    """

    mapping = {

        old: new

        for old, new in mapping.items()

        if old in df.columns

    }

    return df.rename(

        columns=mapping

    )


###############################################################################
# DataFrame Summary
###############################################################################

def dataframe_summary(

    df

):

    """
    Basic dataframe summary.
    """

    return {

        "Rows": len(df),

        "Columns": len(df.columns),

        "Missing Values": int(

            df.isna().sum().sum()

        ),

        "Duplicate Rows": int(

            df.duplicated().sum()

        )

    }