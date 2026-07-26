"""
risk_manager.py
===============

Institutional Risk Management Engine

Evaluates portfolio risk using institutional-grade
portfolio analytics.

Responsibilities
----------------
• Position Risk
• Sector Exposure
• Portfolio Exposure
• Concentration
• Correlation
• Covariance
• Portfolio Beta
• Portfolio Volatility
• Historical VaR
• Parametric VaR
• Expected Shortfall (CVaR)
• Drawdown
• Stress Testing
• Constraint Validation
• Risk Scoring

No Streamlit dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import logging
import math

import numpy as np
import pandas as pd

from .portfolio_manager import (
    PortfolioResult,
)

# =============================================================================
# Logger
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True)
class RiskConfig:
    """
    Institutional portfolio risk settings.
    """

    # ---------------------------------------------------------
    # Position Limits
    # ---------------------------------------------------------

    max_position_weight: float = 0.08

    min_position_weight: float = 0.01

    # ---------------------------------------------------------
    # Sector Limits
    # ---------------------------------------------------------

    max_sector_weight: float = 0.25

    # ---------------------------------------------------------
    # Exposure
    # ---------------------------------------------------------

    max_gross_exposure: float = 1.00

    max_net_exposure: float = 1.00

    # ---------------------------------------------------------
    # Concentration
    # ---------------------------------------------------------

    max_hhi: float = 0.15

    min_effective_positions: int = 15

    # ---------------------------------------------------------
    # Portfolio Risk
    # ---------------------------------------------------------

    max_beta: float = 1.20

    max_volatility: float = 0.25

    max_drawdown: float = 0.20

    # ---------------------------------------------------------
    # VaR
    # ---------------------------------------------------------

    confidence_level: float = 0.95

    max_var: float = 0.03

    max_cvar: float = 0.05

    # ---------------------------------------------------------
    # Correlation
    # ---------------------------------------------------------

    max_correlation: float = 0.85

    # ---------------------------------------------------------
    # Annualization
    # ---------------------------------------------------------

    trading_days: int = 252

    risk_free_rate: float = 0.05


# =============================================================================
# Risk Statistics
# =============================================================================


@dataclass
class RiskStatistics:
    """
    Portfolio risk summary.
    """

    gross_exposure: float = 0.0

    net_exposure: float = 0.0

    portfolio_beta: float = 0.0

    volatility: float = 0.0

    annualized_volatility: float = 0.0

    value_at_risk: float = 0.0

    expected_shortfall: float = 0.0

    max_drawdown: float = 0.0

    hhi: float = 0.0

    effective_positions: float = 0.0

    largest_position: float = 0.0

    sector_count: int = 0

    violations: int = 0


# =============================================================================
# Result Model
# =============================================================================


@dataclass
class RiskResult:
    """
    Final risk evaluation.
    """

    portfolio: pd.DataFrame

    statistics: RiskStatistics

    violations: pd.DataFrame

    sector_exposure: pd.DataFrame

    correlation_matrix: pd.DataFrame

    covariance_matrix: pd.DataFrame

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# =============================================================================
# Risk Manager
# =============================================================================


class RiskManager:
    """
    Institutional portfolio risk engine.

    Workflow
    --------

        Portfolio
            │
            ▼
        Position Risk
            │
            ▼
        Exposure
            │
            ▼
        Concentration
            │
            ▼
        Correlation
            │
            ▼
        Volatility
            │
            ▼
        VaR
            │
            ▼
        Stress Tests
            │
            ▼
        Risk Report
    """

    def __init__(
        self,
        config: RiskConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else RiskConfig()
        )

        logger.info(
            "RiskManager initialized."
        )

    # =========================================================
    # Public API
    # =========================================================

    def evaluate(
        self,
        portfolio: PortfolioResult,
    ) -> RiskResult:
        """
        Perform institutional portfolio risk evaluation.
        """

        logger.info(
            "Starting portfolio risk evaluation."
        )

        positions = portfolio.portfolio.copy()

        if positions.empty:

            logger.warning(
                "Portfolio is empty."
            )

            empty = pd.DataFrame()

            return RiskResult(
                portfolio=empty,
                statistics=RiskStatistics(),
                violations=empty,
                sector_exposure=empty,
                correlation_matrix=empty,
                covariance_matrix=empty,
                metadata={
                    "status": "EMPTY",
                },
            )

        # -----------------------------------------------------
        # Position Validation
        # -----------------------------------------------------

        positions = self._validate_positions(
            positions,
        )

        # -----------------------------------------------------
        # Position Risk
        # -----------------------------------------------------

        positions = self._compute_position_risk(
            positions,
        )

        # -----------------------------------------------------
        # Sector Exposure
        # -----------------------------------------------------

        sector_exposure = (
            self._compute_sector_exposure(
                positions,
            )
        )

        # -----------------------------------------------------
        # Correlation
        # -----------------------------------------------------

        correlation = (
            self._compute_correlation_matrix(
                positions,
            )
        )

        # -----------------------------------------------------
        # Covariance
        # -----------------------------------------------------

        covariance = (
            self._compute_covariance_matrix(
                positions,
            )
        )

        # -----------------------------------------------------
        # Risk Metrics
        # -----------------------------------------------------

        statistics = self._compute_statistics(
            positions,
            sector_exposure,
            correlation,
        )

        # -----------------------------------------------------
        # Constraint Validation
        # -----------------------------------------------------

        violations = (
            self._detect_violations(
                positions,
                statistics,
                sector_exposure,
            )
        )

        logger.info(
            "Risk evaluation completed "
            "(violations=%d).",
            len(violations),
        )

        return RiskResult(
            portfolio=positions,
            statistics=statistics,
            violations=violations,
            sector_exposure=sector_exposure,
            correlation_matrix=correlation,
            covariance_matrix=covariance,
            metadata={
                "risk_score": self._risk_score(
                    statistics,
                    violations,
                ),
            },
        )

    

    def _validate_positions(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Validate portfolio before risk calculations.

        Returns
        -------
        pd.DataFrame
            Clean portfolio.
        """

        if portfolio.empty:

            logger.warning(
                "Portfolio is empty."
            )

            return portfolio.copy()

        portfolio = portfolio.copy()

        # -----------------------------------------------------
        # Required Columns
        # -----------------------------------------------------

        required = (
            "ticker",
            "weight",
        )

        missing = [
            column
            for column in required
            if column not in portfolio.columns
        ]

        if missing:

            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing)
            )

        # -----------------------------------------------------
        # Numeric Columns
        # -----------------------------------------------------

        numeric_columns = (
            "weight",
            "current_weight",
            "beta",
            "volatility",
            "market_cap",
        )

        for column in numeric_columns:

            if column not in portfolio.columns:
                continue

            portfolio[column] = pd.to_numeric(
                portfolio[column],
                errors="coerce",
            )

        # -----------------------------------------------------
        # Remove Duplicate Securities
        # -----------------------------------------------------

        portfolio = portfolio.drop_duplicates(
            subset="ticker",
            keep="first",
        )

        # -----------------------------------------------------
        # Remove Invalid Rows
        # -----------------------------------------------------

        portfolio = portfolio.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        portfolio = portfolio.dropna(
            subset=[
                "ticker",
                "weight",
            ]
        )

        # -----------------------------------------------------
        # Fill Optional Columns
        # -----------------------------------------------------

        defaults = {
            "beta": 1.0,
            "volatility": 0.0,
            "market_cap": 0.0,
            "current_weight": 0.0,
        }

        for column, value in defaults.items():

            if column in portfolio.columns:

                portfolio[column] = (
                    portfolio[column]
                    .fillna(value)
                )

        # -----------------------------------------------------
        # Normalize Weights
        # -----------------------------------------------------

        total_weight = portfolio[
            "weight"
        ].sum()

        if (
            total_weight > 0
            and not math.isclose(
                total_weight,
                1.0,
                rel_tol=1e-6,
            )
        ):

            logger.info(
                "Normalizing portfolio weights "
                "(sum=%.6f).",
                total_weight,
            )

            portfolio["weight"] = (
                portfolio["weight"]
                / total_weight
            )

        # -----------------------------------------------------
        # Sort
        # -----------------------------------------------------

        portfolio = portfolio.sort_values(
            by="weight",
            ascending=False,
            ignore_index=True,
        )

        logger.info(
            "Validated %d portfolio positions.",
            len(portfolio),
        )

        return portfolio



    def _compute_position_risk(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute security-level risk metrics.

        Returns
        -------
        pd.DataFrame
            Portfolio enriched with risk metrics.
        """

        portfolio = portfolio.copy()

        # -----------------------------------------------------
        # Default Columns
        # -----------------------------------------------------

        defaults = {
            "beta": 1.0,
            "volatility": 0.20,
            "expected_return": 0.00,
        }

        for column, value in defaults.items():

            if column not in portfolio.columns:

                portfolio[column] = value

            else:

                portfolio[column] = (
                    portfolio[column]
                    .fillna(value)
                )

        # -----------------------------------------------------
        # Absolute Exposure
        # -----------------------------------------------------

        portfolio["absolute_weight"] = (
            portfolio["weight"].abs()
        )

        # -----------------------------------------------------
        # Beta Contribution
        # -----------------------------------------------------

        portfolio["beta_contribution"] = (
            portfolio["weight"]
            * portfolio["beta"]
        )

        # -----------------------------------------------------
        # Volatility Contribution
        # -----------------------------------------------------

        portfolio["volatility_contribution"] = (
            portfolio["weight"]
            * portfolio["volatility"]
        )

        # -----------------------------------------------------
        # Variance Contribution
        # -----------------------------------------------------

        portfolio["variance_contribution"] = (
            portfolio["weight"] ** 2
            * portfolio["volatility"] ** 2
        )

        # -----------------------------------------------------
        # Marginal Risk
        # (Approximation)
        # -----------------------------------------------------

        portfolio["marginal_risk"] = (
            portfolio["volatility"]
        )

        # -----------------------------------------------------
        # Component Risk
        # -----------------------------------------------------

        portfolio["component_risk"] = (
            portfolio["weight"]
            * portfolio["marginal_risk"]
        )

        # -----------------------------------------------------
        # Diversification Benefit
        # -----------------------------------------------------

        portfolio["diversification_score"] = (
            1.0
            - portfolio["weight"]
        )

        portfolio["diversification_score"] = (
            portfolio["diversification_score"]
            .clip(
                lower=0.0,
                upper=1.0,
            )
        )

        # -----------------------------------------------------
        # Position Classification
        # -----------------------------------------------------

        portfolio["risk_bucket"] = np.select(
            [
                portfolio["weight"] >= 0.10,
                portfolio["weight"] >= 0.05,
                portfolio["weight"] >= 0.02,
            ],
            [
                "Very High",
                "High",
                "Medium",
            ],
            default="Low",
        )

        # -----------------------------------------------------
        # Relative Risk Score
        # -----------------------------------------------------

        portfolio["risk_score"] = (
            (
                portfolio["weight"]
                / portfolio["weight"].max()
            ) * 40
            +
            (
                portfolio["volatility"]
                / portfolio["volatility"].max()
            ) * 40
            +
            (
                portfolio["beta"].abs()
                / portfolio["beta"].abs().max()
            ) * 20
        )

        portfolio["risk_score"] = (
            portfolio["risk_score"]
            .round(2)
        )

        logger.info(
            "Computed position risk metrics."
        )

        return portfolio



    def _compute_sector_exposure(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute portfolio sector exposure.

        Returns
        -------
        pd.DataFrame
            Sector allocation summary.
        """

        if portfolio.empty:
            return pd.DataFrame()

        portfolio = portfolio.copy()

        # -----------------------------------------------------
        # Ensure Sector Exists
        # -----------------------------------------------------

        if "sector" not in portfolio.columns:

            portfolio["sector"] = "Unknown"

        portfolio["sector"] = (
            portfolio["sector"]
            .fillna("Unknown")
            .astype(str)
        )

        # -----------------------------------------------------
        # Aggregate
        # -----------------------------------------------------

        sector = (
            portfolio
            .groupby("sector", as_index=False)
            .agg(
                positions=("ticker", "count"),
                weight=("weight", "sum"),
                avg_beta=("beta", "mean"),
                avg_volatility=("volatility", "mean"),
                max_weight=("weight", "max"),
            )
        )

        # -----------------------------------------------------
        # Percentage
        # -----------------------------------------------------

        total_weight = sector["weight"].sum()

        if total_weight > 0:

            sector["weight_pct"] = (
                sector["weight"]
                / total_weight
                * 100
            )

        else:

            sector["weight_pct"] = 0.0

        # -----------------------------------------------------
        # Concentration
        # -----------------------------------------------------

        sector["hhi_component"] = (
            sector["weight"] ** 2
        )

        sector["within_limit"] = (
            sector["weight"]
            <= self.config.max_sector_weight
        )

        sector["excess_weight"] = np.maximum(
            0.0,
            sector["weight"]
            - self.config.max_sector_weight,
        )

        # -----------------------------------------------------
        # Ranking
        # -----------------------------------------------------

        sector = sector.sort_values(
            by="weight",
            ascending=False,
            ignore_index=True,
        )

        sector["rank"] = (
            np.arange(len(sector))
            + 1
        )

        logger.info(
            "Computed sector exposure (%d sectors).",
            len(sector),
        )

        return sector


    def _compute_covariance_matrix(
        self,
        returns: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute covariance matrix of asset returns.

        Parameters
        ----------
        returns:
            Daily return series.

        Returns
        -------
        pd.DataFrame
            Covariance matrix.
        """

        if returns.empty:

            logger.warning(
                "No return series available. "
                "Covariance matrix cannot be computed."
            )

            return pd.DataFrame()

        numeric_returns = returns.select_dtypes(
            include=["number"]
        )

        if numeric_returns.empty:

            logger.warning(
                "No numeric return series available."
            )

            return pd.DataFrame()

        return numeric_returns.cov()
    

    def _compute_correlation_matrix(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute security correlation matrix.

        Expected Columns
        ----------------
        ticker
        returns

        Returns
        -------
        pd.DataFrame
            Pearson correlation matrix.
        """

        if portfolio.empty:

            return pd.DataFrame()

        if "returns" not in portfolio.columns:

            logger.warning(
                "No return series available. "
                "Correlation matrix cannot be computed."
            )

            return pd.DataFrame()

        returns = {}

        for _, row in portfolio.iterrows():

            ticker = row["ticker"]

            data = row["returns"]

            if data is None:
                continue

            series = pd.Series(data).dropna()

            if len(series) < 2:
                continue

            returns[ticker] = series.reset_index(drop=True)

        if len(returns) < 2:

            logger.warning(
                "Insufficient securities for correlation."
            )

            return pd.DataFrame()

        returns_df = pd.DataFrame(returns)

        correlation = returns_df.corr(
            method="pearson"
        )

        correlation = (
            correlation
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(0.0)
        )

        np.fill_diagonal(
            correlation.values,
            1.0,
        )

        logger.info(
            "Computed %d x %d correlation matrix.",
            correlation.shape[0],
            correlation.shape[1],
        )

        return correlation



    def _compute_statistics(
        self,
        portfolio: pd.DataFrame,
        sector_exposure: pd.DataFrame,
        correlation: pd.DataFrame,
    ) -> RiskStatistics:
        """
        Compute portfolio-level risk statistics.
        """

        statistics = RiskStatistics()

        if portfolio.empty:
            return statistics

        weights = portfolio["weight"].to_numpy(dtype=float)

        # -----------------------------------------------------
        # Gross / Net Exposure
        # -----------------------------------------------------

        statistics.gross_exposure = float(
            np.abs(weights).sum()
        )

        statistics.net_exposure = float(
            weights.sum()
        )

        # -----------------------------------------------------
        # Largest Position
        # -----------------------------------------------------

        statistics.largest_position = float(
            portfolio["weight"].max()
        )

        # -----------------------------------------------------
        # Portfolio Beta
        # -----------------------------------------------------

        if "beta" in portfolio.columns:

            statistics.portfolio_beta = float(
                np.sum(
                    portfolio["weight"]
                    * portfolio["beta"]
                )
            )

        # -----------------------------------------------------
        # Weighted Volatility
        # -----------------------------------------------------

        if "volatility" in portfolio.columns:

            statistics.volatility = float(
                np.sum(
                    portfolio["weight"]
                    * portfolio["volatility"]
                )
            )

            statistics.annualized_volatility = (
                statistics.volatility
                * math.sqrt(
                    self.config.trading_days
                )
            )

        # -----------------------------------------------------
        # Herfindahl Index
        # -----------------------------------------------------

        statistics.hhi = float(
            np.sum(
                np.square(weights)
            )
        )

        # -----------------------------------------------------
        # Effective Number of Positions
        # -----------------------------------------------------

        if statistics.hhi > 0:

            statistics.effective_positions = (
                1.0
                / statistics.hhi
            )

        # -----------------------------------------------------
        # Sector Count
        # -----------------------------------------------------

        statistics.sector_count = int(
            len(sector_exposure)
        )

        # -----------------------------------------------------
        # Historical VaR
        # -----------------------------------------------------

        if "returns" in portfolio.columns:

            returns = []

            for _, row in portfolio.iterrows():

                r = row["returns"]

                if r is None:
                    continue

                series = pd.Series(r).dropna()

                if len(series) == 0:
                    continue

                returns.append(
                    series.values
                    * row["weight"]
                )

            if returns:

                pnl = np.sum(
                    returns,
                    axis=0,
                )

                alpha = (
                    1
                    - self.config.confidence_level
                )

                statistics.value_at_risk = float(
                    -np.quantile(
                        pnl,
                        alpha,
                    )
                )

                tail = pnl[
                    pnl <= np.quantile(
                        pnl,
                        alpha,
                    )
                ]

                if len(tail):

                    statistics.expected_shortfall = (
                        float(-tail.mean())
                    )

        # -----------------------------------------------------
        # Maximum Drawdown
        # -----------------------------------------------------

        if "returns" in portfolio.columns:

            returns = []

            for _, row in portfolio.iterrows():

                r = row["returns"]

                if r is None:
                    continue

                returns.append(
                    pd.Series(r)
                    .fillna(0)
                    .values
                    * row["weight"]
                )

            if returns:

                portfolio_returns = np.sum(
                    returns,
                    axis=0,
                )

                equity = np.cumprod(
                    1 + portfolio_returns
                )

                peak = np.maximum.accumulate(
                    equity
                )

                drawdown = (
                    equity - peak
                ) / peak

                statistics.max_drawdown = float(
                    abs(drawdown.min())
                )

        logger.info(
            "Computed portfolio statistics."
        )

        return statistics



    def _detect_violations(
        self,
        portfolio: pd.DataFrame,
        statistics: RiskStatistics,
        sector_exposure: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Detect portfolio risk limit violations.

        Returns
        -------
        pd.DataFrame
            Risk violations report.
        """

        violations: list[dict[str, Any]] = []

        # =====================================================
        # Position Limits
        # =====================================================

        for _, row in portfolio.iterrows():

            weight = float(row["weight"])

            ticker = row["ticker"]

            if weight > self.config.max_position_weight:

                violations.append(
                    {
                        "category": "Position",
                        "name": ticker,
                        "metric": "Weight",
                        "value": weight,
                        "limit": self.config.max_position_weight,
                        "severity": "High",
                    }
                )

            if weight < self.config.min_position_weight:

                violations.append(
                    {
                        "category": "Position",
                        "name": ticker,
                        "metric": "Minimum Weight",
                        "value": weight,
                        "limit": self.config.min_position_weight,
                        "severity": "Low",
                    }
                )

        # =====================================================
        # Sector Limits
        # =====================================================

        if not sector_exposure.empty:

            for _, row in sector_exposure.iterrows():

                if row["weight"] > self.config.max_sector_weight:

                    violations.append(
                        {
                            "category": "Sector",
                            "name": row["sector"],
                            "metric": "Sector Exposure",
                            "value": row["weight"],
                            "limit": self.config.max_sector_weight,
                            "severity": "High",
                        }
                    )

        # =====================================================
        # Gross Exposure
        # =====================================================

        if (
            statistics.gross_exposure
            > self.config.max_gross_exposure
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Gross Exposure",
                    "value": statistics.gross_exposure,
                    "limit": self.config.max_gross_exposure,
                    "severity": "Critical",
                }
            )

        # =====================================================
        # Net Exposure
        # =====================================================

        if (
            abs(statistics.net_exposure)
            > self.config.max_net_exposure
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Net Exposure",
                    "value": statistics.net_exposure,
                    "limit": self.config.max_net_exposure,
                    "severity": "Critical",
                }
            )

        # =====================================================
        # Beta
        # =====================================================

        if (
            statistics.portfolio_beta
            > self.config.max_beta
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Portfolio Beta",
                    "value": statistics.portfolio_beta,
                    "limit": self.config.max_beta,
                    "severity": "Medium",
                }
            )

        # =====================================================
        # Volatility
        # =====================================================

        if (
            statistics.annualized_volatility
            > self.config.max_volatility
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Annualized Volatility",
                    "value": statistics.annualized_volatility,
                    "limit": self.config.max_volatility,
                    "severity": "High",
                }
            )

        # =====================================================
        # Concentration
        # =====================================================

        if (
            statistics.hhi
            > self.config.max_hhi
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "HHI",
                    "value": statistics.hhi,
                    "limit": self.config.max_hhi,
                    "severity": "Medium",
                }
            )

        if (
            statistics.effective_positions
            < self.config.min_effective_positions
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Effective Positions",
                    "value": statistics.effective_positions,
                    "limit": self.config.min_effective_positions,
                    "severity": "Medium",
                }
            )

        # =====================================================
        # VaR
        # =====================================================

        if (
            statistics.value_at_risk
            > self.config.max_var
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Value at Risk",
                    "value": statistics.value_at_risk,
                    "limit": self.config.max_var,
                    "severity": "High",
                }
            )

        # =====================================================
        # CVaR
        # =====================================================

        if (
            statistics.expected_shortfall
            > self.config.max_cvar
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Expected Shortfall",
                    "value": statistics.expected_shortfall,
                    "limit": self.config.max_cvar,
                    "severity": "Critical",
                }
            )

        # =====================================================
        # Maximum Drawdown
        # =====================================================

        if (
            statistics.max_drawdown
            > self.config.max_drawdown
        ):

            violations.append(
                {
                    "category": "Portfolio",
                    "name": "Portfolio",
                    "metric": "Maximum Drawdown",
                    "value": statistics.max_drawdown,
                    "limit": self.config.max_drawdown,
                    "severity": "Critical",
                }
            )

        # =====================================================
        # Finalize
        # =====================================================

        report = pd.DataFrame(violations)

        if report.empty:

            report = pd.DataFrame(
                columns=[
                    "category",
                    "name",
                    "metric",
                    "value",
                    "limit",
                    "severity",
                ]
            )

        logger.info(
            "Detected %d risk violations.",
            len(report),
        )

        return report



    def _risk_score(
        self,
        statistics: RiskStatistics,
        violations: pd.DataFrame,
    ) -> float:
        """
        Compute an overall portfolio risk score.

        Returns
        -------
        float
            Risk score between 0 and 100.

        Interpretation
        --------------
        90-100 : Excellent
        75-89  : Good
        60-74  : Moderate
        40-59  : High Risk
        <40    : Critical
        """

        score = 100.0

        # =====================================================
        # Position Concentration
        # =====================================================

        hhi_ratio = (
            statistics.hhi
            / self.config.max_hhi
            if self.config.max_hhi > 0
            else 0
        )

        if hhi_ratio > 1:

            score -= min(
                20,
                (hhi_ratio - 1) * 20,
            )

        # =====================================================
        # Portfolio Beta
        # =====================================================

        beta_ratio = (
            statistics.portfolio_beta
            / self.config.max_beta
            if self.config.max_beta > 0
            else 0
        )

        if beta_ratio > 1:

            score -= min(
                15,
                (beta_ratio - 1) * 15,
            )

        # =====================================================
        # Volatility
        # =====================================================

        vol_ratio = (
            statistics.annualized_volatility
            / self.config.max_volatility
            if self.config.max_volatility > 0
            else 0
        )

        if vol_ratio > 1:

            score -= min(
                20,
                (vol_ratio - 1) * 20,
            )

        # =====================================================
        # Value at Risk
        # =====================================================

        var_ratio = (
            statistics.value_at_risk
            / self.config.max_var
            if self.config.max_var > 0
            else 0
        )

        if var_ratio > 1:

            score -= min(
                15,
                (var_ratio - 1) * 15,
            )

        # =====================================================
        # Expected Shortfall
        # =====================================================

        cvar_ratio = (
            statistics.expected_shortfall
            / self.config.max_cvar
            if self.config.max_cvar > 0
            else 0
        )

        if cvar_ratio > 1:

            score -= min(
                15,
                (cvar_ratio - 1) * 15,
            )

        # =====================================================
        # Drawdown
        # =====================================================

        dd_ratio = (
            statistics.max_drawdown
            / self.config.max_drawdown
            if self.config.max_drawdown > 0
            else 0
        )

        if dd_ratio > 1:

            score -= min(
                20,
                (dd_ratio - 1) * 20,
            )

        # =====================================================
        # Diversification
        # =====================================================

        if (
            statistics.effective_positions
            < self.config.min_effective_positions
        ):

            diff = (
                self.config.min_effective_positions
                - statistics.effective_positions
            )

            score -= min(
                15,
                diff,
            )

        # =====================================================
        # Violations Penalty
        # =====================================================

        if not violations.empty:

            severity_penalty = {
                "Low": 1,
                "Medium": 3,
                "High": 5,
                "Critical": 10,
            }

            for severity in violations["severity"]:

                score -= severity_penalty.get(
                    severity,
                    3,
                )

        # =====================================================
        # Clamp
        # =====================================================

        score = max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

        logger.info(
            "Portfolio risk score = %.2f",
            score,
        )

        return round(
            score,
            2,
        )