"""
portfolio_service.py
====================

Institutional Portfolio Analytics Service
"""

from __future__ import annotations

import pandas as pd


class PortfolioService:
    """
    Portfolio analytics service.
    """

    def __init__(self, portfolio: pd.DataFrame):
        self.df = portfolio.copy()

    # =====================================================
    # Basic Statistics
    # =====================================================

    def holdings(self) -> int:
        return len(self.df)

    def average_weight(self) -> float:
        if "Weight %" not in self.df.columns:
            return 0

        return round(
            float(self.df["Weight %"].mean()),
            2,
        )

    def total_weight(self) -> float:
        if "Weight %" not in self.df.columns:
            return 0

        return round(
            float(self.df["Weight %"].sum()),
            2,
        )

    # =====================================================
    # Expected Return
    # =====================================================

    def expected_return(self):
        if (
            "Weight %" not in self.df.columns
            or "Expected Return %" not in self.df.columns
        ):
            return 0

        weights = self.df["Weight %"] / 100

        returns = self.df["Expected Return %"]

        return round(
            float((weights * returns).sum()),
            2,
        )

    # =====================================================
    # Portfolio Score
    # =====================================================

    def portfolio_score(self):
        score = None

        for col in [
            "Institutional Score",
            "Composite Score",
            "Edge Score",
        ]:
            if col in self.df.columns:
                score = col

                break

        if score is None:
            return 0

        return round(
            float(self.df[score].mean()),
            2,
        )

    # =====================================================
    # Concentration (HHI)
    # =====================================================

    def concentration(self):
        if "Weight %" not in self.df.columns:
            return 0

        w = self.df["Weight %"] / 100

        return round(
            float((w**2).sum()),
            4,
        )

    # =====================================================
    # Effective Holdings
    # =====================================================

    def effective_holdings(self):
        hhi = self.concentration()

        if hhi == 0:
            return 0

        return round(
            float(1 / hhi),
            2,
        )

    # =====================================================
    # Normalize Weights
    # =====================================================

    def normalize_weights(self):
        if "Weight %" not in self.df.columns:
            return self.df

        total = self.df["Weight %"].sum()

        if total == 0:
            return self.df

        self.df["Normalized Weight %"] = self.df["Weight %"] / total * 100

        return self.df

    # =====================================================
    # Top Holdings
    # =====================================================

    def top_holdings(
        self,
        n=10,
    ):
        if "Weight %" not in self.df.columns:
            return self.df.head(n)

        return self.df.sort_values(
            "Weight %",
            ascending=False,
        ).head(n)

    # =====================================================
    # Bottom Holdings
    # =====================================================

    def bottom_holdings(
        self,
        n=10,
    ):
        if "Weight %" not in self.df.columns:
            return self.df.tail(n)

        return self.df.sort_values(
            "Weight %",
            ascending=True,
        ).head(n)

    # =====================================================
    # Sector Allocation
    # =====================================================

    def sector_allocation(self):
        if "Sector" not in self.df.columns or "Weight %" not in self.df.columns:
            return pd.DataFrame()

        return (
            self.df.groupby("Sector")["Weight %"]
            .sum()
            .reset_index()
            .sort_values(
                "Weight %",
                ascending=False,
            )
        )

    # =====================================================
    # Recommendation Mix
    # =====================================================

    def recommendation_mix(self):
        if "Recommendation" not in self.df.columns:
            return pd.DataFrame()

        return (
            self.df["Recommendation"]
            .value_counts()
            .rename_axis("Recommendation")
            .reset_index(name="Count")
        )

    # =====================================================
    # Risk Summary
    # =====================================================

    def risk_summary(self):
        cols = [
            c
            for c in [
                "Risk Score",
                "Max Drawdown %",
                "Volatility",
                "Recovery Factor",
            ]
            if c in self.df.columns
        ]

        if not cols:
            return pd.DataFrame()

        return self.df[cols].describe().T

    # =====================================================
    # Performance Summary
    # =====================================================

    def performance_summary(self):
        cols = [
            c
            for c in [
                "Expectancy%",
                "Profit Factor",
                "Reward Risk",
                "Annual Return %",
            ]
            if c in self.df.columns
        ]

        if not cols:
            return pd.DataFrame()

        return self.df[cols].describe().T

    # =====================================================
    # Complete Dashboard Summary
    # =====================================================

    def summary(self):
        return {
            "Holdings": self.holdings(),
            "Total Weight": self.total_weight(),
            "Average Weight": self.average_weight(),
            "Portfolio Score": self.portfolio_score(),
            "Expected Return": self.expected_return(),
            "HHI": self.concentration(),
            "Effective Holdings": self.effective_holdings(),
        }

    # =====================================================
    # Health Score
    # =====================================================

    def health_score(self):
        score = 100

        if self.total_weight() < 99:
            score -= 20

        if self.total_weight() > 101:
            score -= 20

        if self.concentration() > 0.15:
            score -= 20

        if self.effective_holdings() < 10:
            score -= 20

        return max(score, 0)

    # =====================================================
    # Export Summary
    # =====================================================

    def summary_dataframe(self):
        return pd.DataFrame([self.summary()])
