"""
============================================================
Institutional Strategy Comparison Engine V3

Pytest Configuration & Shared Fixtures

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ============================================================
# Random Seed
# ============================================================

np.random.seed(42)

# ============================================================
# Sample Dataset
# ============================================================


@pytest.fixture(scope="session")
def sample_dataframe():

    rows = 100

    return pd.DataFrame({

        "Stock":

            [f"STOCK_{i}" for i in range(rows)],

        "Expectancy%":

            np.random.uniform(5, 40, rows),

        "Profit Factor":

            np.random.uniform(0.8, 4.5, rows),

        "Reward Risk":

            np.random.uniform(0.5, 6.0, rows),

        "Trades":

            np.random.randint(20, 400, rows),

        "Trades / Year":

            np.random.uniform(5, 120, rows),

        "Win %":

            np.random.uniform(25, 90, rows),

        "Signal Quality":

            np.random.uniform(40, 100, rows),

        "Holding Efficiency":

            np.random.uniform(20, 100, rows),

        "Winning Exit %":

            np.random.uniform(40, 95, rows),

        "Losing Exit %":

            np.random.uniform(5, 60, rows),

        "Profit Velocity":

            np.random.uniform(0.5, 8.0, rows)

    })


# ============================================================
# Temporary CSV
# ============================================================


@pytest.fixture()
def sample_csv(

    sample_dataframe,

    tmp_path

):

    file = tmp_path / "sample.csv"

    sample_dataframe.to_csv(

        file,

        index=False

    )

    return file


# ============================================================
# Temporary Excel
# ============================================================


@pytest.fixture()
def sample_excel(

    sample_dataframe,

    tmp_path

):

    file = tmp_path / "sample.xlsx"

    sample_dataframe.to_excel(

        file,

        index=False

    )

    return file


# ============================================================
# Output Directory
# ============================================================


@pytest.fixture()
def output_directory(

    tmp_path

):

    directory = tmp_path / "outputs"

    directory.mkdir()

    return directory


# ============================================================
# Temporary Working Directory
# ============================================================


@pytest.fixture()
def working_directory(

    tmp_path,

    monkeypatch

):

    monkeypatch.chdir(

        tmp_path

    )

    return tmp_path


# ============================================================
# Dummy Recommendation Dataset
# ============================================================


@pytest.fixture()
def scored_dataframe(

    sample_dataframe

):

    df = sample_dataframe.copy()

    df["Edge Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Risk Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Efficiency Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Stability Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Reliability Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Opportunity Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Execution Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Institutional Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    df["Composite Score"] = np.random.uniform(

        60,

        100,

        len(df)

    )

    return df


# ============================================================
# Cleanup
# ============================================================


@pytest.fixture(autouse=True)
def cleanup_outputs():

    yield

    outputs = Path("outputs")

    if outputs.exists():

        shutil.rmtree(

            outputs,

            ignore_errors=True

        )