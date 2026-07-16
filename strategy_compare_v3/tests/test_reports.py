"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Report Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from reports.summary_report import SummaryReport
from reports.institutional_report import InstitutionalReport
from reports.excel_report import ExcelReport
from reports.report_engine import ReportEngine


# ==========================================================
# Summary Report
# ==========================================================

def test_summary_report(scored_dataframe):

    report = SummaryReport(

        scored_dataframe

    )

    result = report.generate()

    assert isinstance(

        result,

        dict

    )


# ==========================================================
# Institutional Report
# ==========================================================

def test_institutional_report(scored_dataframe):

    report = InstitutionalReport(

        scored_dataframe

    )

    result = report.generate()

    assert isinstance(

        result,

        dict

    )


# ==========================================================
# Excel Report
# ==========================================================

def test_excel_report(

    scored_dataframe,

    tmp_path

):

    report = SummaryReport(

        scored_dataframe

    ).generate()

    exporter = ExcelReport(

        output_directory=tmp_path

    )

    file = exporter.generate(

        report

    )

    assert Path(

        file

    ).exists()


# ==========================================================
# Report Engine
# ==========================================================

def test_report_engine(

    scored_dataframe,

    tmp_path

):

    engine = ReportEngine(

        scored_dataframe,

        output_directory=tmp_path

    )

    result = engine.run()

    assert isinstance(

        result,

        dict

    )

    assert "Summary Report" in result

    assert "Institutional Report" in result

    assert "Excel File" in result


# ==========================================================
# Excel Workbook Exists
# ==========================================================

def test_excel_file_created(

    scored_dataframe,

    tmp_path

):

    engine = ReportEngine(

        scored_dataframe,

        output_directory=tmp_path

    )

    result = engine.run()

    assert Path(

        result["Excel File"]

    ).exists()


# ==========================================================
# Empty Dataset
# ==========================================================

def test_empty_dataframe():

    engine = ReportEngine(

        pd.DataFrame()

    )

    with pytest.raises(Exception):

        engine.run()


# ==========================================================
# Single Row
# ==========================================================

def test_single_row(tmp_path):

    df = pd.DataFrame({

        "Stock": ["ABC"],

        "Composite Score": [90],

        "Institutional Score": [88],

        "Recommendation": ["BUY"]

    })

    engine = ReportEngine(

        df,

        output_directory=tmp_path

    )

    result = engine.run()

    assert isinstance(

        result,

        dict

    )


# ==========================================================
# Repeatability
# ==========================================================

def test_repeatability(

    scored_dataframe,

    tmp_path

):

    engine = ReportEngine(

        scored_dataframe,

        output_directory=tmp_path

    )

    first = engine.run()

    second = engine.run()

    assert first.keys() == second.keys()


# ==========================================================
# Summary Sections
# ==========================================================

def test_summary_sections(

    scored_dataframe

):

    report = SummaryReport(

        scored_dataframe

    ).generate()

    expected = [

        "Dataset Information",

        "Score Summary",

        "Recommendation Summary"

    ]

    for section in expected:

        if section in report:

            assert isinstance(

                report[section],

                pd.DataFrame

            )


# ==========================================================
# Institutional Sections
# ==========================================================

def test_institutional_sections(

    scored_dataframe

):

    report = InstitutionalReport(

        scored_dataframe

    ).generate()

    expected = [

        "Executive Summary",

        "Recommendation Distribution",

        "Top Strategies"

    ]

    for section in expected:

        if section in report:

            assert isinstance(

                report[section],

                pd.DataFrame

            )


# ==========================================================
# Performance
# ==========================================================

def test_large_dataset(

    tmp_path

):

    rows = 5000

    df = pd.DataFrame({

        "Stock":

            [f"S{i}" for i in range(rows)],

        "Composite Score":

            [80] * rows,

        "Institutional Score":

            [75] * rows,

        "Recommendation":

            ["BUY"] * rows

    })

    engine = ReportEngine(

        df,

        output_directory=tmp_path

    )

    result = engine.run()

    assert isinstance(

        result,

        dict

    )