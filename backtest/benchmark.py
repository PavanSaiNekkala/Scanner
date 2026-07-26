"""
benchmark.py
============

Institutional Benchmark Analytics Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BenchmarkConfig:
    """
    Benchmark analysis configuration.
    """

    benchmark_name: str = "Benchmark"

    risk_free_rate: float = 0.0

    annualization_factor: int = 252


class BenchmarkEngine:
    """
    Institutional benchmark analytics engine.
    """

    def __init__(
        self,
        config: BenchmarkConfig,
    ) -> None:
        """
        Initialize the benchmark engine.
        """

        self.config = config

        logger.info(
            "BenchmarkEngine initialized."
        )


    def compare(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> dict[str, float]:
        """
        Compare strategy against benchmark.
        """

        strategy_returns = (
            strategy_returns.dropna()
        )

        benchmark_returns = (
            benchmark_returns.dropna()
        )

        common_index = (
            strategy_returns.index.intersection(
                benchmark_returns.index
            )
        )

        strategy_returns = (
            strategy_returns.loc[
                common_index
            ]
        )

        benchmark_returns = (
            benchmark_returns.loc[
                common_index
            ]
        )

        return {
            "alpha": self.alpha(
                strategy_returns,
                benchmark_returns,
            ),
            "beta": self.beta(
                strategy_returns,
                benchmark_returns,
            ),
            "tracking_error": self.tracking_error(
                strategy_returns,
                benchmark_returns,
            ),
            "information_ratio": self.information_ratio(
                strategy_returns,
                benchmark_returns,
            ),
            "active_return": self.active_return(
                strategy_returns,
                benchmark_returns,
            ),
        }

    def active_return(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate active return.
        """

        return float(
            (
                strategy_returns
                - benchmark_returns
            ).mean()
            * self.config.annualization_factor
        )

    def tracking_error(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate annualized tracking error.
        """

        active = (
            strategy_returns
            - benchmark_returns
        )

        return float(
            active.std(
                ddof=1
            )
            * np.sqrt(
                self.config.annualization_factor
            )
        )

    def beta(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate portfolio beta.
        """

        covariance = np.cov(
            strategy_returns,
            benchmark_returns,
        )[0, 1]

        variance = np.var(
            benchmark_returns,
            ddof=1,
        )

        if variance == 0:
            return 0.0

        return float(
            covariance
            / variance
        )

    def alpha(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate annualized alpha.
        """

        beta = self.beta(
            strategy_returns,
            benchmark_returns,
        )

        strategy_mean = (
            strategy_returns.mean()
            * self.config.annualization_factor
        )

        benchmark_mean = (
            benchmark_returns.mean()
            * self.config.annualization_factor
        )

        return float(
            strategy_mean
            - (
                self.config.risk_free_rate
                + beta
                * (
                    benchmark_mean
                    - self.config.risk_free_rate
                )
            )
        )


    def information_ratio(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate annualized Information Ratio.
        """

        tracking_error = self.tracking_error(
            strategy_returns,
            benchmark_returns,
        )

        if tracking_error == 0:
            return 0.0

        return (
            self.active_return(
                strategy_returns,
                benchmark_returns,
            )
            / tracking_error
        )

    def excess_returns(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Return excess returns over benchmark.
        """

        return (
            strategy_returns
            - benchmark_returns
        )

    def cumulative_returns(
        self,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate cumulative returns.
        """

        return (
            1.0 + returns
        ).cumprod() - 1.0

    def relative_drawdown(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Calculate relative drawdown versus benchmark.
        """

        strategy_curve = (
            self.cumulative_returns(
                strategy_returns,
            )
        )

        benchmark_curve = (
            self.cumulative_returns(
                benchmark_returns,
            )
        )

        relative_curve = (
            strategy_curve
            - benchmark_curve
        )

        running_max = (
            relative_curve.cummax()
        )

        return (
            relative_curve
            - running_max
        )

    def summary(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> pd.Series:
        """
        Return benchmark comparison summary.
        """

        metrics = self.compare(
            strategy_returns,
            benchmark_returns,
        )

        metrics.update(
            {
                "strategy_return":
                float(
                    self.cumulative_returns(
                        strategy_returns,
                    ).iloc[-1]
                ),
                "benchmark_return":
                float(
                    self.cumulative_returns(
                        benchmark_returns,
                    ).iloc[-1]
                ),
            }
        )

        return pd.Series(
            metrics,
            name=self.config.benchmark_name,
        )

    def reset(
        self,
    ) -> None:
        """
        Reset benchmark engine.
        """

        logger.info(
            "BenchmarkEngine reset."
        )