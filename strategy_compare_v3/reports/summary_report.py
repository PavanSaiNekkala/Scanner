"""
============================================================
Institutional Strategy Comparison Engine V3
File : reports/summary_report.py

Summary Report Generator

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)


class SummaryReport:
    """
    Generates an executive summary
    of the analysis.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()

    # --------------------------------------------------

    def dataset_information(self):

        return pd.DataFrame({

            "Metric": [

                "Generated On",

                "Total Strategies",

                "Total Columns",

                "Numeric Columns",

                "Missing Values"

            ],

            "Value": [

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),

                len(self.df),

                len(self.df.columns),

                len(

                    self.df.select_dtypes(

                        include="number"

                    ).columns

                ),

                int(

                    self.df.isna()

                    .sum()

                    .sum()

                )

            ]

        })

    # --------------------------------------------------

    def score_summary(self):

        score_columns = [

            column

            for column in self.df.columns

            if column.endswith("Score")

        ]

        if not score_columns:

            return pd.DataFrame()

        return (

            self.df[score_columns]

            .describe()

            .T

            .reset_index()

            .rename(

                columns={

                    "index":

                        "Score"

                }

            )

        )

    # --------------------------------------------------

    def recommendation_summary(self):

        if "Recommendation" not in self.df.columns:

            return pd.DataFrame()

        summary = (

            self.df["Recommendation"]

            .value_counts()

            .rename_axis(

                "Recommendation"

            )

            .reset_index(

                name="Count"

            )

        )

        summary["Percentage"] = (

            summary["Count"]

            /

            len(self.df)

            * 100

        ).round(2)

        return summary

    # --------------------------------------------------

    def top_strategies(
        self,
        limit: int = 10
    ):

        if "Composite Score" not in self.df.columns:

            return pd.DataFrame()

        columns = [

            column

            for column in [

                "Stock",

                "Composite Score",

                "Institutional Score",

                "Recommendation"

            ]

            if column in self.df.columns

        ]

        return (

            self.df

            .sort_values(

                "Composite Score",

                ascending=False

            )

            [columns]

            .head(limit)

            .reset_index(

                drop=True

            )

        )

    # --------------------------------------------------

    def bottom_strategies(
        self,
        limit: int = 10
    ):

        if "Composite Score" not in self.df.columns:

            return pd.DataFrame()

        columns = [

            column

            for column in [

                "Stock",

                "Composite Score",

                "Institutional Score",

                "Recommendation"

            ]

            if column in self.df.columns

        ]

        return (

            self.df

            .sort_values(

                "Composite Score",

                ascending=True

            )

            [columns]

            .head(limit)

            .reset_index(

                drop=True

            )

        )

    # --------------------------------------------------

    def generate(self):

        logger.info(

            "Generating Summary Report..."

        )

        report = {

            "Dataset Information":

                self.dataset_information(),

            "Score Summary":

                self.score_summary(),

            "Recommendation Summary":

                self.recommendation_summary(),

            "Top Strategies":

                self.top_strategies(),

            "Bottom Strategies":

                self.bottom_strategies()

        }

        logger.info(

            "Summary report generated."

        )

        return report


if __name__ == "__main__":

    print(

        "Import inside report_engine.py"

    )