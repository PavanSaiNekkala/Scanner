"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Visualization Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from visualization.heatmaps import HeatmapVisualizer
from visualization.histograms import HistogramVisualizer
from visualization.boxplots import BoxplotVisualizer
from visualization.scatterplots import ScatterPlotVisualizer
from visualization.dashboards import DashboardEngine


# ==========================================================
# Heatmap
# ==========================================================

def test_heatmap(sample_dataframe, tmp_path):

    engine = HeatmapVisualizer(

        sample_dataframe,

        output_directory=tmp_path

    )

    result = engine.save()

    assert Path(result).exists()


# ==========================================================
# Histogram
# ==========================================================

def test_histograms(sample_dataframe, tmp_path):

    engine = HistogramVisualizer(

        sample_dataframe,

        output_directory=tmp_path

    )

    result = engine.generate()

    assert isinstance(result, dict)

    assert "Files" in result

    assert len(result["Files"]) > 0


# ==========================================================
# Boxplots
# ==========================================================

def test_boxplots(sample_dataframe, tmp_path):

    engine = BoxplotVisualizer(

        sample_dataframe,

        output_directory=tmp_path

    )

    result = engine.generate()

    assert isinstance(result, dict)

    assert "Files" in result


# ==========================================================
# Scatterplots
# ==========================================================

def test_scatterplots(sample_dataframe, tmp_path):

    engine = ScatterPlotVisualizer(

        sample_dataframe,

        output_directory=tmp_path

    )

    result = engine.generate()

    assert isinstance(result, dict)


# ==========================================================
# Dashboard
# ==========================================================

def test_dashboard(sample_dataframe, tmp_path):

    engine = DashboardEngine(

        sample_dataframe,

        output_directory=tmp_path

    )

    result = engine.run()

    assert isinstance(result, dict)

    assert "Heatmaps" in result

    assert "Histograms" in result

    assert "Boxplots" in result

    assert "Scatterplots" in result


# ==========================================================
# Output Files
# ==========================================================

def test_chart_files_created(sample_dataframe, tmp_path):

    engine = HistogramVisualizer(

        sample_dataframe,

        output_directory=tmp_path

    )

    engine.generate()

    files = list(

        tmp_path.rglob("*.png")

    )

    assert len(files) > 0


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_empty_dataframe():

    engine = DashboardEngine(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        engine.run()


# ==========================================================
# Single Row
# ==========================================================

def test_single_row():

    df = pd.DataFrame({

        "A": [1],

        "B": [2]

    })

    engine = DashboardEngine(df)

    result = engine.run()

    assert isinstance(result, dict)


# ==========================================================
# Repeatability
# ==========================================================

def test_repeatability(sample_dataframe, tmp_path):

    engine = DashboardEngine(

        sample_dataframe,

        output_directory=tmp_path

    )

    first = engine.run()

    second = engine.run()

    assert first.keys() == second.keys()


# ==========================================================
# Performance
# ==========================================================

def test_large_dataset(tmp_path):

    rows = 5000

    df = pd.DataFrame({

        "A": range(rows),

        "B": range(rows),

        "C": range(rows)

    })

    engine = DashboardEngine(

        df,

        output_directory=tmp_path

    )

    result = engine.run()

    assert isinstance(result, dict)


# ==========================================================
# Statistics
# ==========================================================

def test_histogram_statistics(sample_dataframe, tmp_path):

    engine = HistogramVisualizer(

        sample_dataframe,

        output_directory=tmp_path

    )

    result = engine.generate()

    assert "Statistics" in result

    assert isinstance(

        result["Statistics"],

        pd.DataFrame

    )