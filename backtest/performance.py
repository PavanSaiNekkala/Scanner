"""
performance.py
==============

Institutional Performance Analytics Engine
"""

from __future__ import annotations

from dataclasses import dataclass

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ==========================================================
# Performance Configuration
# ==========================================================


@dataclass(slots=True)
class PerformanceConfig:
    """
    Performance analytics configuration.
    """

    risk_free_rate: float = 0.02

    trading_days: int = 252

    confidence_level: float = 0.95


@dataclass(slots=True)
class PerformanceSummary:
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    maximum_drawdown: float
    recovery_factor: float
    gain_to_pain_ratio: float
    omega_ratio: float
    value_at_risk: float
    conditional_value_at_risk: float
    beta: float | None = None
    alpha: float | None = None
    information_ratio: float | None = None
    treynor_ratio: float | None = None


# ==========================================================
# Performance Engine
# ==========================================================


class PerformanceEngine:
    """
    Institutional Performance Analytics Engine.

    Responsibilities
    ----------------
    • Return metrics
    • Risk-adjusted metrics
    • Drawdown metrics
    • Volatility metrics
    • Benchmark metrics
    • Tail-risk metrics
    """

    def __init__(
        self,
        config: PerformanceConfig | None = None,
    ) -> None:

        self.config = (
            config
            or PerformanceConfig()
        )

        logger.info(
            "Performance Engine initialized."
        )

    def evaluate(
        self,
        history: pd.DataFrame,
        benchmark_returns: pd.Series | None = None,
    ) -> dict[str, float]:
        """
        Evaluate portfolio performance.

        Parameters
        ----------
        history
            Portfolio history DataFrame.
        benchmark_returns
            Optional benchmark returns.

        Returns
        -------
        dict
            Performance metrics.
        """

        if history.empty:

            logger.warning(
                "Empty portfolio history."
            )

            return {}

        required = {
            "portfolio_value",
            "daily_return",
            "cumulative_return",
        }

        missing = required.difference(
            history.columns
        )

        if missing:

            raise ValueError(
                f"Missing columns: {missing}"
            )

        returns = (
            history["daily_return"]
            .fillna(0.0)
            .astype(float)
        )

        portfolio_values = (
            history["portfolio_value"]
            .astype(float)
        )

        metrics = {

            "Total Return":
                self._total_return(
                    portfolio_values,
                ),

            "Annualized Return":
                self._annualized_return(
                    returns,
                ),

            "Annualized Volatility":
                self._annualized_volatility(
                    returns,
                ),

            "Sharpe Ratio":
                self._sharpe_ratio(
                    returns,
                ),

            "Sortino Ratio":
                self._sortino_ratio(
                    returns,
                ),

            "Calmar Ratio":
                self._calmar_ratio(
                    returns,
                    portfolio_values,
                ),

            "Maximum Drawdown":
                self._maximum_drawdown(
                    portfolio_values,
                ),

            "Recovery Factor":
                self._recovery_factor(
                    portfolio_values,
                ),

            "Gain-to-Pain Ratio":
                self._gain_to_pain_ratio(
                    returns,
                ),

            "Omega Ratio":
                self._omega_ratio(
                    returns,
                ),

            "Value at Risk":
                self._value_at_risk(
                    returns,
                ),

            "Conditional VaR":
                self._conditional_value_at_risk(
                    returns,
                ),

        }

        if benchmark_returns is not None:

            benchmark_returns = (
                benchmark_returns
                .fillna(0.0)
                .astype(float)
            )

            metrics.update(

                {

                    "Beta":
                        self._beta(
                            returns,
                            benchmark_returns,
                        ),

                    "Alpha":
                        self._alpha(
                            returns,
                            benchmark_returns,
                        ),

                    "Information Ratio":
                        self._information_ratio(
                            returns,
                            benchmark_returns,
                        ),

                    "Treynor Ratio":
                        self._treynor_ratio(
                            returns,
                            benchmark_returns,
                        ),

                }

            )

        logger.info(
            "Calculated %d performance metrics.",
            len(metrics),
        )

        return self._summary(
            metrics,
        )

    def _total_return(
        self,
        portfolio_values: pd.Series,
    ) -> float:
        """
        Calculate total portfolio return.

        Parameters
        ----------
        portfolio_values
            Portfolio value time series.

        Returns
        -------
        float
            Total portfolio return.
        """

        if portfolio_values.empty:

            return 0.0

        initial_value = float(
            portfolio_values.iloc[0]
        )

        final_value = float(
            portfolio_values.iloc[-1]
        )

        if initial_value <= 0:

            logger.warning(
                "Initial portfolio value must "
                "be greater than zero."
            )

            return 0.0

        total_return = (
            final_value
            - initial_value
        ) / initial_value

        logger.debug(
            "Total return: %.6f",
            total_return,
        )

        return total_return

    def _annualized_return(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate annualized portfolio return (CAGR).

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Annualized return.
        """

        if returns.empty:

            return 0.0

        cumulative_growth = (
            1.0 + returns
        ).prod()

        periods = len(returns)

        if (
            periods == 0
            or cumulative_growth <= 0
        ):

            return 0.0

        years = (
            periods
            / self.config.trading_days
        )

        if years <= 0:

            return 0.0

        annualized_return = (

            cumulative_growth
            ** (1.0 / years)

            - 1.0

        )

        logger.debug(
            "Annualized return: %.6f",
            annualized_return,
        )

        return annualized_return


    def _annualized_volatility(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate annualized portfolio volatility.

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Annualized volatility.
        """

        if returns.empty:

            return 0.0

        volatility = float(
            returns.std(
                ddof=1,
            )
        )

        if np.isnan(
            volatility
        ):

            return 0.0

        annualized_volatility = (

            volatility

            * np.sqrt(
                self.config.trading_days
            )

        )

        logger.debug(
            "Annualized volatility: %.6f",
            annualized_volatility,
        )

        return annualized_volatility


    def _sharpe_ratio(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate the annualized Sharpe ratio.

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Annualized Sharpe ratio.
        """

        if returns.empty:

            return 0.0

        annualized_return = (
            self._annualized_return(
                returns,
            )
        )

        annualized_volatility = (
            self._annualized_volatility(
                returns,
            )
        )

        if annualized_volatility <= 0:

            return 0.0

        excess_return = (

            annualized_return

            - self.config.risk_free_rate

        )

        sharpe_ratio = (

            excess_return

            / annualized_volatility

        )

        logger.debug(
            "Sharpe ratio: %.6f",
            sharpe_ratio,
        )

        return sharpe_ratio


    def _sortino_ratio(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate the annualized Sortino ratio.

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Annualized Sortino ratio.
        """

        if returns.empty:

            return 0.0

        annualized_return = (
            self._annualized_return(
                returns,
            )
        )

        downside_returns = (
            returns[
                returns < 0.0
            ]
        )

        if downside_returns.empty:

            return np.inf

        downside_deviation = float(
            downside_returns.std(
                ddof=1,
            )
        )

        if (
            np.isnan(
                downside_deviation
            )
            or downside_deviation <= 0.0
        ):

            return 0.0

        annualized_downside = (

            downside_deviation

            * np.sqrt(
                self.config.trading_days
            )

        )

        excess_return = (

            annualized_return

            - self.config.risk_free_rate

        )

        sortino_ratio = (

            excess_return

            / annualized_downside

        )

        logger.debug(
            "Sortino ratio: %.6f",
            sortino_ratio,
        )

        return sortino_ratio

    def _calmar_ratio(
        self,
        returns: pd.Series,
        portfolio_values: pd.Series,
    ) -> float:
        """
        Calculate the Calmar ratio.

        Parameters
        ----------
        returns
            Daily portfolio returns.
        portfolio_values
            Portfolio value time series.

        Returns
        -------
        float
            Calmar ratio.
        """

        if (
            returns.empty
            or portfolio_values.empty
        ):

            return 0.0

        annualized_return = (
            self._annualized_return(
                returns,
            )
        )

        maximum_drawdown = abs(
            self._maximum_drawdown(
                portfolio_values,
            )
        )

        if maximum_drawdown <= 0.0:

            return np.inf

        calmar_ratio = (

            annualized_return

            / maximum_drawdown

        )

        logger.debug(
            "Calmar ratio: %.6f",
            calmar_ratio,
        )

        return calmar_ratio

    def _maximum_drawdown(
        self,
        portfolio_values: pd.Series,
    ) -> float:
        """
        Calculate the maximum drawdown.

        Parameters
        ----------
        portfolio_values
            Portfolio value time series.

        Returns
        -------
        float
            Maximum drawdown as a negative decimal.
        """

        if portfolio_values.empty:

            return 0.0

        values = (
            portfolio_values
            .astype(float)
        )

        running_peak = (
            values.cummax()
        )

        drawdowns = (

            values

            / running_peak

            - 1.0

        )

        maximum_drawdown = float(
            drawdowns.min()
        )

        if np.isnan(
            maximum_drawdown
        ):

            return 0.0

        logger.debug(
            "Maximum drawdown: %.6f",
            maximum_drawdown,
        )

        return maximum_drawdown


    def _recovery_factor(
        self,
        portfolio_values: pd.Series,
    ) -> float:
        """
        Calculate the Recovery Factor.

        Parameters
        ----------
        portfolio_values
            Portfolio value time series.

        Returns
        -------
        float
            Recovery Factor.
        """

        if portfolio_values.empty:

            return 0.0

        total_return = (
            self._total_return(
                portfolio_values,
            )
        )

        maximum_drawdown = abs(
            self._maximum_drawdown(
                portfolio_values,
            )
        )

        if maximum_drawdown <= 0.0:

            return np.inf

        recovery_factor = (

            total_return

            / maximum_drawdown

        )

        logger.debug(
            "Recovery factor: %.6f",
            recovery_factor,
        )

        return recovery_factor


    def _gain_to_pain_ratio(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate the Gain-to-Pain Ratio.

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Gain-to-Pain Ratio.
        """

        if returns.empty:

            return 0.0

        positive_returns = (
            returns[
                returns > 0.0
            ]
        )

        negative_returns = (
            returns[
                returns < 0.0
            ]
        )

        total_gain = float(
            positive_returns.sum()
        )

        total_loss = abs(
            float(
                negative_returns.sum()
            )
        )

        if total_loss <= 0.0:

            return np.inf

        gain_to_pain = (

            total_gain

            / total_loss

        )

        logger.debug(
            "Gain-to-Pain Ratio: %.6f",
            gain_to_pain,
        )

        return gain_to_pain

    def _omega_ratio(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate the Omega ratio.

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Omega ratio.
        """

        if returns.empty:

            return 0.0

        mar = (

            self.config.risk_free_rate

            / self.config.trading_days

        )

        excess_returns = (
            returns
            - mar
        )

        gains = float(
            excess_returns[
                excess_returns > 0.0
            ].sum()
        )

        losses = abs(
            float(
                excess_returns[
                    excess_returns < 0.0
                ].sum()
            )
        )

        if losses <= 0.0:

            return np.inf

        omega_ratio = (

            gains

            / losses

        )

        logger.debug(
            "Omega ratio: %.6f",
            omega_ratio,
        )

        return omega_ratio


    def _value_at_risk(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate historical Value at Risk (VaR).

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Value at Risk as a positive decimal.
        """

        if returns.empty:

            return 0.0

        clean_returns = (
            returns
            .dropna()
            .astype(float)
        )

        if clean_returns.empty:

            return 0.0

        percentile = (

            1.0

            - self.config.confidence_level

        ) * 100.0

        var = float(
            np.percentile(
                clean_returns,
                percentile,
            )
        )

        value_at_risk = abs(
            min(
                var,
                0.0,
            )
        )

        logger.debug(
            "Historical VaR (%.2f%%): %.6f",
            self.config.confidence_level * 100,
            value_at_risk,
        )

        return value_at_risk


    def _conditional_value_at_risk(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Calculate historical Conditional Value at Risk (CVaR).

        Also known as Expected Shortfall (ES).

        Parameters
        ----------
        returns
            Daily portfolio returns.

        Returns
        -------
        float
            Conditional Value at Risk as a positive decimal.
        """

        if returns.empty:

            return 0.0

        clean_returns = (
            returns
            .dropna()
            .astype(float)
        )

        if clean_returns.empty:

            return 0.0

        percentile = (

            1.0

            - self.config.confidence_level

        ) * 100.0

        var_threshold = float(
            np.percentile(
                clean_returns,
                percentile,
            )
        )

        tail_losses = (
            clean_returns[
                clean_returns <= var_threshold
            ]
        )

        if tail_losses.empty:

            return 0.0

        conditional_var = abs(
            float(
                tail_losses.mean()
            )
        )

        logger.debug(
            "Historical CVaR (%.2f%%): %.6f",
            self.config.confidence_level * 100,
            conditional_var,
        )

        return conditional_var



    def _beta(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate portfolio beta relative to a benchmark.

        Parameters
        ----------
        portfolio_returns
            Portfolio daily returns.
        benchmark_returns
            Benchmark daily returns.

        Returns
        -------
        float
            Portfolio beta.
        """

        if (
            portfolio_returns.empty
            or benchmark_returns.empty
        ):

            return 0.0

        data = pd.concat(
            [
                portfolio_returns.rename(
                    "portfolio"
                ),
                benchmark_returns.rename(
                    "benchmark"
                ),
            ],
            axis=1,
        ).dropna()

        if len(data) < 2:

            return 0.0

        benchmark_variance = float(
            data["benchmark"].var(
                ddof=1,
            )
        )

        if benchmark_variance <= 0.0:

            return 0.0

        covariance = float(
            data[
                [
                    "portfolio",
                    "benchmark",
                ]
            ].cov(
                ddof=1,
            ).iloc[0, 1]
        )

        beta = (

            covariance

            / benchmark_variance

        )

        logger.debug(
            "Beta: %.6f",
            beta,
        )

        return beta


    def _alpha(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate annualized CAPM alpha.

        Parameters
        ----------
        portfolio_returns
            Portfolio daily returns.
        benchmark_returns
            Benchmark daily returns.

        Returns
        -------
        float
            Annualized alpha.
        """

        if (
            portfolio_returns.empty
            or benchmark_returns.empty
        ):

            return 0.0

        data = pd.concat(
            [
                portfolio_returns.rename(
                    "portfolio",
                ),
                benchmark_returns.rename(
                    "benchmark",
                ),
            ],
            axis=1,
        ).dropna()

        if len(data) < 2:

            return 0.0

        beta = self._beta(
            data["portfolio"],
            data["benchmark"],
        )

        portfolio_return = (
            self._annualized_return(
                data["portfolio"],
            )
        )

        benchmark_return = (
            self._annualized_return(
                data["benchmark"],
            )
        )

        expected_return = (

            self.config.risk_free_rate

            + beta
            * (
                benchmark_return
                - self.config.risk_free_rate
            )

        )

        alpha = (

            portfolio_return

            - expected_return

        )

        logger.debug(
            "Alpha: %.6f",
            alpha,
        )

        return alpha


    def _information_ratio(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate the annualized Information Ratio.

        Parameters
        ----------
        portfolio_returns
            Portfolio daily returns.
        benchmark_returns
            Benchmark daily returns.

        Returns
        -------
        float
            Annualized Information Ratio.
        """

        if (
            portfolio_returns.empty
            or benchmark_returns.empty
        ):

            return 0.0

        data = pd.concat(
            [
                portfolio_returns.rename(
                    "portfolio",
                ),
                benchmark_returns.rename(
                    "benchmark",
                ),
            ],
            axis=1,
        ).dropna()

        if len(data) < 2:

            return 0.0

        active_returns = (

            data["portfolio"]

            - data["benchmark"]

        )

        annualized_active_return = (

            active_returns.mean()

            * self.config.trading_days

        )

        tracking_error = (

            active_returns.std(
                ddof=1,
            )

            * np.sqrt(
                self.config.trading_days
            )

        )

        if (
            np.isnan(
                tracking_error
            )
            or tracking_error <= 0.0
        ):

            return 0.0

        information_ratio = (

            annualized_active_return

            / tracking_error

        )

        logger.debug(
            "Information Ratio: %.6f",
            information_ratio,
        )

        return information_ratio


    def _treynor_ratio(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """
        Calculate the annualized Treynor Ratio.

        Parameters
        ----------
        portfolio_returns
            Portfolio daily returns.
        benchmark_returns
            Benchmark daily returns.

        Returns
        -------
        float
            Annualized Treynor Ratio.
        """

        if (
            portfolio_returns.empty
            or benchmark_returns.empty
        ):

            return 0.0

        data = pd.concat(
            [
                portfolio_returns.rename(
                    "portfolio",
                ),
                benchmark_returns.rename(
                    "benchmark",
                ),
            ],
            axis=1,
        ).dropna()

        if len(data) < 2:

            return 0.0

        beta = self._beta(
            data["portfolio"],
            data["benchmark"],
        )

        if (
            np.isnan(beta)
            or abs(beta) < 1e-12
        ):

            return 0.0

        annualized_return = (
            self._annualized_return(
                data["portfolio"],
            )
        )

        excess_return = (

            annualized_return

            - self.config.risk_free_rate

        )

        treynor_ratio = (

            excess_return

            / beta

        )

        logger.debug(
            "Treynor Ratio: %.6f",
            treynor_ratio,
        )

        return treynor_ratio


    def _summary(
        self,
        metrics: dict[str, float],
    ) -> dict[str, float]:
        """
        Build the standardized performance summary.

        Parameters
        ----------
        metrics
            Raw performance metrics.

        Returns
        -------
        dict[str, float]
            Standardized performance summary.
        """

        summary = {

            "Total Return":
                metrics.get(
                    "Total Return",
                    0.0,
                ),

            "Annualized Return":
                metrics.get(
                    "Annualized Return",
                    0.0,
                ),

            "Annualized Volatility":
                metrics.get(
                    "Annualized Volatility",
                    0.0,
                ),

            "Sharpe Ratio":
                metrics.get(
                    "Sharpe Ratio",
                    0.0,
                ),

            "Sortino Ratio":
                metrics.get(
                    "Sortino Ratio",
                    0.0,
                ),

            "Calmar Ratio":
                metrics.get(
                    "Calmar Ratio",
                    0.0,
                ),

            "Maximum Drawdown":
                metrics.get(
                    "Maximum Drawdown",
                    0.0,
                ),

            "Recovery Factor":
                metrics.get(
                    "Recovery Factor",
                    0.0,
                ),

            "Gain-to-Pain Ratio":
                metrics.get(
                    "Gain-to-Pain Ratio",
                    0.0,
                ),

            "Omega Ratio":
                metrics.get(
                    "Omega Ratio",
                    0.0,
                ),

            "Value at Risk":
                metrics.get(
                    "Value at Risk",
                    0.0,
                ),

            "Conditional VaR":
                metrics.get(
                    "Conditional VaR",
                    0.0,
                ),

            "Beta":
                metrics.get(
                    "Beta",
                ),

            "Alpha":
                metrics.get(
                    "Alpha",
                ),

            "Information Ratio":
                metrics.get(
                    "Information Ratio",
                ),

            "Treynor Ratio":
                metrics.get(
                    "Treynor Ratio",
                ),

        }

        logger.info(
            "Performance summary generated with %d metrics.",
            len(summary),
        )

        return summary

    def reset(
        self,
    ) -> None:
        """
        Reset the performance engine.

        Currently the engine is stateless, but this method
        provides a consistent lifecycle interface and allows
        future stateful extensions.
        """

        logger.info(
            "Performance Engine reset."
        )