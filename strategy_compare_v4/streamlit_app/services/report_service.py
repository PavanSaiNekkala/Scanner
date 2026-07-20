"""
report_service.py
=================

Institutional Report Management Service
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ReportService:
    """
    Report management service.
    """

    def __init__(self, output_folder):
        self.output = Path(output_folder)

        self.files = list(self.output.glob("*.xlsx"))

    # =====================================================
    # Available Reports
    # =====================================================

    def reports(self):
        return sorted([f.name for f in self.files])

    # =====================================================
    # Report Exists
    # =====================================================

    def exists(
        self,
        report: str,
    ):
        return (self.output / report).exists()

    # =====================================================
    # File Size
    # =====================================================

    def file_size(
        self,
        report,
    ):
        file = self.output / report

        if not file.exists():
            return 0

        return round(
            file.stat().st_size / 1024,
            2,
        )

    # =====================================================
    # Workbook
    # =====================================================

    def workbook(
        self,
        report,
    ):
        file = self.output / report

        return pd.ExcelFile(file)

    # =====================================================
    # Sheet Names
    # =====================================================

    def sheets(
        self,
        report,
    ):
        return self.workbook(report).sheet_names

    # =====================================================
    # Load Sheet
    # =====================================================

    def load_sheet(
        self,
        report,
        sheet,
    ):
        file = self.output / report

        return pd.read_excel(
            file,
            sheet_name=sheet,
        )

    # =====================================================
    # Workbook Summary
    # =====================================================

    def workbook_summary(
        self,
        report,
    ):
        excel = self.workbook(report)

        rows = []

        for sheet in excel.sheet_names:
            df = pd.read_excel(
                excel,
                sheet_name=sheet,
            )

            rows.append(
                {
                    "Sheet": sheet,
                    "Rows": len(df),
                    "Columns": len(df.columns),
                    "Memory (KB)": round(
                        df.memory_usage(deep=True).sum() / 1024,
                        2,
                    ),
                }
            )

        return pd.DataFrame(rows)

    # =====================================================
    # Report Summary
    # =====================================================

    def summary(self):
        rows = []

        for report in self.reports():
            rows.append(
                {
                    "Workbook": report,
                    "Sheets": len(self.sheets(report)),
                    "Size (KB)": self.file_size(report),
                }
            )

        return pd.DataFrame(rows)

    # =====================================================
    # Search Reports
    # =====================================================

    def search(
        self,
        keyword,
    ):
        keyword = keyword.lower()

        return [r for r in self.reports() if keyword in r.lower()]

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(
        self,
        report,
        sheet,
    ):
        df = self.load_sheet(
            report,
            sheet,
        )

        numeric = df.select_dtypes(include="number")

        if numeric.empty:
            return pd.DataFrame()

        return numeric.describe().T

    # =====================================================
    # Missing Values
    # =====================================================

    def missing_values(
        self,
        report,
        sheet,
    ):
        df = self.load_sheet(
            report,
            sheet,
        )

        return (
            df.isna()
            .sum()
            .rename("Missing")
            .reset_index()
            .rename(columns={"index": "Column"})
        )

    # =====================================================
    # Column Information
    # =====================================================

    def columns(
        self,
        report,
        sheet,
    ):
        df = self.load_sheet(
            report,
            sheet,
        )

        return pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Unique": df.nunique(),
                "Missing": df.isna().sum(),
            }
        )

    # =====================================================
    # Export CSV
    # =====================================================

    def export_csv(
        self,
        report,
        sheet,
        output_file,
    ):
        df = self.load_sheet(
            report,
            sheet,
        )

        df.to_csv(
            output_file,
            index=False,
        )

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(
        self,
        report,
    ):
        file = self.output / report

        return {
            "Name": file.name,
            "Path": str(file),
            "Size (KB)": self.file_size(report),
            "Sheets": len(self.sheets(report)),
        }

    # =====================================================
    # Dashboard Overview
    # =====================================================

    def dashboard(self):
        return {
            "Reports": len(self.reports()),
            "Directory": str(self.output),
            "Total Size (KB)": round(
                sum(self.file_size(r) for r in self.reports()),
                2,
            ),
        }
