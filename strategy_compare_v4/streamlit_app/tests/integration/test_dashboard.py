"""
Integration tests.
"""

from __future__ import annotations

from services.portfolio_service import PortfolioService


def test_dashboard_pipeline(sample_dataframe):
    service = PortfolioService(sample_dataframe)

    summary = service.summary()

    assert summary is not None

    assert "Total Holdings" in summary

    assert "Portfolio Score" in summary
