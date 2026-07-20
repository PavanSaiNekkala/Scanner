"""
============================================================
Institutional Strategy Comparison Engine V3
File : visualization/heatmaps.py

Heatmap Visualization Engine

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


class HeatmapVisualizer:
    """
    Institutional Heatmap Generator.

    Generates Pearson correlation heatmaps
    for all numeric features.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        output_directory: str = "outputs/charts",
        dpi: int = 300,
    ):
        self.df = dataframe.copy()

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.dpi = dpi

    # -----------------------------------------------------

    def correlation_matrix(self):
        numeric = self.df.select_dtypes(include=np.number)

        return numeric.corr()

    # -----------------------------------------------------

    def save(self, filename: str = "correlation_heatmap.png") -> str:
        logger.info("Generating heatmap...")

        corr = self.correlation_matrix()

        fig, ax = plt.subplots(figsize=(14, 12))

        image = ax.imshow(corr.values, interpolation="nearest", aspect="auto")

        ax.set_xticks(np.arange(len(corr.columns)))

        ax.set_yticks(np.arange(len(corr.columns)))

        ax.set_xticklabels(corr.columns, rotation=90, fontsize=8)

        ax.set_yticklabels(corr.columns, fontsize=8)

        plt.colorbar(image, ax=ax, shrink=0.8)

        plt.title("Correlation Heatmap", fontsize=16, fontweight="bold")

        plt.tight_layout()

        output_file = self.output_directory / filename

        plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        plt.close(fig)

        logger.info("Heatmap saved to %s", output_file)

        return str(output_file)

    # -----------------------------------------------------

    def top_correlations(self, limit: int = 20) -> pd.DataFrame:
        corr = self.correlation_matrix()

        pairs = []

        columns = corr.columns.tolist()

        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                pairs.append(
                    {
                        "Feature A": columns[i],
                        "Feature B": columns[j],
                        "Correlation": corr.iloc[i, j],
                        "Absolute": abs(corr.iloc[i, j]),
                    }
                )

        result = (
            pd.DataFrame(pairs)
            .sort_values("Absolute", ascending=False)
            .head(limit)
            .reset_index(drop=True)
        )

        return result


if __name__ == "__main__":
    print("Import inside dashboards.py")
