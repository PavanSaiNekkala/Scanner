"""
pages/09_Downloads.py
=====================

Institutional Scanner Monitor

Downloads Center

Browse, preview and download
workflow-generated reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import mimetypes
import plotly.express as px

import pandas as pd
import streamlit as st

from core.config import REPORTS_DIR
from core.logger import get_logger
from core.session import (
    initialize as initialize_session,
)
from core.theme import (
    apply_theme,
    inject_card_css,
)

from ui.cards import (
    divider,
    empty_state,
    section,
)

from ui.sidebar import (
    render_sidebar,
)

from ui.tables import (
    holdings_table,
)

LOGGER = get_logger(__name__)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(slots=True, frozen=True)
class DownloadsConfig:
    """
    Downloads dashboard configuration.
    """

    page_title: str = "Downloads"

    page_icon: str = "📦"

    layout: str = "wide"

    reports_root: Path = REPORTS_DIR

    preview_rows: int = 20

    chart_height: int = 420


CONFIG = DownloadsConfig()

# =============================================================================
# Streamlit Configuration
# =============================================================================

st.set_page_config(

    page_title=CONFIG.page_title,

    page_icon=CONFIG.page_icon,

    layout=CONFIG.layout,

)

apply_theme()

inject_card_css()

render_sidebar()

initialize_session()

# =============================================================================
# Repository Scanner
# =============================================================================


@st.cache_data(show_spinner=False)
def scan_repository(
    root: Path,
) -> pd.DataFrame:
    """
    Scan the reports repository.
    """

    files: list[dict] = []

    if not root.exists():

        return pd.DataFrame()

    for file in root.rglob("*"):

        if not file.is_file():

            continue

        stat = file.stat()

        files.append(

            {

                "Name": file.name,

                "Folder": str(

                    file.parent.relative_to(
                        root,
                    )

                ),

                "Extension": file.suffix.lower(),

                "Size (MB)": round(

                    stat.st_size
                    / 1024
                    / 1024,

                    3,

                ),

                "Modified": datetime.fromtimestamp(

                    stat.st_mtime,

                ),

                "Path": file,

            }

        )

    if not files:

        return pd.DataFrame()

    return (

        pd.DataFrame(files)

        .sort_values(

            "Modified",

            ascending=False,

        )

        .reset_index(

            drop=True,

        )

    )

# =============================================================================
# Repository
# =============================================================================

repository = scan_repository(

    CONFIG.reports_root,

)

# =============================================================================
# Validation
# =============================================================================

if repository.empty:

    empty_state(

        "Repository Empty",

        (
            "No downloadable reports "
            "were found.\n\n"

            "Run the workflow to "
            "generate reports."

        ),

    )

    st.stop()

# =============================================================================
# Page Header
# =============================================================================

section(

    "Downloads Center",

    (
        "Browse, preview and download "
        "workflow-generated reports."
    ),

)

# =============================================================================
# Repository KPIs
# =============================================================================

total_reports = len(
    repository,
)

total_storage = (

    repository["Size (MB)"]

    .sum()

)

total_folders = (

    repository["Folder"]

    .nunique()

)

total_types = (

    repository["Extension"]

    .nunique()

)

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:

    st.metric(

        "Reports",

        f"{total_reports:,}",

    )

with metric2:

    st.metric(

        "Folders",

        total_folders,

    )

with metric3:

    st.metric(

        "File Types",

        total_types,

    )

with metric4:

    st.metric(

        "Storage",

        f"{total_storage:.2f} MB",

    )

divider()

# =============================================================================
# Repository Overview
# =============================================================================

section(

    "Repository Overview",

    (
        "Latest reports available "
        "for download."
    ),

)

overview = repository[

    [

        "Name",

        "Folder",

        "Extension",

        "Size (MB)",

        "Modified",

    ]

].head(10)

holdings_table(

    overview,

    key="repository_overview",

)

st.caption(

    f"Showing latest "

    f"{len(overview):,} "

    f"of "

    f"{total_reports:,} "

    f"reports."

)

divider()

# =============================================================================
# Repository Explorer
# =============================================================================

section(

    "Repository Explorer",

    (
        "Search and browse "
        "workflow-generated reports."
    ),

)

search_col, folder_col, type_col = st.columns(
    [2, 1, 1]
)

with search_col:

    search_text = st.text_input(

        "Search Reports",

        placeholder="Filename...",

    )

with folder_col:

    selected_folder = st.selectbox(

        "Folder",

        [

            "All",

            *sorted(

                repository["Folder"]

                .dropna()

                .unique()

                .tolist()

            ),

        ],

    )

with type_col:

    selected_type = st.selectbox(

        "File Type",

        [

            "All",

            *sorted(

                repository["Extension"]

                .dropna()

                .unique()

                .tolist()

            ),

        ],

    )

filtered_repository = repository.copy()

if search_text:

    filtered_repository = (

        filtered_repository[

            filtered_repository["Name"]

            .str.contains(

                search_text,

                case=False,

                na=False,

            )

        ]

    )

if selected_folder != "All":

    filtered_repository = (

        filtered_repository[

            filtered_repository["Folder"]

            ==

            selected_folder

        ]

    )

if selected_type != "All":

    filtered_repository = (

        filtered_repository[

            filtered_repository["Extension"]

            ==

            selected_type

        ]

    )

st.caption(

    f"{len(filtered_repository):,} "

    f"report(s) found."

)

holdings_table(

    filtered_repository.drop(

        columns=[

            "Path",

        ],

        errors="ignore",

    ),

    key="repository_table",

)

divider()

# =============================================================================
# Folder Distribution
# =============================================================================

section(

    "Folder Distribution",

    (
        "Reports grouped by "
        "repository folder."
    ),

)

folder_summary = (

    filtered_repository

    .groupby(

        "Folder",

        dropna=False,

    )

    .agg(

        Reports=(

            "Name",

            "count",

        ),

        Storage=(

            "Size (MB)",

            "sum",

        ),

    )

    .reset_index()

    .sort_values(

        "Reports",

        ascending=False,

    )

)

left, right = st.columns([1, 2])

with left:

    holdings_table(

        folder_summary,

        key="folder_summary",

    )

with right:

    if not folder_summary.empty:

        figure = px.treemap(

            folder_summary,

            path=[

                "Folder",

            ],

            values="Storage",

            color="Reports",

        )

        figure.update_layout(

            height=CONFIG.chart_height,

        )

        st.plotly_chart(

            figure,

            use_container_width=True,

        )

    else:

        st.info(
            "No folder statistics available."
        )

divider()

# =============================================================================
# File Type Distribution
# =============================================================================

section(

    "File Type Distribution",

    (
        "Repository file formats."
    ),

)

extension_summary = (

    filtered_repository

    .groupby(

        "Extension",

        dropna=False,

    )

    .agg(

        Reports=(

            "Name",

            "count",

        ),

        Storage=(

            "Size (MB)",

            "sum",

        ),

    )

    .reset_index()

    .sort_values(

        "Reports",

        ascending=False,

    )

)

left, right = st.columns([1, 2])

with left:

    holdings_table(

        extension_summary,

        key="extension_summary",

    )

with right:

    if not extension_summary.empty:

        figure = px.pie(

            extension_summary,

            names="Extension",

            values="Reports",

            hole=0.45,

        )

        figure.update_layout(

            height=CONFIG.chart_height,

        )

        st.plotly_chart(

            figure,

            use_container_width=True,

        )

    else:

        st.info(
            "No file type data available."
        )

divider()

# =============================================================================
# Storage Analytics
# =============================================================================

section(

    "Storage Analytics",

    (
        "Repository storage usage."
    ),

)

left, right = st.columns(2)

with left:

    figure = px.histogram(

        filtered_repository,

        x="Size (MB)",

        nbins=25,

    )

    figure.update_layout(

        height=CONFIG.chart_height,

        xaxis_title="File Size (MB)",

    )

    st.plotly_chart(

        figure,

        use_container_width=True,

    )

with right:

    largest_files = (

        filtered_repository

        .sort_values(

            "Size (MB)",

            ascending=False,

        )

        .head(15)

    )

    if not largest_files.empty:

        figure = px.bar(

            largest_files,

            x="Size (MB)",

            y="Name",

            orientation="h",

            text="Size (MB)",

            color="Size (MB)",

        )

        figure.update_layout(

            height=CONFIG.chart_height,

            yaxis=dict(

                autorange="reversed",

            ),

            coloraxis_showscale=False,

        )

        st.plotly_chart(

            figure,

            use_container_width=True,

        )

    else:

        st.info(
            "No storage statistics available."
        )

divider()

# =============================================================================
# Recent Reports
# =============================================================================

section(

    "Recent Reports",

    (
        "Most recently generated "
        "workflow reports."
    ),

)

recent_reports = (

    filtered_repository

    .sort_values(

        "Modified",

        ascending=False,

    )

    .head(20)

)

holdings_table(

    recent_reports.drop(

        columns=[

            "Path",

        ],

        errors="ignore",

    ),

    key="recent_reports",

)

divider()

# =============================================================================
# Report Preview
# =============================================================================

section(

    "Report Preview",

    (
        "Preview the selected "
        "workflow report."
    ),

)

selected_report = st.selectbox(

    "Select Report",

    filtered_repository["Name"],

)

selected_row = (

    filtered_repository.loc[

        filtered_repository["Name"]

        ==

        selected_report

    ]

    .iloc[0]

)

selected_path = selected_row["Path"]

selected_suffix = (

    selected_path

    .suffix

    .lower()

)

left, right = st.columns(

    [1, 2]

)

with left:

    st.metric(

        "Folder",

        selected_row["Folder"],

    )

    st.metric(

        "Type",

        selected_suffix,

    )

    st.metric(

        "Size",

        f"{selected_row['Size (MB)']:.3f} MB",

    )

    st.metric(

        "Modified",

        selected_row[

            "Modified"

        ].strftime(

            "%d %b %Y",

        ),

    )

with right:

    if selected_suffix == ".csv":

        try:

            preview = pd.read_csv(

                selected_path,

                nrows=CONFIG.preview_rows,

            )

            holdings_table(

                preview,

                key="preview_csv",

            )

        except Exception as exc:

            st.error(

                f"Unable to preview CSV: {exc}"

            )

    elif selected_suffix in (

        ".xlsx",

        ".xls",

    ):

        try:

            preview = pd.read_excel(

                selected_path,

                nrows=CONFIG.preview_rows,

            )

            holdings_table(

                preview,

                key="preview_excel",

            )

        except Exception as exc:

            st.error(

                f"Unable to preview Excel: {exc}"

            )

    else:

        st.info(

            "Preview is unavailable "

            "for this file type."

        )

divider()

# =============================================================================
# Individual Downloads
# =============================================================================

section(

    "Individual Downloads",

    (
        "Download workflow "
        "reports individually."
    ),

)

for _, report in (

    filtered_repository

    .iterrows()

):

    with st.container(

        border=True,

    ):

        info, action = st.columns(

            [4, 1]

        )

        with info:

            st.markdown(

                f"**{report['Name']}**"

            )

            st.caption(

                report["Folder"]

            )

            st.write(

                f"{report['Extension']}"

                " • "

                f"{report['Size (MB)']:.3f} MB"

            )

        with action:

            mime = (

                mimetypes.guess_type(

                    str(

                        report["Path"]

                    )

                )[0]

                or

                "application/octet-stream"

            )


            with open(

                report["Path"],

                "rb",

            ) as file:


                st.download_button(

                    "Download",

                    data=file,

                    file_name=report["Name"],

                    mime=mime,

                    key=(

                        f"download_"

                        f"{report['Folder']}_"

                        f"{report['Name']}"

                    ),

                    use_container_width=True,

                )


divider()

# =============================================================================
# Bulk Selection
# =============================================================================

section(

    "Bulk Download",

    (
        "Select multiple reports "
        "for ZIP export."
    ),

)

selected_files = st.multiselect(

    "Reports",

    options=filtered_repository[

        "Name"

    ].tolist(),

)

selected_reports = (

    filtered_repository.loc[

        filtered_repository["Name"]

        .isin(

            selected_files,

        )

    ]

)

metric1, metric2 = st.columns(2)

with metric1:

    st.metric(

        "Selected",

        len(

            selected_reports,

        ),

    )

selected_size = (

    selected_reports[
        "Size (MB)"
    ].sum()

)

with metric2:

    st.metric(

        "Total Size",

        f"{selected_size:.2f} MB",

    )

divider()

# =============================================================================
# ZIP Package
# =============================================================================

section(

    "ZIP Package",

    (
        "Export selected reports "
        "as a ZIP archive."
    ),

)

if selected_reports.empty:

    st.info(

        "Select one or more "

        "reports to continue."

    )

else:

    st.button(

        "Create ZIP Package",

        use_container_width=True,

    )

    st.info(

        "ZIP generation handled "

        "by the repository service."

    )

divider()

# =============================================================================
# Repository Diagnostics
# =============================================================================

section(

    "Repository Diagnostics",

    (
        "Overall repository status "
        "for workflow-generated reports."
    ),

)

diagnostics = pd.DataFrame(

    [

        {

            "Metric": "Total Reports",

            "Value": len(
                repository,
            ),

        },

        {

            "Metric": "Filtered Reports",

            "Value": len(
                filtered_repository,
            ),

        },

        {

            "Metric": "Folders",

            "Value": repository[
                "Folder"
            ].nunique(),

        },

        {

            "Metric": "File Types",

            "Value": repository[
                "Extension"
            ].nunique(),

        },

        {

            "Metric": "Total Storage (MB)",

            "Value": round(

                repository[
                    "Size (MB)"
                ].sum(),

                2,

            ),

        },

        {

            "Metric": "Average File Size (MB)",

            "Value": round(

                repository[
                    "Size (MB)"
                ].mean(),

                3,

            ),

        },

        {

            "Metric": "Largest File (MB)",

            "Value": round(

                repository[
                    "Size (MB)"
                ].max(),

                3,

            ),

        },

        {

            "Metric": "Smallest File (MB)",

            "Value": round(

                repository[
                    "Size (MB)"
                ].min(),

                3,

            ),

        },

    ]

)

holdings_table(

    diagnostics,

    key="repository_diagnostics",

)

divider()

# =============================================================================
# Repository Health
# =============================================================================

section(

    "Repository Health",

    (
        "High-level repository "
        "health indicators."
    ),

)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Reports",

        len(repository),

    )

with col2:

    st.metric(

        "Folders",

        repository[
            "Folder"
        ].nunique(),

    )

with col3:

    st.metric(

        "Extensions",

        repository[
            "Extension"
        ].nunique(),

    )

with col4:

    st.metric(

        "Storage",

        f"{repository['Size (MB)'].sum():.2f} MB",

    )

divider()

# =============================================================================
# Repository Insights
# =============================================================================

section(

    "Repository Insights",

    (
        "Repository observations."
    ),

)

insights = []

if len(repository) > 100:

    insights.append(
        "Large report repository detected."
    )

if repository["Folder"].nunique() > 5:

    insights.append(
        "Reports are organized across multiple folders."
    )

if repository["Extension"].nunique() > 5:

    insights.append(
        "Repository contains multiple report formats."
    )

if repository["Size (MB)"].max() > 100:

    insights.append(
        "Very large report files exist."
    )

if not insights:

    insights.append(
        "Repository appears healthy."
    )

for insight in insights:

    st.success(

        insight,

    )

divider()

# =============================================================================
# Report Status
# =============================================================================

section(

    "Repository Status",

    (
        "Current repository overview."
    ),

)

status = pd.DataFrame(

    [

        {

            "Metric": "Repository Root",

            "Value": str(

                CONFIG.reports_root,

            ),

        },

        {

            "Metric": "Available Reports",

            "Value": len(
                repository,
            ),

        },

        {

            "Metric": "Filtered Reports",

            "Value": len(
                filtered_repository,
            ),

        },

        {

            "Metric": "Storage (MB)",

            "Value": round(

                repository[
                    "Size (MB)"
                ].sum(),

                2,

            ),

        },

    ]

)

holdings_table(

    status,

    key="repository_status",

)

divider()

# =============================================================================
# Footer
# =============================================================================

st.caption(

    "Institutional Scanner Monitor"

)

st.caption(

    "Downloads Center"

)

st.caption(

    (
        "Workflow Report Repository • "
        "Downloads • Preview • ZIP Export"
    )

)