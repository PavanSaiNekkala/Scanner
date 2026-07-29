"""
turnover.py
===========

Institutional Portfolio Turnover Analytics Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TurnoverConfig:
    """
    Portfolio turnover configuration.
    """

    annualization_factor: int = 252


class TurnoverEngine:
    """
    Institutional portfolio turnover engine.
    """

    def __init__(
        self,
        config: TurnoverConfig,
    ) -> None:
        """
        Initialize turnover engine.
        """

        self.config = config

        logger.info(
            "TurnoverEngine initialized."
        )


    def turnover(
        self,
        trades: pd.DataFrame,
        portfolio_value: float,
    ) -> float:
        """
        Calculate portfolio turnover ratio.
        """

        if trades.empty:
            return 0.0

        if portfolio_value <= 0:
            raise ValueError(
                "portfolio_value must be positive."
            )

        traded_value = (
            trades["quantity"]
            * trades["price"]
        ).abs().sum()

        return float(
            traded_value
            / portfolio_value
        )

    def annualized_turnover(
        self,
        trades: pd.DataFrame,
        portfolio_value: float,
        periods: int,
    ) -> float:
        """
        Calculate annualized turnover.
        """

        if periods <= 0:
            raise ValueError(
                "periods must be positive."
            )

        turnover = self.turnover(
            trades,
            portfolio_value,
        )

        return (
            turnover
            * (
                self.config.annualization_factor
                / periods
            )
        )

    def average_trade_size(
        self,
        trades: pd.DataFrame,
    ) -> float:
        """
        Calculate average trade value.
        """

        if trades.empty:
            return 0.0

        trade_values = (
            trades["quantity"]
            * trades["price"]
        ).abs()

        return float(
            trade_values.mean()
        )

    def total_traded_value(
        self,
        trades: pd.DataFrame,
    ) -> float:
        """
        Return total traded value.
        """

        if trades.empty:
            return 0.0

        return float(
            (
                trades["quantity"]
                * trades["price"]
            ).abs().sum()
        )

    def trade_count(
        self,
        trades: pd.DataFrame,
    ) -> int:
        """
        Return number of executed trades.
        """

        return int(
            len(trades)
        )


    def buy_turnover(
        self,
        trades: pd.DataFrame,
        portfolio_value: float,
    ) -> float:
        """
        Calculate buy-side turnover.
        """

        if trades.empty:
            return 0.0

        buys = trades[
            trades["side"] == "BUY"
        ]

        traded_value = (
            buys["quantity"]
            * buys["price"]
        ).abs().sum()

        return float(
            traded_value
            / portfolio_value
        )

    def sell_turnover(
        self,
        trades: pd.DataFrame,
        portfolio_value: float,
    ) -> float:
        """
        Calculate sell-side turnover.
        """

        if trades.empty:
            return 0.0

        sells = trades[
            trades["side"] == "SELL"
        ]

        traded_value = (
            sells["quantity"]
            * sells["price"]
        ).abs().sum()

        return float(
            traded_value
            / portfolio_value
        )

    def average_holding_period(
        self,
        trades: pd.DataFrame,
    ) -> float:
        """
        Calculate average holding period.
        """

        if (
            trades.empty
            or "holding_days"
            not in trades.columns
        ):
            return 0.0

        return float(
            trades[
                "holding_days"
            ].mean()
        )

    def summary(
        self,
        trades: pd.DataFrame,
        portfolio_value: float,
        periods: int,
    ) -> pd.Series:
        """
        Return turnover summary statistics.
        """

        return pd.Series(
            {
                "Turnover":
                self.turnover(
                    trades,
                    portfolio_value,
                ),
                "Annualized Turnover":
                self.annualized_turnover(
                    trades,
                    portfolio_value,
                    periods,
                ),
                "Buy Turnover":
                self.buy_turnover(
                    trades,
                    portfolio_value,
                ),
                "Sell Turnover":
                self.sell_turnover(
                    trades,
                    portfolio_value,
                ),
                "Average Trade Size":
                self.average_trade_size(
                    trades,
                ),
                "Average Holding Period":
                self.average_holding_period(
                    trades,
                ),
                "Trade Count":
                self.trade_count(
                    trades,
                ),
                "Total Traded Value":
                self.total_traded_value(
                    trades,
                ),
            }
        )

    def reset(
        self,
    ) -> None:
        """
        Reset turnover engine.
        """

        logger.info(
            "TurnoverEngine reset."
        )