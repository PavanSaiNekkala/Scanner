"""
=============================================================
Institutional Excel Export Engine V4

Module:
    reports/excel_exporter.py

Purpose:
    Export all institutional reports into a
    professionally formatted Excel workbook.

Features

    • Multiple Worksheets
    • Auto Column Width
    • Freeze Panes
    • Filters
    • Number Formatting
    • Conditional Formatting
    • Institution Ready Layout

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import openpyxl

from openpyxl.styles import Font
from openpyxl.styles import PatternFill
from openpyxl.styles import Border
from openpyxl.styles import Side
from openpyxl.styles import Alignment

from openpyxl.utils import get_column_letter

from openpyxl.formatting.rule import ColorScaleRule


class ExcelExporter:

    """
    Institutional Excel Export Engine
    """

    def __init__(

        self,

        output_file="Institutional_Report.xlsx"

    ):

        self.output = output_file

        self.writer = None

        self.workbook = None


    # ---------------------------------------------------------

    def create_workbook(self):

        """
        Create Excel workbook.
        """

        self.writer = pd.ExcelWriter(

            self.output,

            engine="openpyxl"

        )

        return self


    # ---------------------------------------------------------

    def add_sheet(

        self,

        dataframe,

        sheet_name

    ):

        """
        Export dataframe.
        """

        dataframe.to_excel(

            self.writer,

            sheet_name=sheet_name,

            index=False

        )

        return self


    # ---------------------------------------------------------

    def save(self):

        """
        Save workbook.
        """

        self.writer.close()

        return self


    # ---------------------------------------------------------

    def load_workbook(self):

        """
        Load workbook for formatting.
        """

        self.workbook = openpyxl.load_workbook(

            self.output

        )

        return self


    # ---------------------------------------------------------

    def style_headers(self):

        """
        Style every worksheet header.
        """

        header_fill = PatternFill(

            fill_type="solid",

            fgColor="1F4E78"

        )

        header_font = Font(

            bold=True,

            color="FFFFFF"

        )

        thin = Side(

            style="thin"

        )

        border = Border(

            left=thin,

            right=thin,

            top=thin,

            bottom=thin

        )

        for ws in self.workbook.worksheets:

            for cell in ws[1]:

                cell.fill = header_fill

                cell.font = header_font

                cell.border = border

                cell.alignment = Alignment(

                    horizontal="center",

                    vertical="center"

                )

        return self


    # ---------------------------------------------------------

    def freeze_headers(self):

        """
        Freeze first row.
        """

        for ws in self.workbook.worksheets:

            ws.freeze_panes = "A2"

        return self


    # ---------------------------------------------------------

    def auto_filter(self):

        """
        Enable filters.
        """

        for ws in self.workbook.worksheets:

            ws.auto_filter.ref = ws.dimensions

        return self


    # ---------------------------------------------------------

    def auto_width(self):

        """
        Auto-size columns.
        """

        for ws in self.workbook.worksheets:

            for column in ws.columns:

                length = 0

                letter = get_column_letter(

                    column[0].column

                )

                for cell in column:

                    try:

                        length = max(

                            length,

                            len(

                                str(cell.value)

                            )

                        )

                    except:

                        pass

                ws.column_dimensions[

                    letter

                ].width = min(

                    length + 3,

                    40

                )

        return self


    # ---------------------------------------------------------

    def number_format(self):

        """
        Apply number formats.
        """

        for ws in self.workbook.worksheets:

            for row in ws.iter_rows(

                min_row=2

            ):

                for cell in row:

                    if isinstance(

                        cell.value,

                        float

                    ):

                        cell.number_format = "0.00"

        return self

    # ---------------------------------------------------------

    def apply_color_scale(self):

        """
        Apply conditional formatting
        to numeric columns.
        """

        rule = ColorScaleRule(

            start_type="min",

            start_color="F8696B",

            mid_type="percentile",

            mid_value=50,

            mid_color="FFEB84",

            end_type="max",

            end_color="63BE7B"

        )

        for ws in self.workbook.worksheets:

            if ws.max_row <= 2:

                continue

            for col in range(2, ws.max_column + 1):

                ws.conditional_formatting.add(

                    f"{get_column_letter(col)}2:{get_column_letter(col)}{ws.max_row}",

                    rule

                )

        return self


    # ---------------------------------------------------------

    def alternate_row_colors(self):

        """
        Apply alternating row colors.
        """

        fill = PatternFill(

            fill_type="solid",

            fgColor="F7F7F7"

        )

        for ws in self.workbook.worksheets:

            for row in range(2, ws.max_row + 1):

                if row % 2 == 0:

                    for col in range(1, ws.max_column + 1):

                        ws.cell(

                            row=row,

                            column=col

                        ).fill = fill

        return self


    # ---------------------------------------------------------

    def highlight_recommendations(self):

        """
        Highlight recommendation values.
        """

        colors = {

            "Strong Buy": "00B050",

            "Buy": "92D050",

            "Watch": "FFD966",

            "Improve": "F4B183",

            "Avoid": "FF9999",

            "Reject": "FF0000"

        }

        for ws in self.workbook.worksheets:

            headers = [

                c.value

                for c in ws[1]

            ]

            if "Recommendation" not in headers:

                continue

            col = headers.index(

                "Recommendation"

            ) + 1

            for row in range(

                2,

                ws.max_row + 1

            ):

                cell = ws.cell(

                    row=row,

                    column=col

                )

                if cell.value in colors:

                    cell.fill = PatternFill(

                        fill_type="solid",

                        fgColor=colors[

                            cell.value

                        ]

                    )

                    cell.font = Font(

                        bold=True,

                        color="FFFFFF"

                    )

        return self


    # ---------------------------------------------------------

    def add_summary_sheet(self):

        """
        Create workbook summary.
        """

        if "Summary" in self.workbook.sheetnames:

            del self.workbook["Summary"]

        ws = self.workbook.create_sheet(

            "Summary",

            0

        )

        ws["A1"] = "Institutional Strategy Comparison Report"

        ws["A1"].font = Font(

            bold=True,

            size=16

        )

        ws["A3"] = "Workbook"

        ws["B3"] = Path(

            self.output

        ).name

        ws["A4"] = "Worksheets"

        ws["B4"] = len(

            self.workbook.sheetnames

        ) - 1

        ws["A5"] = "Generated"

        ws["B5"] = pd.Timestamp.now()

        return self


    # ---------------------------------------------------------

    def workbook_properties(self):

        """
        Workbook metadata.
        """

        self.workbook.properties.creator = "Strategy Comparison Engine"

        self.workbook.properties.title = (

            "Institutional Strategy Report"

        )

        self.workbook.properties.subject = (

            "Strategy Analytics"

        )

        self.workbook.properties.category = (

            "Trading Analytics"

        )

        return self


    # ---------------------------------------------------------

    def finalize(self):

        """
        Save formatted workbook.
        """

        self.workbook.save(

            self.output

        )

        return self


    # ---------------------------------------------------------

    def run(self):

        """
        Execute formatting pipeline.
        """

        return (

            self

            .load_workbook()

            .style_headers()

            .freeze_headers()

            .auto_filter()

            .auto_width()

            .number_format()

            .apply_color_scale()

            .alternate_row_colors()

            .highlight_recommendations()

            .add_summary_sheet()

            .workbook_properties()

            .finalize()

        )


# ==========================================================
# Convenience Function
# ==========================================================

def export_excel(

    output_file,

    sheets

):

    """
    Export multiple dataframes to
    formatted Excel workbook.

    Parameters
    ----------
    output_file : str
        Output workbook path.

    sheets : dict
        Dictionary where:
            key   = sheet name
            value = dataframe
    """

    exporter = ExcelExporter(

        output_file

    )

    exporter.create_workbook()

    for sheet, df in sheets.items():

        if isinstance(

            df,

            pd.DataFrame

        ):

            exporter.add_sheet(

                df,

                sheet

            )

    exporter.save()

    exporter.run()

    return exporter


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    print(

        "Import export_excel() into the reporting pipeline."

    )