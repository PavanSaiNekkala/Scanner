"""
============================================================
Institutional Strategy Comparison Engine V3
File : visualization/boxplots.py

Boxplot Visualization Engine

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


class BoxplotVisualizer:
    """
    Institutional Boxplot Generator.

    Generates boxplots for every
    numeric feature and reports
    outlier statistics.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        output_directory: str = "outputs/charts/boxplots",
        dpi: int = 300,
    ):
        self.df = dataframe.copy()

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.dpi = dpi

    # --------------------------------------------------

    def numeric_columns(self):
        return self.df.select_dtypes(include=np.number).columns.tolist()

    # --------------------------------------------------

    def generate_boxplot(
        self,
        column: str,
    ) -> str:
        logger.info("Generating boxplot: %s", column)

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.boxplot(self.df[column].dropna(), vert=True, patch_artist=False)

        ax.set_title(f"Boxplot - {column}", fontsize=14, fontweight="bold")

        ax.set_ylabel(column)

        plt.tight_layout()

        filename = (
            column.replace("/", "_").replace("%", "Pct").replace(" ", "_")
            + "_boxplot.png"
        )

        output_file = self.output_directory / filename

        plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        plt.close(fig)

        return str(output_file)

    # --------------------------------------------------

    def generate_all(self):
        outputs = {}

        for column in self.numeric_columns():
            outputs[column] = self.generate_boxplot(column)

        logger.info("Generated %d boxplots.", len(outputs))

        return outputs

    # --------------------------------------------------

    def outlier_statistics(self):
        summary = []

        for column in self.numeric_columns():
            series = self.df[column].dropna()

            q1 = series.quantile(0.25)

            q3 = series.quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr

            upper = q3 + 1.5 * iqr

            outliers = series[(series < lower) | (series > upper)]

            summary.append(
                {
                    "Feature": column,
                    "Q1": q1,
                    "Median": series.median(),
                    "Q3": q3,
                    "IQR": iqr,
                    "Lower Bound": lower,
                    "Upper Bound": upper,
                    "Outliers": len(outliers),
                    "Outlier %": round(len(outliers) / len(series) * 100, 2),
                }
            )

        return pd.DataFrame(summary)

    # --------------------------------------------------

    def generate(self):
        return {
            "Files": self.generate_all(),
            "Outlier Statistics": self.outlier_statistics(),
        }


if __name__ == "__main__":
    print("Import inside dashboards.py")
