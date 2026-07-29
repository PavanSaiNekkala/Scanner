"""
ui.tables
=========

Reusable institutional table components.

Features
--------
- Responsive tables
- Search
- Column selector
- CSV export
- Dataset statistics
- Validation
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import inspect
import pandas as pd
import streamlit as st

# =============================================================================
# Helpers
# =============================================================================


def dataframe_exists(
    df: pd.DataFrame,
) -> bool:
    """
    Return True when dataframe has rows.
    """

    return (
        isinstance(df, pd.DataFrame)
        and not df.empty
    )


def dataframe_statistics(
    df: pd.DataFrame,
) -> dict[str, int]:
    """
    Basic dataframe statistics.
    """

    if df.empty:

        return {

            "Rows": 0,

            "Columns": 0,

            "Missing": 0,

            "Duplicates": 0,

        }

    return {

        "Rows": len(df),

        "Columns": len(df.columns),

        "Missing": int(
            df.isna().sum().sum()
        ),

        "Duplicates": int(
            df.duplicated().sum()
        ),

    }


# =============================================================================
# Search
# =============================================================================


def search_dataframe(
    df: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """
    Search entire dataframe.
    """

    if not query:

        return df

    mask = df.astype(
        str,
    ).apply(
        lambda column:
        column.str.contains(
            query,
            case=False,
            na=False,
        )
    ).any(
        axis=1,
    )

    return df.loc[
        mask
    ]


# =============================================================================
# Column Selector
# =============================================================================

def column_selector(
    df: pd.DataFrame,
    *,
    key: str,
) -> pd.DataFrame:
    """
    Interactive column selector.
    """

    columns = st.multiselect(
        "Columns",
        options=df.columns.tolist(),
        default=df.columns.tolist(),
        key=key,          # <-- changed
    )

    if not columns:
        return df

    return df[columns]

# =============================================================================
# Download
# =============================================================================


def csv_bytes(
    df: pd.DataFrame,
) -> bytes:
    """
    Convert dataframe to CSV bytes.
    """

    return df.to_csv(
        index=False,
    ).encode(
        "utf-8",
    )


def excel_bytes(
    df: pd.DataFrame,
) -> bytes:
    """
    Convert dataframe to Excel bytes.
    """

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        df.to_excel(

            writer,

            index=False,

        )

    return output.getvalue()


def download_buttons(
    data,
    filename: str,
    label: str = "Download CSV",
    key: str | None = None,
) -> None:
    """
    Render a download button for DataFrames or raw bytes.
    """

    if data is None:
        st.info("Nothing available to download.")
        return

    # Convert DataFrame -> CSV bytes
    if isinstance(data, pd.DataFrame):
        payload = data.to_csv(index=False).encode("utf-8")
        mime = "text/csv"
        if not filename.endswith(".csv"):
            filename = f"{filename}.csv"

    # Already bytes
    elif isinstance(data, bytes):
        payload = data
        mime = "application/octet-stream"

    # String
    elif isinstance(data, str):
        payload = data.encode("utf-8")
        mime = "text/plain"

    else:
        raise TypeError(
            f"Unsupported download type: {type(data)}"
        )

    st.download_button(
        label=label,
        data=payload,
        file_name=filename,
        mime=mime,
        key=key or f"download_{filename}",
        use_container_width=True,
    )

# =============================================================================
# Statistics
# =============================================================================


def statistics_row(
    df: pd.DataFrame,
) -> None:
    """
    Dataset statistics.
    """

    stats = dataframe_statistics(
        df,
    )

    cols = st.columns(
        len(stats),
    )

    for col, item in zip(
        cols,
        stats.items(),
    ):

        key, value = item

        with col:

            st.metric(

                key,

                value,

            )


# =============================================================================
# Generic Table
# =============================================================================

def dataframe_table(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    key: str = "table",
    searchable: bool = True,
    selectable_columns: bool = True,
    downloadable: bool = True,
    height: int = 600,
) -> None:
    """
    Institutional dataframe viewer.
    """

    if title:
        st.subheader(title)

    if not dataframe_exists(df):
        st.info("No records available.")
        return

    statistics_row(df)

    working = df.copy()

    # ==========================================================
    # Search
    # ==========================================================

    if searchable:

        query = st.text_input(
            "Search",
            key=f"{key}_search",
            placeholder="Search all columns...",
        )

        working = search_dataframe(
            working,
            query,
        )

    # ==========================================================
    # Column Selector
    # ==========================================================

    if selectable_columns:

        working = column_selector(
            working,
            key=f"{key}_columns",
        )

    # ==========================================================
    # Display
    # ==========================================================

    st.dataframe(
        working,
        use_container_width=True,
        hide_index=True,
        height=height,
    )

    # ==========================================================
    # Download
    # ==========================================================

    if downloadable:

        download_buttons(
            working,
            filename=key,
            key=f"{key}_download",
        )

# =============================================================================
# Sorting
# =============================================================================


def sortable_dataframe(
    df: pd.DataFrame,
    *,
    key: str,
) -> pd.DataFrame:
    """
    Interactive dataframe sorting.
    """

    if df.empty:

        return df

    col1, col2 = st.columns(2)

    with col1:

        column = st.selectbox(

            "Sort By",

            options=df.columns,

            key=f"{key}_sort",

        )

    with col2:

        ascending = st.checkbox(

            "Ascending",

            value=False,

            key=f"{key}_ascending",

        )

    return df.sort_values(

        by=column,

        ascending=ascending,

    )


# =============================================================================
# Numeric Filter
# =============================================================================


def numeric_filter(
    df: pd.DataFrame,
    *,
    column: str,
    key: str,
) -> pd.DataFrame:
    """
    Numeric range filter.
    """

    if column not in df.columns:

        return df

    if not pd.api.types.is_numeric_dtype(
        df[column],
    ):

        return df

    minimum = float(
        df[column].min(),
    )

    maximum = float(
        df[column].max(),
    )

    values = st.slider(

        column,

        min_value=minimum,

        max_value=maximum,

        value=(minimum, maximum),

        key=key,

    )

    return df.loc[
        df[column].between(
            values[0],
            values[1],
        )
    ]


# =============================================================================
# Category Filter
# =============================================================================


def category_filter(
    df: pd.DataFrame,
    *,
    column: str,
    key: str,
) -> pd.DataFrame:
    """
    Category multiselect filter.
    """

    if column not in df.columns:

        return df

    values = sorted(

        df[column]

        .dropna()

        .astype(str)

        .unique()

        .tolist()

    )

    selected = st.multiselect(

        column,

        values,

        default=values,

        key=key,

    )

    if not selected:

        return df

    return df.loc[
        df[column].astype(str).isin(
            selected,
        )
    ]


# =============================================================================
# Date Filter
# =============================================================================


def date_filter(
    df: pd.DataFrame,
    *,
    column: str,
) -> pd.DataFrame:
    """
    Filter date range.
    """

    if column not in df.columns:

        return df

    try:

        dates = pd.to_datetime(
            df[column],
        )

    except Exception:

        return df

    start = dates.min().date()

    end = dates.max().date()

    selected = st.date_input(

        "Date Range",

        value=(start, end),

    )

    if len(selected) != 2:

        return df

    return df.loc[
        dates.dt.date.between(

            selected[0],

            selected[1],

        )
    ]


# =============================================================================
# Conditional Styling
# =============================================================================


def style_returns(
    df: pd.DataFrame,
) -> pd.io.formats.style.Styler:
    """
    Highlight returns.
    """

    def color(value):

        try:

            value = float(value)

        except Exception:

            return ""

        if value > 0:

            return (
                "background-color:#DCFCE7;"
                "color:#166534;"
            )

        if value < 0:

            return (
                "background-color:#FEE2E2;"
                "color:#991B1B;"
            )

        return ""

    columns = [

        c

        for c in df.columns

        if "return" in c.lower()

        or "%" in c

    ]

    if not columns:

        return df.style

    return df.style.applymap(

        color,

        subset=columns,

    )


# =============================================================================
# Holdings Table
# =============================================================================

def holdings_table(
    df: pd.DataFrame,
    *,
    key: str | None = None,
) -> None:

    if key is None:
        caller = inspect.stack()[1]
        filename = Path(caller.filename).stem
        function = caller.function
        line = caller.lineno

        key = f"{filename}_{function}_{line}"

    dataframe_table(
        df,
        title="Current Holdings",
        key=key,
    )

# =============================================================================
# Daily Monitor Table
# =============================================================================


def daily_monitor_table(
    df: pd.DataFrame,
) -> None:
    """
    Daily monitor viewer.
    """

    if df.empty:

        st.info(
            "No daily monitor available."
        )

        return

    dataframe_table(

        df,

        title="Daily Monitor",

        key="daily_monitor",

    )


# =============================================================================
# Risk Table
# =============================================================================


def risk_table(
    df: pd.DataFrame,
) -> None:
    """
    Risk summary.
    """

    dataframe_table(

        df,

        title="Risk Summary",

        key="risk",

        searchable=False,

    )


# =============================================================================
# Portfolio Table
# =============================================================================


def portfolio_table(
    df: pd.DataFrame,
) -> None:
    """
    Portfolio summary.
    """

    dataframe_table(

        df,

        title="Portfolio Summary",

        key="portfolio",

        searchable=False,

    )


# =============================================================================
# Execution Table
# =============================================================================


def execution_table(
    df: pd.DataFrame,
) -> None:
    """
    Execution summary.
    """

    dataframe_table(

        df,

        title="Execution Summary",

        key="execution",

        searchable=False,

    )


# =============================================================================
# Performance Table
# =============================================================================


def performance_table(
    df: pd.DataFrame,
) -> None:
    """
    Performance summary.
    """

    dataframe_table(

        df,

        title="Performance Summary",

        key="performance",

    )


# =============================================================================
# History Table
# =============================================================================


def history_table(
    df: pd.DataFrame,
    *,
    title: str,
) -> None:
    """
    Generic history viewer.
    """

    dataframe_table(

        df,

        title=title,

        key=title.lower().replace(
            " ",
            "_",
        ),

    )


# =============================================================================
# Preview Table
# =============================================================================


def preview_table(
    df: pd.DataFrame,
    *,
    rows: int = 10,
) -> None:
    """
    Preview first rows.
    """

    if df.empty:

        st.info(
            "No preview available."
        )

        return

    st.dataframe(

        df.head(rows),

        use_container_width=True,

        hide_index=True,

    )


# =============================================================================
# Data Quality
# =============================================================================


def data_quality_report(
    df: pd.DataFrame,
) -> None:
    """
    Display data quality metrics.
    """

    stats = dataframe_statistics(
        df,
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rows",
        stats["Rows"],
    )

    col2.metric(
        "Columns",
        stats["Columns"],
    )

    col3.metric(
        "Missing",
        stats["Missing"],
    )

    col4.metric(
        "Duplicates",
        stats["Duplicates"],
    )



def dataframe_info(df: pd.DataFrame) -> None:
    """
    Display basic dataframe diagnostics.
    """

    if df.empty:

        st.info("No data available.")

        return

    summary = pd.DataFrame(

        {

            "Metric": [

                "Rows",

                "Columns",

                "Missing Values",

                "Duplicate Rows",

                "Memory (KB)",

            ],

            "Value": [

                len(df),

                len(df.columns),

                int(df.isna().sum().sum()),

                int(df.duplicated().sum()),

                round(

                    df.memory_usage(deep=True).sum() / 1024,

                    2,

                ),

            ],

        }

    )

    st.dataframe(

        summary,

        use_container_width=True,

        hide_index=True,

    )

