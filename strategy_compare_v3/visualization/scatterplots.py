"""
============================================================
Institutional Strategy Comparison Engine V3
File : visualization/scatterplots.py

Scatter Plot Visualization Engine

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


class ScatterPlotVisualizer:
    """
    Institutional Scatter Plot Generator.

    Generates scatter plots for selected
    pairs of important institutional metrics.
    """

    DEFAULT_PAIRS = [

        ("Expectancy%", "Profit Factor"),

        ("Win %", "Expectancy%"),

        ("Edge Score", "Composite Score"),

        ("Risk Score", "Composite Score"),

        ("Efficiency Score", "Composite Score"),

        ("Reliability Score", "Composite Score"),

        ("Institutional Score", "Composite Score"),

        ("Trades", "Win %"),

        ("Trades", "Profit Factor"),

        ("Reward Risk Ratio", "Profit Factor")

    ]

    def __init__(
        self,
        dataframe: pd.DataFrame,
        output_directory: str = "outputs/charts/scatterplots",
        dpi: int = 300
    ):

        self.df = dataframe.copy()

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(

            parents=True,

            exist_ok=True

        )

        self.dpi = dpi

    # --------------------------------------------------

    def generate_plot(
        self,
        x: str,
        y: str
    ):

        if x not in self.df.columns:

            return None

        if y not in self.df.columns:

            return None

        logger.info(

            "Generating scatter plot %s vs %s",

            x,

            y

        )

        fig, ax = plt.subplots(

            figsize=(8, 6)

        )

        ax.scatter(

            self.df[x],

            self.df[y],

            alpha=0.70

        )

        ax.set_xlabel(x)

        ax.set_ylabel(y)

        ax.set_title(

            f"{x} vs {y}",

            fontsize=14,

            fontweight="bold"

        )

        plt.tight_layout()

        filename = (

            f"{x}_vs_{y}"

            .replace("/", "_")

            .replace("%", "Pct")

            .replace(" ", "_")

            + ".png"

        )

        output_file = (

            self.output_directory

            / filename

        )

        plt.savefig(

            output_file,

            dpi=self.dpi,

            bbox_inches="tight"

        )

        plt.close(fig)

        return str(output_file)

    # --------------------------------------------------

    def correlation_table(self):

        rows = []

        for x, y in self.DEFAULT_PAIRS:

            if x not in self.df.columns:

                continue

            if y not in self.df.columns:

                continue

            corr = self.df[[x, y]].corr().iloc[0, 1]

            rows.append({

                "X":

                    x,

                "Y":

                    y,

                "Correlation":

                    round(corr, 4)

            })

        return pd.DataFrame(rows)

    # --------------------------------------------------

    def generate_all(self):

        files = {}

        for x, y in self.DEFAULT_PAIRS:

            result = self.generate_plot(

                x,

                y

            )

            if result:

                files[f"{x} vs {y}"] = result

        logger.info(

            "%d scatter plots generated.",

            len(files)

        )

        return files

    # --------------------------------------------------

    def generate(self):

        return {

            "Files":

                self.generate_all(),

            "Correlations":

                self.correlation_table()

        }


if __name__ == "__main__":

    print(

        "Import inside dashboards.py"

    )