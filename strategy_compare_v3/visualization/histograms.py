"""
============================================================
Institutional Strategy Comparison Engine V3
File : visualization/histograms.py

Histogram Visualization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.logger import get_logger

logger = get_logger(__name__)


class HistogramVisualizer:
    """
    Institutional Histogram Generator.

    Generates histogram plots for every
    numeric feature in the dataset.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        output_directory: str = "outputs/charts/histograms",
        bins: int = 30,
        dpi: int = 300,
    ):

        self.df = dataframe.copy()

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.bins = bins

        self.dpi = dpi

    # -----------------------------------------------------

    def numeric_columns(self):

        return self.df.select_dtypes(
            include=np.number
        ).columns.tolist()

    # -----------------------------------------------------

    def generate_histogram(
        self,
        column: str,
    ) -> str:

        logger.info(
            "Generating histogram: %s",
            column
        )

        fig, ax = plt.subplots(
            figsize=(8, 5)
        )

        ax.hist(
            self.df[column].dropna(),
            bins=self.bins
        )

        ax.set_title(
            f"Histogram - {column}",
            fontsize=14,
            fontweight="bold"
        )

        ax.set_xlabel(column)

        ax.set_ylabel("Frequency")

        plt.tight_layout()

        filename = (

            column

            .replace("/", "_")

            .replace("%", "Pct")

            .replace(" ", "_")

            + "_histogram.png"

        )

        output_file = self.output_directory / filename

        plt.savefig(
            output_file,
            dpi=self.dpi,
            bbox_inches="tight"
        )

        plt.close(fig)

        return str(output_file)

    # -----------------------------------------------------

    def generate_all(self):

        logger.info(
            "Generating all histograms..."
        )

        outputs = {}

        for column in self.numeric_columns():

            outputs[column] = self.generate_histogram(
                column
            )

        logger.info(
            "Generated %d histograms.",
            len(outputs)
        )

        return outputs

    # -----------------------------------------------------

    def statistics(self):

        numeric = self.df.select_dtypes(
            include=np.number
        )

        summary = []

        for column in numeric.columns:

            summary.append({

                "Feature":

                    column,

                "Mean":

                    numeric[column].mean(),

                "Median":

                    numeric[column].median(),

                "Std":

                    numeric[column].std(),

                "Variance":

                    numeric[column].var(),

                "Minimum":

                    numeric[column].min(),

                "Maximum":

                    numeric[column].max(),

                "Skewness":

                    numeric[column].skew(),

                "Kurtosis":

                    numeric[column].kurt()

            })

        return pd.DataFrame(summary)

    # -----------------------------------------------------

    def generate(self):

        return {

            "Files":

                self.generate_all(),

            "Statistics":

                self.statistics()

        }


if __name__ == "__main__":

    print(
        "Import inside dashboards.py"
    )