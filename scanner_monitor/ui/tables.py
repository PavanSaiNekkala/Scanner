"""
ui/tables.py
============

Reusable institutional table
components for the
Scanner Monitor.

Provides standardized:

- DataFrame rendering
- Searching
- Filtering
- Downloads
- Statistics
- Data quality
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import inspect

import pandas as pd
import streamlit as st

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class TableConfig:
    """
    Shared table configuration.
    """

    default_height: int = 600

    preview_rows: int = 20

    max_export_rows: int = 1_000_000

    hide_index: bool = True

    use_container_width: bool = True

    searchable: bool = True

    downloadable: bool = True

    selectable_columns: bool = True


CONFIG = TableConfig()

# =============================================================================
# Validation
# =============================================================================


def dataframe_exists(
    dataframe: pd.DataFrame,
) -> bool:
    """
    Return True when a dataframe
    exists and contains rows.
    """

    return (

        isinstance(

            dataframe,

            pd.DataFrame,

        )

        and

        not dataframe.empty

    )


def require_dataframe(
    dataframe: pd.DataFrame,
    *,
    message: str = (
        "No records available."
    ),
) -> bool:
    """
    Validate dataframe before
    rendering.
    """

    if dataframe_exists(
        dataframe,
    ):

        return True

    st.info(
        message,
    )

    return False


def column_exists(
    dataframe: pd.DataFrame,
    column: str,
) -> bool:
    """
    Check whether a column exists.
    """

    return (

        dataframe_exists(
            dataframe,
        )

        and

        column in dataframe.columns

    )


# =============================================================================
# Shared Renderer
# =============================================================================


def render_dataframe(
    dataframe: pd.DataFrame,
    *,
    height: int | None = None,
) -> None:
    """
    Standard dataframe renderer.
    """

    st.dataframe(

        dataframe,

        use_container_width=(
            CONFIG.use_container_width
        ),

        hide_index=(
            CONFIG.hide_index
        ),

        height=(

            height

            or

            CONFIG.default_height

        ),

    )


# =============================================================================
# Statistics Engine
# =============================================================================


def dataframe_statistics(
    dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """
    Calculate dataframe statistics.
    """

    if not dataframe_exists(
        dataframe,
    ):

        return {

            "Rows": 0,

            "Columns": 0,

            "Missing": 0,

            "Duplicates": 0,

            "Memory (KB)": 0.0,

        }

    return {

        "Rows":

            len(
                dataframe,
            ),

        "Columns":

            len(
                dataframe.columns,
            ),

        "Missing":

            int(

                dataframe

                .isna()

                .sum()

                .sum()

            ),

        "Duplicates":

            int(

                dataframe

                .duplicated()

                .sum()

            ),

        "Memory (KB)":

            round(

                dataframe

                .memory_usage(
                    deep=True,
                )

                .sum()

                / 1024,

                2,

            ),

    }


# =============================================================================
# Statistics Row
# =============================================================================


def statistics_row(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display dataframe statistics.
    """

    statistics = (

        dataframe_statistics(

            dataframe,

        )

    )

    columns = st.columns(

        len(
            statistics,
        )

    )

    for column, item in zip(

        columns,

        statistics.items(),

    ):

        title, value = item

        with column:

            st.metric(

                title,

                value,

            )

# =============================================================================
# Search Engine
# =============================================================================


