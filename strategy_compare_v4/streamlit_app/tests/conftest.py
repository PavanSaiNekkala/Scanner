"""
Shared pytest fixtures.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "Stock": [
                "ABC",
                "XYZ",
                "PQR",
            ],
            "Institutional Score": [
                95.5,
                88.3,
                79.1,
            ],
            "Recommendation": [
                "STRONG BUY",
                "BUY",
                "WATCH",
            ],
            "Weight %": [
                40,
                35,
                25,
            ],
        }
    )
