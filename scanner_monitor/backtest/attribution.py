"""
attribution.py
==============

Institutional Performance Attribution Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AttributionConfig:
    """
    Attribution analysis configuration.
    """

    annualization_factor: int = 252

    benchmark_name: str = "Benchmark"


class AttributionEngine:
    """
    Institutional performance attribution engine.
    """

    def __init__(
        self,
        config: AttributionConfig,
    ) -> None:
        """
        Initialize attribution engine.
        """

        self.config = config

        logger.info(
            "AttributionEngine initialized."
        )


    def contribution_to_return(
        self,
        weights: pd.Series,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate return contribution.
        """

        return (
            weights
            * returns
        )

    def contribution_to_risk(
        self,
        weights: pd.Series,
        volatility: pd.Series,
    ) -> pd.Series:
        """
        Calculate risk contribution.
        """

        contribution = (
            weights.abs()
            * volatility
        )

        total = contribution.sum()

        if total == 0:
            return contribution

        return (
            contribution
            / total
        )

    def allocation_effect(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate allocation effect.
        """

        return (
            portfolio_weights
            - benchmark_weights
        ) * benchmark_returns

    def selection_effect(
        self,
        portfolio_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate selection effect.
        """

        return (
            portfolio_weights
            * (
                portfolio_returns
                - benchmark_returns
            )
        )

    def interaction_effect(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate interaction effect.
        """

        return (
            (
                portfolio_weights
                - benchmark_weights
            )
            * (
                portfolio_returns
                - benchmark_returns
            )
        )

    def contribution_to_return(
        self,
        weights: pd.Series,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate return contribution.
        """

        return (
            weights
            * returns
        )

    def contribution_to_risk(
        self,
        weights: pd.Series,
        volatility: pd.Series,
    ) -> pd.Series:
        """
        Calculate risk contribution.
        """

        contribution = (
            weights.abs()
            * volatility
        )

        total = contribution.sum()

        if total == 0:
            return contribution

        return (
            contribution
            / total
        )

    def allocation_effect(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate allocation effect.
        """

        return (
            portfolio_weights
            - benchmark_weights
        ) * benchmark_returns

    def selection_effect(
        self,
        portfolio_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate selection effect.
        """

        return (
            portfolio_weights
            * (
                portfolio_returns
                - benchmark_returns
            )
        )

    def interaction_effect(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate interaction effect.
        """

        return (
            (
                portfolio_weights
                - benchmark_weights
            )
            * (
                portfolio_returns
                - benchmark_returns
            )
        )

    def brinson_attribution(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.DataFrame:
        """
        Compute Brinson attribution.
        """

        allocation = (
            self.allocation_effect(
                portfolio_weights,
                benchmark_weights,
                benchmark_returns,
            )
        )

        selection = (
            self.selection_effect(
                portfolio_weights,
                portfolio_returns,
                benchmark_returns,
            )
        )

        interaction = (
            self.interaction_effect(
                portfolio_weights,
                benchmark_weights,
                portfolio_returns,
                benchmark_returns,
            )
        )

        return pd.DataFrame(
            {
                "Allocation":
                allocation,
                "Selection":
                selection,
                "Interaction":
                interaction,
                "Total":
                allocation
                + selection
                + interaction,
            }
        )

    def factor_attribution(
        self,
        factor_exposures: pd.DataFrame,
        factor_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate factor attribution.
        """

        common = (
            factor_exposures.columns
            .intersection(
                factor_returns.index
            )
        )

        if common.empty:
            return pd.Series(
                dtype=float,
            )

        return (
            factor_exposures[
                common
            ]
            .multiply(
                factor_returns[
                    common
                ],
                axis=1,
            )
            .sum(
                axis=0,
            )
        )

    def sector_attribution(
        self,
        sectors: pd.Series,
        contributions: pd.Series,
    ) -> pd.Series:
        """
        Aggregate attribution by sector.
        """

        return (
            contributions
            .groupby(
                sectors
            )
            .sum()
            .sort_values(
                ascending=False,
            )
        )

    def security_attribution(
        self,
        contributions: pd.Series,
    ) -> pd.Series:
        """
        Return security-level attribution.
        """

        return (
            contributions
            .sort_values(
                ascending=False,
            )
        )

    def summary(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Return attribution summary.
        """

        allocation = (
            self.allocation_effect(
                portfolio_weights,
                benchmark_weights,
                benchmark_returns,
            ).sum()
        )

        selection = (
            self.selection_effect(
                portfolio_weights,
                portfolio_returns,
                benchmark_returns,
            ).sum()
        )

        interaction = (
            self.interaction_effect(
                portfolio_weights,
                benchmark_weights,
                portfolio_returns,
                benchmark_returns,
            ).sum()
        )

        total = (
            allocation
            + selection
            + interaction
        )

        return pd.Series(
            {
                "Allocation":
                allocation,
                "Selection":
                selection,
                "Interaction":
                interaction,
                "Total Attribution":
                total,
            }
        )

    def reset(
        self,
    ) -> None:
        """
        Reset attribution engine.
        """

        logger.info(
            "AttributionEngine reset."
        )