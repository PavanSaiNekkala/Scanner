"""
Downloads Page
"""

from pathlib import Path

import pandas as pd

import streamlit as st


###########################################################################
# DOWNLOAD PAGE
###########################################################################

class DownloadPage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.ranked = result[

            "ranked"

        ]

        self.excel = Path(

            result[

                "excel"

            ]

        )

        self.exports = result.get(

            "exports",

            {}

        )

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Downloads"

        )

        self.report_information()

        st.divider()

        self.export_statistics()

    ###########################################################################
    # REPORT INFORMATION
    ###########################################################################

    def report_information(self):

        st.subheader(

            "Generated Report"

        )

        dataframe = pd.DataFrame({

            "Property": [

                "Report Name",

                "Strategies",

                "Best Strategy",

                "Highest Score",

                "Average Score"

            ],

            "Value": [

                self.excel.name,

                len(

                    self.ranked

                ),

                self.ranked.iloc[

                    0

                ][

                    "Strategy"

                ],

                round(

                    self.ranked[

                        "Overall Score"

                    ].max(),

                    2

                ),

                round(

                    self.ranked[

                        "Overall Score"

                    ].mean(),

                    2

                )

            ]

        })

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # EXPORT STATISTICS
    ###########################################################################

    def export_statistics(self):

        st.subheader(

            "Export Statistics"

        )

        size = (

            round(

                self.excel.stat().st_size

                / 1024,

                2

            )

            if self.excel.exists()

            else 0

        )

        dataframe = pd.DataFrame({

            "Metric": [

                "Workbook Exists",

                "Workbook Size (KB)",

                "CSV / JSON Exports",

                "Output Location"

            ],

            "Value": [

                self.excel.exists(),

                size,

                len(

                    self.exports

                ),

                str(

                    self.excel.parent

                )

            ]

        })

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # DOWNLOAD EXCEL
    ###########################################################################

    def download_excel(self):

        st.subheader(

            "Excel Report"

        )

        if not self.excel.exists():

            st.warning(

                "Excel report not found."

            )

            return

        with open(

            self.excel,

            "rb"

        ) as file:

            st.download_button(

                label="📥 Download Excel Report",

                data=file,

                file_name=self.excel.name,

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                width="stretch"

            )

    ###########################################################################
    # DOWNLOAD CSV
    ###########################################################################

    def download_csv(self):

        st.subheader(

            "CSV Export"

        )

        csv_data = self.ranked.to_csv(

            index=False

        ).encode(

            "utf-8"

        )

        st.download_button(

            label="📥 Download Strategy Ranking (CSV)",

            data=csv_data,

            file_name="Strategy_Ranking.csv",

            mime="text/csv",

            width="stretch"

        )

    ###########################################################################
    # DOWNLOAD JSON
    ###########################################################################

    def download_json(self):

        st.subheader(

            "JSON Export"

        )

        json_data = self.ranked.to_json(

            orient="records",

            indent=4

        )

        st.download_button(

            label="📥 Download Strategy Ranking (JSON)",

            data=json_data,

            file_name="Strategy_Ranking.json",

            mime="application/json",

            width="stretch"

        )

    ###########################################################################
    # DOWNLOAD ALL EXPORTS
    ###########################################################################

    def download_all_exports(self):

        st.subheader(

            "Additional Exports"

        )

        exports = self.exports.get(

            "csv_json",

            {}

        )

        if not exports:

            st.info(

                "No additional exports available."

            )

            return

        for name, path in sorted(

            exports.items()

        ):

            path = Path(

                path

            )

            if not path.exists():

                continue

            suffix = path.suffix.lower()

            mime = (

                "text/csv"

                if suffix == ".csv"

                else "application/json"

            )

            with open(

                path,

                "rb"

            ) as file:

                st.download_button(

                    label=f"📥 {path.name}",

                    data=file,

                    file_name=path.name,

                    mime=mime,

                    key=f"download_{name}",

                    width="stretch"

                )

    ###########################################################################
    # EXPORT VALIDATION
    ###########################################################################

    def export_validation(self):

        st.subheader(

            "Export Validation"

        )

        validation = self.exports.get(

            "validation",

            {}

        )

        if not validation:

            st.info(

                "Validation information is unavailable."

            )

            return

        dataframe = pd.DataFrame({

            "Property":

                list(

                    validation.keys()

                ),

            "Value":

                list(

                    validation.values()

                )

        })

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # EXPORT METADATA
    ###########################################################################

    def export_metadata(self):

        st.subheader(

            "Export Metadata"

        )

        version = self.exports.get(

            "Version",

            {}

        )

        if not version:

            st.info(

                "Metadata unavailable."

            )

            return

        dataframe = pd.DataFrame({

            "Property":

                list(

                    version.keys()

                ),

            "Value":

                list(

                    version.values()

                )

        })

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # EXPORT PREVIEW
    ###########################################################################

    def export_preview(self):

        st.subheader(

            "Export Preview"

        )

        dataframe = self.ranked.head(

            10

        ).copy()

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # EXPORT SUMMARY
    ###########################################################################

    def export_summary(self):

        st.subheader(

            "Export Summary"

        )

        rows = [

            {

                "Metric":

                    "Excel Workbook",

                "Value":

                    self.excel.name

            },

            {

                "Metric":

                    "Strategies",

                "Value":

                    len(

                        self.ranked

                    )

            },

            {

                "Metric":

                    "CSV / JSON Files",

                "Value":

                    len(

                        self.exports.get(

                            "csv_json",

                            {}

                        )

                    )

            },

            {

                "Metric":

                    "Workbook Exists",

                "Value":

                    self.excel.exists()

            }

        ]

        dataframe = pd.DataFrame(

            rows

        )

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # RAW DATA PREVIEW
    ###########################################################################

    def raw_data_preview(self):

        st.subheader(

            "Raw Data Preview"

        )

        dataframe = self.ranked.copy()

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # DOWNLOAD HISTORY
    ###########################################################################

    def download_history(self):

        st.subheader(

            "Generated Files"

        )

        rows = [

            {

                "File":

                    self.excel.name,

                "Type":

                    "Excel",

                "Available":

                    self.excel.exists()

            }

        ]

        exports = self.exports.get(

            "csv_json",

            {}

        )

        for _, path in sorted(

            exports.items()

        ):

            path = Path(

                path

            )

            rows.append({

                "File":

                    path.name,

                "Type":

                    path.suffix.replace(

                        ".",

                        ""

                    ).upper(),

                "Available":

                    path.exists()

            })

        dataframe = pd.DataFrame(

            rows

        )

        dataframe = dataframe.astype(

            str

        )

        st.dataframe(

            dataframe,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # COMPLETE PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Downloads"

        )

        self.report_information()

        st.divider()

        self.export_statistics()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.download_excel()

        with right:

            self.download_csv()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.download_json()

        with right:

            self.download_all_exports()

        st.divider()

        left, right = st.columns(

            2

        )

        with left:

            self.export_validation()

        with right:

            self.export_metadata()

        st.divider()

        self.export_summary()

        st.divider()

        self.export_preview()

        st.divider()

        self.raw_data_preview()

        st.divider()

        self.download_history()