def search_dataframe(
    dataframe: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """
    Search across every column.

    Parameters
    ----------
    dataframe
        Source dataframe.

    query
        Search text.

    Returns
    -------
    pd.DataFrame
    """

    if (

        not dataframe_exists(
            dataframe,
        )

        or

        not query

    ):

        return dataframe

    mask = (

        dataframe

        .astype(str)

        .apply(

            lambda column:

            column.str.contains(

                query,

                case=False,

                na=False,

            )

        )

        .any(

            axis=1,

        )

    )

    return dataframe.loc[

        mask,

    ]


def search_box(
    dataframe: pd.DataFrame,
    *,
    key: str,
    label: str = "Search",
) -> pd.DataFrame:
    """
    Display search box.
    """

    query = st.text_input(

        label,

        placeholder="Search all columns...",

        key=f"{key}_search",

    )

    return search_dataframe(

        dataframe,

        query,

    )


# =============================================================================
# Column Selector
# =============================================================================


def column_selector(
    dataframe: pd.DataFrame,
    *,
    key: str,
) -> pd.DataFrame:
    """
    Interactive column selector.
    """

    if not dataframe_exists(
        dataframe,
    ):

        return dataframe

    selected = st.multiselect(

        "Columns",

        options=list(

            dataframe.columns,

        ),

        default=list(

            dataframe.columns,

        ),

        key=f"{key}_columns",

    )

    if not selected:

        return dataframe

    return dataframe[

        selected

    ]


# =============================================================================
# Export Engine
# =============================================================================


def csv_bytes(
    dataframe: pd.DataFrame,
) -> bytes:
    """
    Convert dataframe to CSV.
    """

    return (

        dataframe

        .to_csv(

            index=False,

        )

        .encode(

            "utf-8",

        )

    )


def excel_bytes(
    dataframe: pd.DataFrame,
) -> bytes:
    """
    Convert dataframe to Excel.
    """

    output = BytesIO()

    with pd.ExcelWriter(

        output,

        engine="openpyxl",

    ) as writer:

        dataframe.to_excel(

            writer,

            index=False,

        )

    return output.getvalue()


def download_buttons(
    dataframe: pd.DataFrame,
    *,
    filename: str,
    key: str,
) -> None:
    """
    Display export buttons.
    """

    if not dataframe_exists(
        dataframe,
    ):

        return

    left, right = st.columns(2)

    with left:

        st.download_button(

            "Download CSV",

            data=csv_bytes(

                dataframe,

            ),

            file_name=f"{filename}.csv",

            mime="text/csv",

            key=f"{key}_csv",

            use_container_width=True,

        )

    with right:

        st.download_button(

            "Download Excel",

            data=excel_bytes(

                dataframe,

            ),

            file_name=f"{filename}.xlsx",

            mime=(
                "application/"
                "vnd.openxmlformats-"
                "officedocument."
                "spreadsheetml.sheet"
            ),

            key=f"{key}_excel",

            use_container_width=True,

        )

# =============================================================================
# Generic Table Engine
# =============================================================================


def dataframe_table(
    dataframe: pd.DataFrame,
    *,
    title: str | None = None,
    key: str = "table",
    searchable: bool = CONFIG.searchable,
    selectable_columns: bool = (
        CONFIG.selectable_columns
    ),
    downloadable: bool = (
        CONFIG.downloadable
    ),
    height: int | None = None,
) -> None:
    """
    Institutional dataframe viewer.
    """

    if title:

        st.subheader(

            title,

        )

    if not require_dataframe(

        dataframe,

    ):

        return

    statistics_row(

        dataframe,

    )

    working = dataframe.copy()

    # ==========================================================
    # Search
    # ==========================================================

    if searchable:

        working = search_box(

            working,

            key=key,

        )

    # ==========================================================
    # Column Selector
    # ==========================================================

    if selectable_columns:

        working = column_selector(

            working,

            key=key,

        )

    render_dataframe(

        working,

        height=height,

    )

    if downloadable:

        download_buttons(

            working,

            filename=key,

            key=key,

        )


# =============================================================================
# Sorting
# =============================================================================


def sortable_dataframe(
    dataframe: pd.DataFrame,
    *,
    key: str,
) -> pd.DataFrame:
    """
    Interactive sorting.
    """

    if not dataframe_exists(

        dataframe,

    ):

        return dataframe

    left, right = st.columns(

        2,

    )

    with left:

        column = st.selectbox(

            "Sort By",

            dataframe.columns,

            key=f"{key}_sort",

        )

    with right:

        ascending = st.checkbox(

            "Ascending",

            value=False,

            key=f"{key}_ascending",

        )

    return dataframe.sort_values(

        by=column,

        ascending=ascending,

    )


# =============================================================================
# Numeric Filter
# =============================================================================


def numeric_filter(
    dataframe: pd.DataFrame,
    *,
    column: str,
    key: str,
) -> pd.DataFrame:
    """
    Numeric range filter.
    """

    if not column_exists(

        dataframe,

        column,

    ):

        return dataframe

    if not pd.api.types.is_numeric_dtype(

        dataframe[column],

    ):

        return dataframe

    minimum = float(

        dataframe[column].min(),

    )

    maximum = float(

        dataframe[column].max(),

    )

    selected = st.slider(

        column,

        min_value=minimum,

        max_value=maximum,

        value=(

            minimum,

            maximum,

        ),

        key=f"{key}_range",

    )

    return dataframe.loc[

        dataframe[column].between(

            selected[0],

            selected[1],

        )

    ]


# =============================================================================
# Category Filter
# =============================================================================


def category_filter(
    dataframe: pd.DataFrame,
    *,
    column: str,
    key: str,
) -> pd.DataFrame:
    """
    Category filter.
    """

    if not column_exists(

        dataframe,

        column,

    ):

        return dataframe

    values = sorted(

        dataframe[column]

        .dropna()

        .astype(str)

        .unique()

        .tolist()

    )

    selected = st.multiselect(

        column,

        options=values,

        default=values,

        key=f"{key}_category",

    )

    if not selected:

        return dataframe

    return dataframe.loc[

        dataframe[column]

        .astype(str)

        .isin(

            selected,

        )

    ]


# =============================================================================
# Date Filter
# =============================================================================


def date_filter(
    dataframe: pd.DataFrame,
    *,
    column: str,
    key: str,
) -> pd.DataFrame:
    """
    Date range filter.
    """

    if not column_exists(

        dataframe,

        column,

    ):

        return dataframe

    try:

        dates = pd.to_datetime(

            dataframe[column],

            errors="coerce",

        )

    except Exception:

        return dataframe

    dates = dates.dropna()

    if dates.empty:

        return dataframe

    selected = st.date_input(

        "Date Range",

        value=(

            dates.min().date(),

            dates.max().date(),

        ),

        key=f"{key}_date",

    )

    if len(selected) != 2:

        return dataframe

    mask = pd.to_datetime(

        dataframe[column],

        errors="coerce",

    ).dt.date.between(

        selected[0],

        selected[1],

    )

    return dataframe.loc[

        mask,

    ]

# =============================================================================
# Conditional Styling
# =============================================================================


def style_returns(
    dataframe: pd.DataFrame,
) -> pd.io.formats.style.Styler:
    """
    Apply return highlighting.
    """

    if not dataframe_exists(

        dataframe,

    ):

        return dataframe.style

    def color(

        value: object,

    ) -> str:

        try:

            number = float(

                value,

            )

        except (

            TypeError,

            ValueError,

        ):

            return ""

        if number > 0:

            return (

                "background-color:#DCFCE7;"

                "color:#166534;"

            )

        if number < 0:

            return (

                "background-color:#FEE2E2;"

                "color:#991B1B;"

            )

        return ""

    columns = [

        column

        for column

        in dataframe.columns

        if (

            "return"

            in column.lower()

        )

        or (

            "%"

            in column

        )

    ]

    if not columns:

        return dataframe.style

    return dataframe.style.map(

        color,

        subset=columns,

    )


# =============================================================================
# Specialized Tables
# =============================================================================


def holdings_table(
    dataframe: pd.DataFrame,
    *,
    key: str | None = None,
) -> None:
    """
    Holdings viewer.
    """

    if key is None:

        caller = inspect.stack()[1]

        filename = Path(

            caller.filename,

        ).stem

        key = (

            f"{filename}_"

            f"{caller.function}_"

            f"{caller.lineno}"

        )

    dataframe_table(

        dataframe,

        title="Current Holdings",

        key=key,

    )


def portfolio_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Portfolio summary.
    """

    dataframe_table(

        dataframe,

        title="Portfolio Summary",

        key="portfolio",

        searchable=False,

    )


def daily_monitor_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Daily monitor.
    """

    dataframe_table(

        dataframe,

        title="Daily Monitor",

        key="daily_monitor",

    )


def risk_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Risk summary.
    """

    dataframe_table(

        dataframe,

        title="Risk Summary",

        key="risk",

        searchable=False,

    )


def execution_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Execution summary.
    """

    dataframe_table(

        dataframe,

        title="Execution Summary",

        key="execution",

        searchable=False,

    )


def performance_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Performance summary.
    """

    dataframe_table(

        dataframe,

        title="Performance Summary",

        key="performance",

    )


def history_table(
    dataframe: pd.DataFrame,
    *,
    title: str,
) -> None:
    """
    Generic history viewer.
    """

    dataframe_table(

        dataframe,

        title=title,

        key=(

            title

            .lower()

            .replace(

                " ",

                "_",

            )

        ),

    )


# =============================================================================
# Preview Table
# =============================================================================


def preview_table(
    dataframe: pd.DataFrame,
    *,
    rows: int = CONFIG.preview_rows,
) -> None:
    """
    Display preview rows.
    """

    if not require_dataframe(

        dataframe,

        message="No preview available.",

    ):

        return

    render_dataframe(

        dataframe.head(

            rows,

        ),

        height=None,

    )

# =============================================================================
# Data Quality
# =============================================================================


def data_quality_report(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display dataset quality metrics.
    """

    if not require_dataframe(

        dataframe,

    ):

        return

    statistics_row(

        dataframe,

    )


# =============================================================================
# DataFrame Information
# =============================================================================


def dataframe_info(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display dataframe metadata.
    """

    if not require_dataframe(

        dataframe,

    ):

        return

    memory = round(

        dataframe.memory_usage(

            deep=True,

        ).sum()

        / 1024,

        2,

    )

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

                len(

                    dataframe,

                ),

                len(

                    dataframe.columns,

                ),

                int(

                    dataframe

                    .isna()

                    .sum()

                    .sum()

                ),

                int(

                    dataframe

                    .duplicated()

                    .sum()

                ),

                memory,

            ],

        }

    )

    render_dataframe(

        summary,

        height=None,

    )


# =============================================================================
# Metadata
# =============================================================================


def dataframe_metadata(
    dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return dataframe metadata.
    """

    if not dataframe_exists(

        dataframe,

    ):

        return {

            "rows": 0,

            "columns": 0,

            "memory_kb": 0.0,

            "missing": 0,

            "duplicates": 0,

        }

    return {

        "rows":

            len(

                dataframe,

            ),

        "columns":

            len(

                dataframe.columns,

            ),

        "memory_kb":

            round(

                dataframe

                .memory_usage(

                    deep=True,

                )

                .sum()

                / 1024,

                2,

            ),

        "missing":

            int(

                dataframe

                .isna()

                .sum()

                .sum()

            ),

        "duplicates":

            int(

                dataframe

                .duplicated()

                .sum()

            ),

    }


# =============================================================================
# Utility Functions
# =============================================================================


def dataframe_shape(
    dataframe: pd.DataFrame,
) -> tuple[int, int]:
    """
    Return dataframe shape.
    """

    if not dataframe_exists(

        dataframe,

    ):

        return (

            0,

            0,

        )

    return dataframe.shape


def dataframe_memory(
    dataframe: pd.DataFrame,
) -> float:
    """
    Return dataframe memory
    in kilobytes.
    """

    if not dataframe_exists(

        dataframe,

    ):

        return 0.0

    return round(

        dataframe

        .memory_usage(

            deep=True,

        )

        .sum()

        / 1024,

        2,

    )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [

    "CONFIG",

    "dataframe_exists",

    "require_dataframe",

    "column_exists",

    "render_dataframe",

    "dataframe_statistics",

    "statistics_row",

    "search_dataframe",

    "search_box",

    "column_selector",

    "csv_bytes",

    "excel_bytes",

    "download_buttons",

    "dataframe_table",

    "sortable_dataframe",

    "numeric_filter",

    "category_filter",

    "date_filter",

    "style_returns",

    "holdings_table",

    "portfolio_table",

    "daily_monitor_table",

    "risk_table",

    "execution_table",

    "performance_table",

    "history_table",

    "preview_table",

    "data_quality_report",

    "dataframe_info",

    "dataframe_metadata",

    "dataframe_shape",

    "dataframe_memory",

]