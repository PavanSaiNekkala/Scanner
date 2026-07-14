"""
Downloads Page
"""

from pathlib import Path

import streamlit as st

import pandas as pd


###########################################################################
# DOWNLOAD PAGE
###########################################################################

class DownloadPage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.ranked = result["ranked"]

        self.excel = result["excel"]

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(self):

        st.header(

            "Downloads"

        )

        self.report_information()

        self.download_excel()

        self.download_csv()

        self.download_json()

    ###########################################################################
    # REPORT INFO
    ###########################################################################

    def report_information(self):

        st.subheader(

            "Generated Report"

        )

        rows = [

            {

                "Property": "Strategies",

                "Value": len(

                    self.ranked

                )

            },

            {

                "Property": "Report",

                "Value": Path(

                    self.excel

                ).name

            },

            {

                "Property": "Best Strategy",

                "Value": self.ranked.iloc[0][

                    "Strategy"

                ]

            },

            {

                "Property": "Best Score",

                "Value": round(

                    self.ranked.iloc[0][

                        "Overall Score"

                    ],

                    2

                )

            }

        ]

        df = df.astype(str)

        st.table(
            df,
            width="stretch"
        )

        st.table(

            pd.DataFrame(

                rows

            )

        )

    ###########################################################################
    # EXCEL
    ###########################################################################

    def download_excel(self):

        st.subheader(

            "Excel Report"

        )

        with open(

            self.excel,

            "rb"

        ) as f:

            st.download_button(

                label="Download Excel Report",

                data=f,

                file_name=Path(

                    self.excel

                ).name,

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            )

    ###########################################################################
    # CSV
    ###########################################################################

    def download_csv(self):

        st.subheader(

            "CSV Export"

        )

        csv = self.ranked.to_csv(

            index=False

        ).encode(

            "utf-8"

        )

        st.download_button(

            label="Download CSV",

            data=csv,

            file_name="Strategy_Ranking.csv",

            mime="text/csv"

        )

    ###########################################################################
    # JSON
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

            label="Download JSON",

            data=json_data,

            file_name="Strategy_Ranking.json",

            mime="application/json"

        )

    ###########################################################################
    # RAW DATA
    ###########################################################################

    def preview(self):

        st.subheader(

            "Preview"

        )

        df = df.astype(str)

        st.dataframe(
            df,
            width="stretch"
        )

        st.dataframe(

            self.ranked,

            width="stretch",

            hide_index=True

        )