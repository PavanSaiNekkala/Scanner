"""
============================================================
Institutional Strategy Comparison Engine V3

Export Component

============================================================
"""

from __future__ import annotations

import streamlit as st


class Exporters:
    @staticmethod
    def excel(file_path: str):
        with open(file_path, "rb") as file:
            st.download_button(
                label="Download Excel Report",
                data=file,
                file_name="Institutional_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
