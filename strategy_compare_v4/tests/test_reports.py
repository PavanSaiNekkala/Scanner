"""
=============================================================
Institutional Strategy Comparison Platform V4

File:
    tests/test_reports.py

Purpose:
    Unit tests for reporting modules.

=============================================================
"""

from pathlib import Path

import pandas as pd

from reports.excel_exporter import ExcelExporter
from reports.charts import (
    composite_score_chart,
    edge_score_chart,
    recommendation_chart,
    expectancy_profit_chart,
    reliability_efficiency_chart,
    correlation_heatmap,
    portfolio_chart,
)
from reports.dashboard import load_data


###############################################################################
# Sample Comparison Data
###############################################################################

def comparison_dataframe():

    return pd.DataFrame({

        "Stock": [

            "ABC",

            "XYZ",

            "PQR"

        ],

        "Composite Score": [

            92,

            81,

            75

        ],

        "Edge Score": [

            90,

            79,

            72

        ],

        "Reliability Score": [

            91,

            78,

            70

        ],

        "Efficiency Score": [

            88,

            76,

            69

        ],

        "Expectancy": [

            4.2,

            2.6,

            1.7

        ],

        "Profit Factor": [

            2.4,

            1.8,

            1.4

        ],

        "Recommendation": [

            "Strong Buy",

            "Buy",

            "Watch"

        ]

    })


###############################################################################
# Portfolio Sample
###############################################################################

def portfolio_dataframe():

    return pd.DataFrame({

        "Stock": [

            "ABC",

            "XYZ",

            "PQR"

        ],

        "Weight": [

            45,

            35,

            20

        ]

    })


###############################################################################
# Correlation Matrix
###############################################################################

def correlation_dataframe():

    return pd.DataFrame(

        [

            [1.0,0.70,0.45],

            [0.70,1.0,0.62],

            [0.45,0.62,1.0]

        ],

        columns=[

            "S1",

            "S2",

            "S3"

        ],

        index=[

            "S1",

            "S2",

            "S3"

        ]

    )


###############################################################################
# Composite Chart
###############################################################################

def test_composite_chart():

    figure = composite_score_chart(

        comparison_dataframe()

    )

    assert figure is not None


###############################################################################
# Edge Chart
###############################################################################

def test_edge_chart():

    figure = edge_score_chart(

        comparison_dataframe()

    )

    assert figure is not None


###############################################################################
# Recommendation Chart
###############################################################################

def test_recommendation_chart():

    figure = recommendation_chart(

        comparison_dataframe()

    )

    assert figure is not None


###############################################################################
# Expectancy Chart
###############################################################################

def test_expectancy_chart():

    figure = expectancy_profit_chart(

        comparison_dataframe()

    )

    assert figure is not None


###############################################################################
# Reliability Chart
###############################################################################

def test_reliability_chart():

    figure = reliability_efficiency_chart(

        comparison_dataframe()

    )

    assert figure is not None


###############################################################################
# Correlation Heatmap
###############################################################################

def test_heatmap():

    figure = correlation_heatmap(

        correlation_dataframe()

    )

    assert figure is not None


###############################################################################
# Portfolio Chart
###############################################################################

def test_portfolio_chart():

    figure = portfolio_chart(

        portfolio_dataframe()

    )

    assert figure is not None


###############################################################################
# Dashboard Load CSV
###############################################################################

def test_dashboard_load_csv(

    tmp_path

):

    df = comparison_dataframe()

    file = tmp_path / "sample.csv"

    df.to_csv(

        file,

        index=False

    )

    loaded = load_data(file)

    assert len(

        loaded

    ) == len(df)


###############################################################################
# Dashboard Load Excel
###############################################################################

def test_dashboard_load_excel(

    tmp_path

):

    df = comparison_dataframe()

    file = tmp_path / "sample.xlsx"

    df.to_excel(

        file,

        index=False

    )

    loaded = load_data(file)

    assert len(

        loaded

    ) == len(df)


###############################################################################
# Excel Exporter
###############################################################################

def test_excel_exporter(

    tmp_path

):

    exporter = ExcelExporter(

        tmp_path / "report.xlsx"

    )

    assert exporter is not None


###############################################################################
# Export File Creation
###############################################################################

def test_excel_file_created(

    tmp_path

):

    file = tmp_path / "report.xlsx"

    exporter = ExcelExporter(file)

    exporter.create_workbook()

    exporter.save()

    assert Path(file).exists()