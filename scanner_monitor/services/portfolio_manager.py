"""
portfolio_manager.py
====================

Institutional Portfolio Construction Engine

Builds an investable portfolio from BatchScanResult using
institutional-grade portfolio construction rules.

Responsibilities
----------------
• Candidate Validation
• Multi-factor Ranking
• Position Sizing
• Diversification
• Sector Constraints
• Risk Constraints
• Weight Allocation
• Portfolio Statistics
• Rebalancing
• Trade Generation

No Streamlit dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import logging
import math

import numpy as np
import pandas as pd

from .batch_scanner import (
    BatchScanResult,
)

# =============================================================================
# Logger
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True)
class PortfolioConfig:
    """
    Portfolio construction settings.
    """

    # ---------------------------------------------------------
    # Portfolio Size
    # ---------------------------------------------------------

    max_holdings: int = 30

    min_holdings: int = 10

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
    # Candidate Filters
    # ---------------------------------------------------------

    min_confidence: float = 5.0

    min_rank_score: float = 0.0

    min_relative_strength: float = 0.0

    min_expectancy: float = 0.0

    min_win_rate: float = 45.0

    # ---------------------------------------------------------
    # Liquidity
    # ---------------------------------------------------------

    min_avg_volume: int = 500_000

    min_market_cap: float = 0.0

    # ---------------------------------------------------------
    # Weighting
    # ---------------------------------------------------------

    weighting_method: str = "confidence"

    normalize_weights: bool = True

    # ---------------------------------------------------------
    # Rebalancing
    # ---------------------------------------------------------

    rebalance_threshold: float = 0.02


# =============================================================================
# Portfolio Statistics
# =============================================================================


@dataclass
class PortfolioStatistics:
    """
    Portfolio level KPIs.
    """

    total_candidates: int = 0

    accepted_candidates: int = 0

    rejected_candidates: int = 0

    holdings: int = 0

    invested_weight: float = 0.0

    average_weight: float = 0.0

    average_confidence: float = 0.0

    average_rank_score: float = 0.0

    average_relative_strength: float = 0.0

    average_expectancy: float = 0.0

    average_win_rate: float = 0.0

    sector_count: int = 0

    largest_position: float = 0.0

    smallest_position: float = 0.0

    cash_weight: float = 0.0


# =============================================================================
# Portfolio Result
# =============================================================================


@dataclass
class PortfolioResult:
    """
    Final portfolio output.
    """

    portfolio: pd.DataFrame

    candidates: pd.DataFrame

    rejected: pd.DataFrame

    orders: pd.DataFrame

    statistics: PortfolioStatistics

    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Portfolio Manager
# =============================================================================


class PortfolioManager:
    """
    Institutional portfolio construction engine.

    Workflow
    --------
        BatchScanResult
                │
                ▼
        Candidate Validation
                │
                ▼
          Candidate Filters
                │
                ▼
          Multi-factor Ranking
                │
                ▼
         Position Allocation
                │
                ▼
         Sector Constraints
                │
                ▼
          Portfolio Output
    """

    def __init__(
        self,
        config: PortfolioConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else PortfolioConfig()
        )

        logger.info(
            "PortfolioManager initialized "
            "(max_holdings=%d)",
            self.config.max_holdings,
        )

    # =========================================================
    # Public API
    # =========================================================

    def build_portfolio(
        self,
        batch: BatchScanResult,
    ) -> PortfolioResult:
        """
        Build an institutional portfolio from a BatchScanResult.
        """

        logger.info(
            "Starting portfolio construction."
        )

        candidates = batch.summary.copy()

        if candidates.empty:

            logger.warning(
                "No candidates available."
            )

            empty = pd.DataFrame()

            return PortfolioResult(
                portfolio=empty,
                candidates=empty,
                rejected=empty,
                orders=empty,
                statistics=PortfolioStatistics(),
                metadata={
                    "market": batch.market,
                },
            )

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        candidates = self._validate_candidates(
            candidates,
        )

        # -----------------------------------------------------
        # Candidate Filters
        # -----------------------------------------------------

        candidates, rejected = self._apply_filters(
            candidates,
        )

        if candidates.empty:

            logger.warning(
                "No candidates survived filtering."
            )

            empty = pd.DataFrame()

            return PortfolioResult(
                portfolio=empty,
                candidates=empty,
                rejected=rejected,
                orders=empty,
                statistics=PortfolioStatistics(
                    total_candidates=len(batch.summary),
                    rejected_candidates=len(rejected),
                ),
                metadata={
                    "market": batch.market,
                },
            )

        # -----------------------------------------------------
        # Ranking
        # -----------------------------------------------------

        ranked = self._rank_candidates(
            candidates,
        )

        # -----------------------------------------------------
        # Select Top Holdings
        # -----------------------------------------------------

        portfolio = ranked.head(
            self.config.max_holdings,
        ).copy()

        # -----------------------------------------------------
        # Position Allocation
        # -----------------------------------------------------

        portfolio = self._allocate_weights(
            portfolio,
        )

        # -----------------------------------------------------
        # Sector Constraints
        # -----------------------------------------------------

        portfolio = self._apply_sector_constraints(
            portfolio,
        )

        # -----------------------------------------------------
        # Portfolio Rebalancing
        # -----------------------------------------------------

        portfolio = self._rebalance(
            portfolio,
        )

        # -----------------------------------------------------
        # Orders
        # -----------------------------------------------------

        orders = self._build_orders(
            portfolio,
        )

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        statistics = self._compute_statistics(
            portfolio,
            candidates,
            rejected,
        )

        logger.info(
            "Portfolio construction completed "
            "(holdings=%d).",
            len(portfolio),
        )

        return PortfolioResult(
            portfolio=portfolio,
            candidates=candidates,
            rejected=rejected,
            orders=orders,
            statistics=statistics,
            metadata={
                "market": batch.market,
                "config": self.config,
            },
        )

    # =========================================================
    # Internal Pipeline (implemented in later parts)
    # =========================================================

    def _validate_candidates(
        self,
        candidates: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Validate candidate universe before portfolio construction.

        Returns
        -------
        pd.DataFrame
            Cleaned candidate DataFrame.
        """

        if candidates.empty:

            logger.warning(
                "Candidate DataFrame is empty."
            )

            return candidates.copy()

        candidates = candidates.copy()

        # -----------------------------------------------------
        # Required Columns
        # -----------------------------------------------------

        required = (
            "ticker",
            "confidence",
            "rank_score",
            "relative_strength",
            "expectancy",
            "win_rate",
        )

        missing = [
            column
            for column in required
            if column not in candidates.columns
        ]

        if missing:

            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing)
            )

        # -----------------------------------------------------
        # Numeric Columns
        # -----------------------------------------------------

        numeric_columns = [
            "confidence",
            "rank_score",
            "relative_strength",
            "expectancy",
            "win_rate",
            "avg_volume",
            "market_cap",
        ]

        for column in numeric_columns:

            if column not in candidates.columns:
                continue

            candidates[column] = pd.to_numeric(
                candidates[column],
                errors="coerce",
            )

        # -----------------------------------------------------
        # Remove Duplicate Tickers
        # -----------------------------------------------------

        candidates = candidates.drop_duplicates(
            subset="ticker",
            keep="first",
        )

        # -----------------------------------------------------
        # Remove Invalid Rows
        # -----------------------------------------------------

        candidates = candidates.dropna(
            subset=[
                "ticker",
                "confidence",
                "rank_score",
                "relative_strength",
            ]
        )

        # -----------------------------------------------------
        # Replace Optional Missing Values
        # -----------------------------------------------------

        defaults = {
            "expectancy": 0.0,
            "win_rate": 0.0,
            "avg_volume": 0,
            "market_cap": 0.0,
        }

        for column, value in defaults.items():

            if column in candidates.columns:

                candidates[column] = (
                    candidates[column]
                    .fillna(value)
                )

        # -----------------------------------------------------
        # Remove Infinite Values
        # -----------------------------------------------------

        candidates = candidates.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        candidates = candidates.dropna(
            subset=[
                "confidence",
                "rank_score",
                "relative_strength",
            ]
        )

        # -----------------------------------------------------
        # Reset Index
        # -----------------------------------------------------

        candidates = candidates.reset_index(
            drop=True,
        )

        logger.info(
            "Validated %d candidates.",
            len(candidates),
        )

        return candidates
    
    def _apply_filters(
        self,
        candidates: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Apply portfolio eligibility rules.

        Returns
        -------
        tuple
            (
                accepted_candidates,
                rejected_candidates,
            )
        """

        if candidates.empty:

            return (
                candidates.copy(),
                pd.DataFrame(),
            )

        accepted = candidates.copy()

        rejected_frames: list[pd.DataFrame] = []

        def reject(
            mask: pd.Series,
            reason: str,
        ) -> None:

            nonlocal accepted

            if not mask.any():
                return

            rejected = accepted.loc[
                mask
            ].copy()

            rejected["reject_reason"] = reason

            rejected_frames.append(
                rejected,
            )

            accepted = accepted.loc[
                ~mask
            ].copy()

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        reject(
            accepted["confidence"]
            < self.config.min_confidence,
            "Low Confidence",
        )

        logger.debug(
            "After confidence:",
            len(accepted)
        )

        # -------------------------------------------------
        # Rank Score
        # -------------------------------------------------

        reject(
            accepted["rank_score"]
            < self.config.min_rank_score,
            "Low Rank Score",
        )

        logger.debug(
            "After rank:",
            len(accepted)
        )

        # -------------------------------------------------
        # Relative Strength
        # -------------------------------------------------

        reject(
            accepted["relative_strength"]
            < self.config.min_relative_strength,
            "Weak Relative Strength",
        )

        # -------------------------------------------------
        # Expectancy
        # -------------------------------------------------

        if "expectancy" in accepted.columns:

            reject(
                accepted["expectancy"]
                < self.config.min_expectancy,
                "Negative Expectancy",
            )

        logger.debug(
            "After expectancy:",
            len(accepted)
        )

        # -------------------------------------------------
        # Win Rate
        # -------------------------------------------------

        if "win_rate" in accepted.columns:

            reject(
                accepted["win_rate"]
                < self.config.min_win_rate,
                "Low Win Rate",
            )

        logger.debug(
            "After win rate:",
            len(accepted)
        )

        # -------------------------------------------------
        # Average Volume
        # -------------------------------------------------

        if "avg_volume" in accepted.columns:

            reject(
                accepted["avg_volume"]
                < self.config.min_avg_volume,
                "Low Liquidity",
            )

        # -------------------------------------------------
        # Market Cap
        # -------------------------------------------------

        if "market_cap" in accepted.columns:

            reject(
                accepted["market_cap"]
                < self.config.min_market_cap,
                "Low Market Cap",
            )

        # -------------------------------------------------
        # Finalize
        # -------------------------------------------------

        accepted = accepted.reset_index(
            drop=True,
        )

        if rejected_frames:

            rejected = (
                pd.concat(
                    rejected_frames,
                    ignore_index=True,
                )
                .drop_duplicates(
                    subset="ticker",
                )
                .reset_index(
                    drop=True,
                )
            )

        else:

            rejected = pd.DataFrame(
                columns=list(
                    candidates.columns
                )
                + [
                    "reject_reason",
                ]
            )

        logger.info(
            "Candidate filtering completed "
            "(accepted=%d rejected=%d)",
            len(accepted),
            len(rejected),
        )

        return (
            accepted,
            rejected,
        )

    def _rank_candidates(
        self,
        candidates: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Rank portfolio candidates using a multi-factor score.

        Higher score = better candidate.
        """

        if candidates.empty:

            return candidates.copy()

        ranked = candidates.copy()

        # -----------------------------------------------------
        # Normalize Factors
        # -----------------------------------------------------

        factors = (
            "confidence",
            "rank_score",
            "relative_strength",
            "expectancy",
            "win_rate",
        )

        for factor in factors:

            if factor not in ranked.columns:
                continue

            minimum = ranked[factor].min()
            maximum = ranked[factor].max()

            if math.isclose(
                minimum,
                maximum,
            ):

                ranked[f"{factor}_norm"] = 1.0

            else:

                ranked[f"{factor}_norm"] = (
                    (
                        ranked[factor]
                        - minimum
                    )
                    /
                    (
                        maximum
                        - minimum
                    )
                )

        # -----------------------------------------------------
        # Factor Weights
        # -----------------------------------------------------

        weights = {
            "confidence_norm": 0.35,
            "rank_score_norm": 0.30,
            "relative_strength_norm": 0.15,
            "expectancy_norm": 0.10,
            "win_rate_norm": 0.10,
        }

        ranked["portfolio_score"] = 0.0

        for column, weight in weights.items():

            if column in ranked.columns:

                ranked["portfolio_score"] += (
                    ranked[column] * weight
                )

        # -----------------------------------------------------
        # Final Ranking
        # -----------------------------------------------------

        sort_columns = [
            "portfolio_score",
        ]

        ascending = [
            False,
        ]

        for column in (
            "confidence",
            "rank_score",
            "relative_strength",
        ):

            if column in ranked.columns:

                sort_columns.append(column)

                ascending.append(False)

        ranked = ranked.sort_values(
            by=sort_columns,
            ascending=ascending,
            ignore_index=True,
        )

        ranked["portfolio_rank"] = (
            np.arange(
                1,
                len(ranked) + 1,
            )
        )

        logger.info(
            "Ranked %d portfolio candidates.",
            len(ranked),
        )

        return ranked

    def _allocate_weights(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Allocate portfolio weights based on the configured
        weighting method.

        Returns
        -------
        pd.DataFrame
            Portfolio with normalized weights.
        """

        if portfolio.empty:

            return portfolio.copy()

        portfolio = portfolio.copy()

        # -----------------------------------------------------
        # Select Weighting Factor
        # -----------------------------------------------------

        method = self.config.weighting_method.lower()

        factor_map = {
            "confidence": "confidence",
            "rank": "rank_score",
            "relative_strength": "relative_strength",
            "expectancy": "expectancy",
            "equal": None,
        }

        factor = factor_map.get(
            method,
            "confidence",
        )

        # -----------------------------------------------------
        # Raw Weights
        # -----------------------------------------------------

        if factor is None:

            portfolio["weight"] = (
                1.0 / len(portfolio)
            )

        elif factor not in portfolio.columns:

            logger.warning(
                "Weight factor '%s' missing. "
                "Using equal weighting.",
                factor,
            )

            portfolio["weight"] = (
                1.0 / len(portfolio)
            )

        else:

            values = (
                portfolio[factor]
                .clip(lower=0.0)
                .astype(float)
            )

            total = values.sum()

            if math.isclose(
                total,
                0.0,
            ):

                portfolio["weight"] = (
                    1.0 / len(portfolio)
                )

            else:

                portfolio["weight"] = (
                    values / total
                )

        # -----------------------------------------------------
        # Apply Position Limits
        # -----------------------------------------------------

        portfolio["weight"] = portfolio[
            "weight"
        ].clip(
            lower=self.config.min_position_weight,
            upper=self.config.max_position_weight,
        )

        # -----------------------------------------------------
        # Normalize Weights
        # -----------------------------------------------------

        if self.config.normalize_weights:

            total = portfolio[
                "weight"
            ].sum()

            if total > 0:

                portfolio["weight"] = (
                    portfolio["weight"] / total
                )

        # -----------------------------------------------------
        # Derived Fields
        # -----------------------------------------------------

        portfolio["weight_pct"] = (
            portfolio["weight"] * 100.0
        )

        portfolio["capital_fraction"] = (
            portfolio["weight"]
        )

        portfolio = portfolio.sort_values(
            by="weight",
            ascending=False,
            ignore_index=True,
        )

        logger.info(
            "Allocated weights "
            "(total=%.4f).",
            portfolio["weight"].sum(),
        )

        return portfolio

    def _apply_sector_constraints(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Apply maximum sector exposure constraints.

        Returns
        -------
        pd.DataFrame
            Portfolio satisfying sector limits.
        """

        if portfolio.empty:

            return portfolio.copy()

        portfolio = portfolio.copy()

        if "sector" not in portfolio.columns:

            logger.info(
                "Sector column not available. "
                "Skipping sector constraints."
            )

            return portfolio

        limit = self.config.max_sector_weight

        if limit <= 0:

            return portfolio

        # -----------------------------------------------------
        # Iterative Sector Constraint
        # -----------------------------------------------------

        for _ in range(10):

            sector_weights = (
                portfolio
                .groupby(
                    "sector",
                    observed=True,
                )["weight"]
                .sum()
            )

            excess_found = False

            for sector, sector_weight in sector_weights.items():

                if sector_weight <= limit:

                    continue

                excess_found = True

                excess = sector_weight - limit

                mask = (
                    portfolio["sector"]
                    == sector
                )

                sector_total = portfolio.loc[
                    mask,
                    "weight",
                ].sum()

                if math.isclose(
                    sector_total,
                    0.0,
                ):

                    continue

                reduction = (
                    portfolio.loc[
                        mask,
                        "weight",
                    ]
                    /
                    sector_total
                ) * excess

                portfolio.loc[
                    mask,
                    "weight",
                ] -= reduction

                other_mask = ~mask

                other_total = portfolio.loc[
                    other_mask,
                    "weight",
                ].sum()

                if (
                    other_total > 0
                    and excess > 0
                ):

                    addition = (
                        portfolio.loc[
                            other_mask,
                            "weight",
                        ]
                        /
                        other_total
                    ) * excess

                    portfolio.loc[
                        other_mask,
                        "weight",
                    ] += addition

            if not excess_found:

                break

        # -----------------------------------------------------
        # Safety Normalization
        # -----------------------------------------------------

        portfolio["weight"] = (
            portfolio["weight"]
            .clip(lower=0.0)
        )

        total = portfolio["weight"].sum()

        if total > 0:

            portfolio["weight"] /= total

        portfolio["weight_pct"] = (
            portfolio["weight"] * 100.0
        )

        exposure = (
            portfolio
            .groupby(
                "sector",
                observed=True,
            )["weight"]
            .sum()
            .sort_values(
                ascending=False,
            )
            .to_dict()
        )

        logger.info(
            "Applied sector constraints "
            "(%d sectors).",
            len(exposure),
        )

        logger.debug(
            "Sector exposure: %s",
            exposure,
        )

        return portfolio
    

    def _rebalance(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Rebalance portfolio by comparing target weights with
        current weights.

        Expected optional input columns
        -------------------------------
        current_weight : Existing portfolio weight

        Output Columns
        --------------
        target_weight
        weight_change
        rebalance_action
        """

        if portfolio.empty:

            return portfolio.copy()

        portfolio = portfolio.copy()

        # -----------------------------------------------------
        # Initialize Current Weight
        # -----------------------------------------------------

        if "current_weight" not in portfolio.columns:

            portfolio["current_weight"] = 0.0

        portfolio["target_weight"] = (
            portfolio["weight"]
        )

        portfolio["weight_change"] = (
            portfolio["target_weight"]
            - portfolio["current_weight"]
        )

        threshold = self.config.rebalance_threshold

        # -----------------------------------------------------
        # Rebalance Decision
        # -----------------------------------------------------

        actions = []

        for _, row in portfolio.iterrows():

            current = float(
                row["current_weight"]
            )

            target = float(
                row["target_weight"]
            )

            delta = target - current

            if abs(delta) < threshold:

                action = "HOLD"

            elif current == 0:

                action = "BUY"

            elif target == 0:

                action = "SELL"

            elif delta > 0:

                action = "INCREASE"

            else:

                action = "DECREASE"

            actions.append(action)

        portfolio["rebalance_action"] = actions

        # -----------------------------------------------------
        # Turnover
        # -----------------------------------------------------

        portfolio["turnover"] = (
            portfolio["weight_change"]
            .abs()
        )

        total_turnover = (
            portfolio["turnover"]
            .sum()
        )

        logger.info(
            "Portfolio rebalanced "
            "(turnover=%.4f).",
            total_turnover,
        )

        return portfolio
    
    def _build_orders(
        self,
        portfolio: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate executable trade orders from the
        rebalanced portfolio.

        Returns
        -------
        pd.DataFrame
            Institutional order book.
        """

        if portfolio.empty:

            return pd.DataFrame()

        portfolio = portfolio.copy()

        # -----------------------------------------------------
        # Required Columns
        # -----------------------------------------------------

        required = (
            "ticker",
            "rebalance_action",
            "current_weight",
            "target_weight",
            "weight_change",
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
        # Build Orders
        # -----------------------------------------------------

        logger.debug(
            "PORTFOLIO COLUMNS:",
            portfolio.columns.tolist()
        )

        orders = pd.DataFrame()

        orders["ticker"] = portfolio["ticker"]

        orders["action"] = portfolio[
            "rebalance_action"
        ]

        orders["current_weight"] = portfolio[
            "current_weight"
        ]

        orders["target_weight"] = portfolio[
            "target_weight"
        ]

        orders["weight_change"] = portfolio[
            "weight_change"
        ]

        orders["trade_weight"] = (
            portfolio["weight_change"].abs()
        )

        # -----------------------------------------------------
        # Execution Price
        # -----------------------------------------------------

        if "plan_entry" in portfolio.columns:

            orders["price"] = portfolio["plan_entry"]

        elif "limit_price" in portfolio.columns:

            orders["price"] = portfolio["limit_price"]

        elif "entry_ref" in portfolio.columns:

            orders["price"] = portfolio["entry_ref"]

        elif "last_close" in portfolio.columns:

            orders["price"] = portfolio["last_close"]

        else:

            raise ValueError(
                "No execution price field available."
            )

        # -----------------------------------------------------
        # Optional Fields
        # -----------------------------------------------------

        optional = (
            "sector",
            "confidence",
            "rank_score",
            "portfolio_rank",
        )

        for column in optional:

            if column in portfolio.columns:

                orders[column] = portfolio[column]

        # -----------------------------------------------------
        # Priority
        # -----------------------------------------------------

        priority = {
            "BUY": 1,
            "INCREASE": 2,
            "DECREASE": 3,
            "SELL": 4,
            "HOLD": 5,
        }

        orders["priority"] = (
            orders["action"]
            .map(priority)
            .fillna(99)
            .astype(int)
        )

        # -----------------------------------------------------
        # Remove HOLD Orders
        # -----------------------------------------------------

        orders = orders.loc[
            orders["action"] != "HOLD"
        ].copy()

        # -----------------------------------------------------
        # Sort Orders
        # -----------------------------------------------------

        orders = orders.sort_values(
            by=[
                "priority",
                "trade_weight",
            ],
            ascending=[
                True,
                False,
            ],
            ignore_index=True,
        )

        logger.info(
            "Generated %d executable orders.",
            len(orders),
        )

        return orders
    

    def _compute_statistics(
        self,
        portfolio: pd.DataFrame,
        candidates: pd.DataFrame,
        rejected: pd.DataFrame,
    ) -> PortfolioStatistics:
        """
        Compute portfolio-level statistics.

        Returns
        -------
        PortfolioStatistics
        """

        stats = PortfolioStatistics()

        stats.total_candidates = len(candidates) + len(rejected)

        stats.accepted_candidates = len(candidates)

        stats.rejected_candidates = len(rejected)

        stats.holdings = len(portfolio)

        if portfolio.empty:

            logger.info(
                "Portfolio statistics computed "
                "(empty portfolio)."
            )

            return stats

        # -----------------------------------------------------
        # Portfolio Weights
        # -----------------------------------------------------

        if "weight" in portfolio.columns:

            weights = (
                portfolio["weight"]
                .astype(float)
            )

            stats.invested_weight = float(
                weights.sum()
            )

            stats.average_weight = float(
                weights.mean()
            )

            stats.largest_position = float(
                weights.max()
            )

            stats.smallest_position = float(
                weights.min()
            )

            stats.cash_weight = max(
                0.0,
                1.0 - stats.invested_weight,
            )

        # -----------------------------------------------------
        # Factor Statistics
        # -----------------------------------------------------

        factor_map = {
            "confidence":
                "average_confidence",

            "rank_score":
                "average_rank_score",

            "relative_strength":
                "average_relative_strength",

            "expectancy":
                "average_expectancy",

            "win_rate":
                "average_win_rate",
        }

        for column, attribute in factor_map.items():

            if column in portfolio.columns:

                value = float(
                    portfolio[column]
                    .mean()
                )

                setattr(
                    stats,
                    attribute,
                    value,
                )

        # -----------------------------------------------------
        # Sector Statistics
        # -----------------------------------------------------

        if "sector" in portfolio.columns:

            stats.sector_count = int(
                portfolio["sector"]
                .nunique()
            )

        logger.info(
            "Portfolio statistics computed "
            "(holdings=%d)",
            stats.holdings,
        )

        return stats