"""
Unit tests for services.
"""

from __future__ import annotations

from services.portfolio_service import PortfolioService


def test_portfolio_weight(sample_dataframe):
    service = PortfolioService(sample_dataframe)

    assert service.total_weight() == 100


def test_average_weight(sample_dataframe):
    service = PortfolioService(sample_dataframe)

    assert service.average_weight() > 0


def test_health_score(sample_dataframe):
    service = PortfolioService(sample_dataframe)

    score = service.health_score()

    assert score >= 0


def test_summary(sample_dataframe):
    service = PortfolioService(sample_dataframe)

    summary = service.summary()

    assert isinstance(summary, dict)
