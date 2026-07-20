"""
============================================================
Institutional Strategy Comparison Engine V3
File : visualization/dashboards.py

Master Dashboard Visualization Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from core.logger import get_logger

from visualization.heatmaps import HeatmapVisualizer
from visualization.histograms import HistogramVisualizer
from visualization.boxplots import BoxplotVisualizer
from visualization.scatterplots import ScatterPlotVisualizer

logger = get_logger(__name__)


class DashboardEngine:
    """
    Institutional Dashboard Engine.

    Coordinates every visualization module
    and produces a unified dashboard report.
    """

    def __init__(
        self, dataframe: pd.DataFrame, output_directory: str = "outputs/charts"
    ):
        self.df = dataframe.copy()

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(parents=True, exist_ok=True)

        self.results: Dict[str, Any] = {}

        self.execution_time = 0.0

    # --------------------------------------------------

    def heatmaps(self):
        engine = HeatmapVisualizer(self.df, output_directory=self.output_directory)

        return {"Chart": engine.save(), "Correlations": engine.top_correlations()}

    # --------------------------------------------------

    def histograms(self):
        engine = HistogramVisualizer(self.df, output_directory=self.output_directory)

        return engine.generate()

    # --------------------------------------------------

    def boxplots(self):
        engine = BoxplotVisualizer(self.df, output_directory=self.output_directory)

        return engine.generate()

    # --------------------------------------------------

    def scatterplots(self):
        engine = ScatterPlotVisualizer(self.df, output_directory=self.output_directory)

        return engine.generate()

    # --------------------------------------------------

    def run(self):
        logger.info("=" * 80)

        logger.info("Generating Dashboard...")

        start = time.perf_counter()

        self.results["Heatmaps"] = self.heatmaps()

        self.results["Histograms"] = self.histograms()

        self.results["Boxplots"] = self.boxplots()

        self.results["Scatterplots"] = self.scatterplots()

        self.execution_time = round(time.perf_counter() - start, 3)

        self.results["Execution Time"] = self.execution_time

        logger.info("Dashboard generated in %.3f seconds.", self.execution_time)

        logger.info("=" * 80)

        return self.results

    # --------------------------------------------------

    def summary(self):
        return {
            "Modules": ["Heatmaps", "Histograms", "Boxplots", "Scatterplots"],
            "Execution Time": self.execution_time,
        }


if __name__ == "__main__":
    print("Import inside main.py")
