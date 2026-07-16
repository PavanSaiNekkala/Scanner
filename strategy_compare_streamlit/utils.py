"""
Common Utility Functions
"""

from pathlib import Path

import numpy as np

import pandas as pd

from config import (

    DECIMAL_PLACES,

    TOP_N

)

###########################################################################
# DIRECTORY
###########################################################################

def ensure_directory(

    path

):

    path = Path(

        path

    )

    path.mkdir(

        parents=True,

        exist_ok=True

    )

    return path


###########################################################################
# EMPTY DATAFRAME
###########################################################################

def is_empty_dataframe(

    dataframe

):

    return (

        dataframe is None

        or

        dataframe.empty

    )


###########################################################################
# NUMERIC
###########################################################################

def numeric(

    series

):

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

    return (

        safe_divide(

            numerator,

            denominator

        )

        * 100

    )


###########################################################################
# NORMALIZE
###########################################################################

def normalize(

    series

):

    series = numeric(

        series

    )

    if series.isna().all():

        return series

    minimum = series.min()

    maximum = series.max()

    if maximum == minimum:

        return pd.Series(

            100.0,

            index=series.index

        )

    return (

        (

            series

            - minimum

        )

        /

        (

            maximum

            - minimum

        )

    ) * 100


###########################################################################
# ROUND
###########################################################################

def round_dataframe(

    dataframe,

    digits=DECIMAL_PLACES

):

    df = dataframe.copy()

    cols = df.select_dtypes(

        include=np.number

    ).columns

    df[cols] = df[

        cols

    ].round(

        digits

    )

    return df


###########################################################################
# NUMERIC COLUMNS
###########################################################################

def numeric_columns(

    dataframe

):

    return dataframe.select_dtypes(

        include=np.number

    ).columns.tolist()


###########################################################################
# TEXT COLUMNS
###########################################################################

def text_columns(

    dataframe

):

    return dataframe.select_dtypes(

        exclude=np.number

    ).columns.tolist()


###########################################################################
# IS NUMERIC
###########################################################################

def is_numeric_column(

    dataframe,

    column

):

    if column not in dataframe.columns:

        return False

    return pd.api.types.is_numeric_dtype(

        dataframe[column]

    )


###########################################################################
# CHECK REQUIRED COLUMNS
###########################################################################

def check_columns(

    dataframe,

    required

):

    return [

        column

        for column in required

        if column not in dataframe.columns

    ]


###########################################################################
# TOP N
###########################################################################

def top_n(

    dataframe,

    column,

    n=TOP_N

):

    if (

        column not in dataframe.columns

        or

        dataframe.empty

    ):

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

    n=TOP_N

):

    if (

        column not in dataframe.columns

        or

        dataframe.empty

    ):

        return dataframe

    return dataframe.nsmallest(

        n,

        column

    )


###########################################################################
# FORMAT %
###########################################################################

def percent(

    value

):

    if pd.isna(

        value

    ):

        return ""

    return f"{value:.2f}%"


###########################################################################
# FORMAT NUMBER
###########################################################################

def number(

    value,

    digits=DECIMAL_PLACES

):

    if pd.isna(

        value

    ):

        return ""

    return round(

        float(value),

        digits

    )


###########################################################################
# SORT
###########################################################################

def sort_dataframe(

    dataframe,

    column,

    ascending=False

):

    if column not in dataframe.columns:

        return dataframe

    return dataframe.sort_values(

        column,

        ascending=ascending

    )


###########################################################################
# DESCENDING
###########################################################################

def descending(

    dataframe,

    column

):

    return sort_dataframe(

        dataframe,

        column,

        False

    )


###########################################################################
# ASCENDING
###########################################################################

def ascending(

    dataframe,

    column

):

    return sort_dataframe(

        dataframe,

        column,

        True

    )


###########################################################################
# FORMAT DATAFRAME
###########################################################################

def format_dataframe(

    dataframe

):

    return dataframe.astype(

        str

    )


###########################################################################
# MEMORY
###########################################################################

def memory_usage(

    dataframe

):

    return round(

        dataframe.memory_usage(

            deep=True

        ).sum()

        / 1024,

        2

    )


###########################################################################
# DATAFRAME INFO
###########################################################################

def dataframe_info(

    dataframe

):

    return {

        "Rows":

            len(

                dataframe

            ),

        "Columns":

            len(

                dataframe.columns

            ),

        "Memory (KB)":

            memory_usage(

                dataframe

            )

    }