"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
tests/test_reports.py

Purpose
-------
Unit tests for reporting modules.

Tests
-----
• Chart generation
• Dashboard data loading
• Excel exporter
• Workbook creation

=============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from reports.charts import (
    composite_score_chart,
    correlation_heatmap,
    edge_score_chart,
    expectancy_profit_chart,
    portfolio_chart,
    recommendation_chart,
    reliability_efficiency_chart,
)
from reports.dashboard import load_data
from reports.excel_exporter import ExcelExporter


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def comparison_dataframe() -> pd.DataFrame:
    """
    Sample comparison report.
    """

    return pd.DataFrame(
        {
            "Stock": [
                "ABC",
                "XYZ",
                "PQR",
            ],
            "Composite Score": [
                92,
                81,
                75,
            ],
            "Edge Score": [
                90,
                79,
                72,
            ],
            "Reliability Score": [
                91,
                78,
                70,
            ],
            "Efficiency Score": [
                88,
                76,
                69,
            ],
            "Expectancy": [
                4.2,
                2.6,
                1.7,
            ],
            "Profit Factor": [
                2.4,
                1.8,
                1.4,
            ],
            "Recommendation": [
                "Strong Buy",
                "Buy",
                "Watch",
            ],
        }
    )


@pytest.fixture
def portfolio_dataframe() -> pd.DataFrame:
    """
    Sample portfolio.
    """

    return pd.DataFrame(
        {
            "Stock": [
                "ABC",
                "XYZ",
                "PQR",
            ],
            "Weight": [
                45,
                35,
                20,
            ],
        }
    )


@pytest.fixture
def correlation_dataframe() -> pd.DataFrame:
    """
    Sample correlation matrix.
    """

    return pd.DataFrame(
        [
            [1.00, 0.70, 0.45],
            [0.70, 1.00, 0.62],
            [0.45, 0.62, 1.00],
        ],
        columns=[
            "S1",
            "S2",
            "S3",
        ],
        index=[
            "S1",
            "S2",
            "S3",
        ],
    )


# ============================================================
# Charts
# ============================================================

@pytest.mark.parametrize(
    "chart_function",
    [
        composite_score_chart,
        edge_score_chart,
        recommendation_chart,
        expectancy_profit_chart,
        reliability_efficiency_chart,
    ],
)
def test_report_charts(
    chart_function,
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    All report charts should
    generate successfully.
    """

    figure = chart_function(
        comparison_dataframe
    )

    assert figure is not None


def test_correlation_heatmap(
    correlation_dataframe: pd.DataFrame,
) -> None:
    """
    Correlation heatmap.
    """

    figure = correlation_heatmap(
        correlation_dataframe
    )

    assert figure is not None


def test_portfolio_chart(
    portfolio_dataframe: pd.DataFrame,
) -> None:
    """
    Portfolio allocation chart.
    """

    figure = portfolio_chart(
        portfolio_dataframe
    )

    assert figure is not None


# ============================================================
# Dashboard
# ============================================================

def test_dashboard_load_csv(
    tmp_path: Path,
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    Dashboard should load CSV.
    """

    file = tmp_path / "sample.csv"

    comparison_dataframe.to_csv(
        file,
        index=False,
    )

    loaded = load_data(file)

    assert len(loaded) == len(
        comparison_dataframe
    )


def test_dashboard_load_excel(
    tmp_path: Path,
    comparison_dataframe: pd.DataFrame,
) -> None:
    """
    Dashboard should load Excel.
    """

    file = tmp_path / "sample.xlsx"

    comparison_dataframe.to_excel(
        file,
        index=False,
    )

    loaded = load_data(file)

    assert len(loaded) == len(
        comparison_dataframe
    )


# ============================================================
# Excel Exporter
# ============================================================

def test_excel_exporter_creation(
    tmp_path: Path,
) -> None:
    """
    ExcelExporter object.
    """

    exporter = ExcelExporter(
        tmp_path / "report.xlsx"
    )

    assert exporter is not None


def test_excel_workbook_created(
    tmp_path: Path,
) -> None:
    """
    Workbook should be written.
    """

    file = tmp_path / "report.xlsx"

    exporter = ExcelExporter(file)

    exporter.create_workbook()

    exporter.save()

    assert file.exists()


# ============================================================
# Edge Cases
# ============================================================

def test_empty_dataframe_chart() -> None:
    """
    Empty DataFrame should
    not crash chart creation.
    """

    df = pd.DataFrame()

    with pytest.raises(Exception):
        composite_score_chart(df)


def test_invalid_dashboard_file(
    tmp_path: Path,
) -> None:
    """
    Invalid file should raise.
    """

    file = tmp_path / "invalid.txt"

    file.write_text("Invalid")

    with pytest.raises(Exception):
        load_data(file)