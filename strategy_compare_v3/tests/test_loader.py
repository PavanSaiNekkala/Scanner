"""
============================================================
Institutional Strategy Comparison Engine V3

Unit Tests - Data Loader

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from core.loader import DataLoader

# ==========================================================
# CSV Loading
# ==========================================================


def test_load_csv(sample_csv):
    loader = DataLoader(sample_csv)

    df = loader.load()

    assert isinstance(df, pd.DataFrame)

    assert len(df) == 100

    assert "Stock" in df.columns


# ==========================================================
# Excel Loading
# ==========================================================


def test_load_excel(sample_excel):
    loader = DataLoader(sample_excel)

    df = loader.load()

    assert isinstance(df, pd.DataFrame)

    assert len(df) == 100

    assert "Stock" in df.columns


# ==========================================================
# Invalid File
# ==========================================================


def test_invalid_file():
    with pytest.raises(FileNotFoundError):
        loader = DataLoader(Path("invalid_file.csv"))

        loader.load()


# ==========================================================
# Unsupported Extension
# ==========================================================


def test_invalid_extension(tmp_path):
    file = tmp_path / "sample.txt"

    file.write_text("invalid")

    loader = DataLoader(file)

    with pytest.raises(ValueError):
        loader.load()


# ==========================================================
# Empty CSV
# ==========================================================


def test_empty_csv(tmp_path):
    file = tmp_path / "empty.csv"

    pd.DataFrame().to_csv(file, index=False)

    loader = DataLoader(file)

    df = loader.load()

    assert isinstance(df, pd.DataFrame)

    assert df.empty


# ==========================================================
# Empty Excel
# ==========================================================


def test_empty_excel(tmp_path):
    file = tmp_path / "empty.xlsx"

    pd.DataFrame().to_excel(file, index=False)

    loader = DataLoader(file)

    df = loader.load()

    assert isinstance(df, pd.DataFrame)

    assert df.empty


# ==========================================================
# Data Types
# ==========================================================


def test_dataframe_types(sample_csv):
    loader = DataLoader(sample_csv)

    df = loader.load()

    assert df["Stock"].dtype == object

    assert pd.api.types.is_numeric_dtype(df["Expectancy%"])


# ==========================================================
# Duplicate Load
# ==========================================================


def test_multiple_loads(sample_csv):
    loader = DataLoader(sample_csv)

    df1 = loader.load()

    df2 = loader.load()

    pd.testing.assert_frame_equal(df1, df2)


# ==========================================================
# Missing Columns
# ==========================================================


def test_missing_columns(tmp_path):
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

    file = tmp_path / "missing.csv"

    df.to_csv(file, index=False)

    loader = DataLoader(file)

    loaded = loader.load()

    assert isinstance(loaded, pd.DataFrame)


# ==========================================================
# Large Dataset
# ==========================================================


def test_large_dataset(tmp_path):
    rows = 50000

    df = pd.DataFrame(
        {
            "Stock": [f"S{i}" for i in range(rows)],
            "Expectancy%": range(rows),
            "Profit Factor": range(rows),
        }
    )

    file = tmp_path / "large.csv"

    df.to_csv(file, index=False)

    loader = DataLoader(file)

    loaded = loader.load()

    assert len(loaded) == rows
