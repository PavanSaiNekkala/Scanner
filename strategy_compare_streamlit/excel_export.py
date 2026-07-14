import json

from pathlib import Path

import pandas as pd

from config import REPORT_NAME


class ExcelExporter:

    def __init__(self):

        self.output = REPORT_NAME

    ###########################################################################

    def export(

        self,

        ranked,

        recommendations,

        overlap

    ):

        with pd.ExcelWriter(

            self.output,

            engine="openpyxl"

        ) as writer:

            ranked.to_excel(

                writer,

                sheet_name="Strategy Ranking",

                index=False

            )

            recommendations.to_excel(

                writer,

                sheet_name="Recommendations",

                index=False

            )

            overlap.to_excel(

                writer,

                sheet_name="Top Stocks",

                index=False

            )

        return self.output

    ###########################################################################

    def export_csv(

        self,

        dataframe,

        filename

    ):

        path = Path(filename)

        dataframe.to_csv(

            path,

            index=False

        )

        return path

    ###########################################################################

    def export_json(

        self,

        dataframe,

        filename

    ):

        path = Path(filename)

        dataframe.to_json(

            path,

            orient="records",

            indent=4

        )

        return path