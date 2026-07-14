"""
Common Utility Functions
"""

from pathlib import Path

import numpy as np

import pandas as pd


###########################################################################
# PATH
###########################################################################

def ensure_directory(path):

    path = Path(path)

    path.mkdir(

        parents=True,

        exist_ok=True

    )

    return path


###########################################################################
# NUMERIC CONVERSION
###########################################################################

def numeric(series):

    return pd.to_numeric(

        series,

        errors="coerce"

    )


###########################################################################
# SAFE DIVISION
###########################################################################

def safe_divide(

    numerator,

    denominator

):

    numerator = np.asarray(

        numerator,

        dtype=float

    )

    denominator = np.asarray(

        denominator,

        dtype=float

    )

    return np.where(

        denominator == 0,

        np.nan,

        numerator / denominator

    )


###########################################################################
# PERCENTAGE
###########################################################################

def percentage(

    numerator,

    denominator

):

    return safe_divide(

        numerator,

        denominator

    ) * 100


###########################################################################
# NORMALIZE SERIES
###########################################################################

def normalize(series):

    series = numeric(

        series

    )

    minimum = series.min()

    maximum = series.max()

    if pd.isna(minimum):

        return series

    if pd.isna(maximum):

        return series

    if maximum == minimum:

        return pd.Series(

            100,

            index=series.index

        )

    return (

        (series - minimum)

        /

        (maximum - minimum)

    ) * 100


###########################################################################
# ROUND DATAFRAME
###########################################################################

def round_dataframe(

    dataframe,

    digits=2

):

    df = dataframe.copy()

    numeric_cols = df.select_dtypes(

        include=np.number

    ).columns

    df[numeric_cols] = df[

        numeric_cols

    ].round(

        digits

    )

    return df


###########################################################################
# FIND NUMERIC COLUMNS
###########################################################################

def numeric_columns(

    dataframe

):

    return dataframe.select_dtypes(

        include=np.number

    ).columns.tolist()


###########################################################################
# FIND TEXT COLUMNS
###########################################################################

def text_columns(

    dataframe

):

    return dataframe.select_dtypes(

        exclude=np.number

    ).columns.tolist()


###########################################################################
# CHECK REQUIRED COLUMNS
###########################################################################

def check_columns(

    dataframe,

    required

):

    missing = [

        c

        for c in required

        if c not in dataframe.columns

    ]

    return missing


###########################################################################
# TOP N
###########################################################################

def top_n(

    dataframe,

    column,

    n=10

):

    if column not in dataframe.columns:

        return dataframe

    return dataframe.nlargest(

        n,

        column

    )


###########################################################################
# BOTTOM N
###########################################################################

def bottom_n(

    dataframe,

    column,

    n=10

):

    if column not in dataframe.columns:

        return dataframe

    return dataframe.nsmallest(

        n,

        column

    )


###########################################################################
# FORMAT PERCENT
###########################################################################

def percent(value):

    if pd.isna(value):

        return ""

    return f"{value:.2f}%"


###########################################################################
# FORMAT NUMBER
###########################################################################

def number(

    value,

    digits=2

):

    if pd.isna(value):

        return ""

    return round(

        float(value),

        digits

    )


###########################################################################
# SORT DESCENDING
###########################################################################

def descending(

    dataframe,

    column

):

    if column not in dataframe.columns:

        return dataframe

    return dataframe.sort_values(

        column,

        ascending=False

    )


###########################################################################
# SORT ASCENDING
###########################################################################

def ascending(

    dataframe,

    column

):

    if column not in dataframe.columns:

        return dataframe

    return dataframe.sort_values(

        column,

        ascending=True

    )


###########################################################################
# DATAFRAME INFO
###########################################################################

def dataframe_info(

    dataframe

):

    return {

        "Rows": len(

            dataframe

        ),

        "Columns": len(

            dataframe.columns

        ),

        "Memory (KB)": round(

            dataframe.memory_usage(

                deep=True

            ).sum()

            /

            1024,

            2

        )

    }