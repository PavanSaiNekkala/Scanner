"""
============================================================
Institutional Strategy Comparison Engine V3

File : reports/excel_strategy_exporter.py

Excel Strategy Comparison Exporter

Author : Pavan Sai
============================================================
"""

from __future__ import annotations


from pathlib import Path

import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)



class ExcelStrategyExporter:
    """
    Exports institutional strategy comparison report.

    Generates workbook:

    Institutional_Strategy_Comparison.xlsx


    Sheets
    ------

    1. Strategy Ranking
    2. Top Stocks
    3. Complete Comparison
    4. Performance Analysis
    5. Risk Analysis
    6. Exit Analysis
    7. Statistical Summary

    """



    def __init__(
        self,
        output_path: str | Path = 
        "outputs/excel/Institutional_Strategy_Comparison.xlsx"
    ):


        self.output_path = Path(

            output_path

        )


        self.output_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )



    # ==================================================
    # SAFE SHEET WRITER
    # ==================================================

    def write_sheet(
        self,
        writer,
        dataframe,
        sheet_name
    ):


        if dataframe is None:

            return


        if not isinstance(

            dataframe,

            pd.DataFrame

        ):

            return



        dataframe.to_excel(

            writer,

            sheet_name=sheet_name,

            index=False

        )



    # ==================================================
    # EXPORT
    # ==================================================

    def export(
        self,
        report_data: dict
    ):


        logger.info(

            "Creating Excel Strategy Report..."

        )


        with pd.ExcelWriter(

            self.output_path,

            engine="openpyxl"

        ) as writer:



            # ------------------------------------------
            # Strategy Ranking
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Strategy Ranking"

                ),

                "Strategy Ranking"

            )



            # ------------------------------------------
            # Top Stocks
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Top Stocks"

                ),

                "Top Stocks"

            )



            # ------------------------------------------
            # Full Comparison
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Complete Comparison"

                ),

                "Complete Comparison"

            )



            # ------------------------------------------
            # Performance
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Performance Analysis"

                ),

                "Performance Analysis"

            )



            # ------------------------------------------
            # Risk
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Risk Analysis"

                ),

                "Risk Analysis"

            )



            # ------------------------------------------
            # Exit
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Exit Analysis"

                ),

                "Exit Analysis"

            )



            # ------------------------------------------
            # Statistics
            # ------------------------------------------

            self.write_sheet(

                writer,

                report_data.get(

                    "Statistical Summary"

                ),

                "Statistical Summary"

            )



        logger.info(

            "Excel report created: %s",

            self.output_path

        )


        return self.output_path



if __name__ == "__main__":

    print(

        "Import ExcelStrategyExporter"

    )