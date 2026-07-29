"""
portfolio_tracker.py
====================

Institutional Portfolio Tracking Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from scanner_monitor.backtest.position_manager import Position

import logging
import pandas as pd


logger = logging.getLogger(__name__)


# ==========================================================
# Portfolio Snapshot
# ==========================================================


@dataclass(slots=True)
class PortfolioSnapshot:
    """
    Portfolio state at a point in time.
    """

    date: pd.Timestamp

    cash: float

    invested_value: float

    portfolio_value: float

    daily_return: float = 0.0

    cumulative_return: float = 0.0

    gross_exposure: float = 0.0

    net_exposure: float = 0.0

    leverage: float = 1.0

    number_of_positions: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=datetime.now,
    )

# ==========================================================
# Portfolio Tracker
# ==========================================================


class PortfolioTracker:
    """
    Institutional Portfolio Tracking Engine.

    Responsibilities
    ----------------
    • Portfolio valuation
    • NAV calculation
    • Daily snapshots
    • Equity curve
    • Cash tracking
    • Exposure tracking
    • Performance history
    """

    def __init__(
        self,
        initial_capital: float,
    ) -> None:
        """
        Initialize portfolio tracker.

        Parameters
        ----------
        initial_capital
            Starting portfolio capital.
        """

        if initial_capital <= 0:
            raise ValueError(
                "initial_capital must be greater than zero."
            )

        self.initial_capital = float(
            initial_capital
        )

        self.current_cash = float(
            initial_capital
        )

        self.current_value = float(
            initial_capital
        )

        self.previous_value = float(
            initial_capital
        )

        self.cumulative_return = 0.0

        self.history: list[
            PortfolioSnapshot
        ] = []

        self.latest_snapshot: (
            PortfolioSnapshot | None
        ) = None

        logger.info(
            "Portfolio Tracker initialized "
            "with capital %.2f",
            self.initial_capital,
        )

    def update(
        self,
        date: pd.Timestamp,
        positions: dict[str, Position],
        cash: float,
    ) -> PortfolioSnapshot:
        """
        Update portfolio state.

        Parameters
        ----------
        date
            Current portfolio date.
        positions
            Current portfolio positions.
        cash
            Current cash balance.

        Returns
        -------
        PortfolioSnapshot
            Portfolio snapshot.
        """

        date = pd.Timestamp(date)

        invested_value = self._portfolio_value(
            positions,
        )

        portfolio_value = (
            invested_value + cash
        )

        daily_return = self._daily_return(
            portfolio_value,
        )

        self.cumulative_return = (
            self._cumulative_return(
                portfolio_value,
            )
        )

        gross_exposure = (
            self._gross_exposure(
                positions,
            )
        )

        net_exposure = (
            self._net_exposure(
                positions,
            )
        )

        leverage = (
            gross_exposure
            / portfolio_value
            if portfolio_value > 0
            else 0.0
        )

        snapshot = PortfolioSnapshot(

            date=date,

            cash=cash,

            invested_value=invested_value,

            portfolio_value=portfolio_value,

            daily_return=daily_return,

            cumulative_return=self.cumulative_return,

            gross_exposure=gross_exposure,

            net_exposure=net_exposure,

            leverage=leverage,

            number_of_positions=len(
                positions
            ),

        )

        self.history.append(
            snapshot
        )

        self.latest_snapshot = (
            snapshot
        )

        self.current_cash = cash

        self.previous_value = (
            portfolio_value
        )

        self.current_value = (
            portfolio_value
        )

        logger.info(
            "Portfolio updated | "
            "Value: %.2f | "
            "Cash: %.2f | "
            "Positions: %d",
            portfolio_value,
            cash,
            len(positions),
        )

        return snapshot

    def _portfolio_value(
        self,
        positions: dict[str, Position],
    ) -> float:
        """
        Calculate total invested portfolio value.

        Parameters
        ----------
        positions
            Current portfolio positions.

        Returns
        -------
        float
            Total market value of all open positions.
        """

        if not positions:

            return 0.0

        invested_value = sum(
            position.market_value
            for position in positions.values()
        )

        logger.debug(
            "Portfolio invested value: %.2f",
            invested_value,
        )

        return invested_value


    def _gross_exposure(
        self,
        positions: dict[str, Position],
    ) -> float:
        """
        Calculate gross portfolio exposure.

        Gross exposure is the sum of the absolute
        market values of all open positions.

        Parameters
        ----------
        positions
            Current portfolio positions.

        Returns
        -------
        float
            Gross portfolio exposure.
        """

        if not positions:

            return 0.0

        gross_exposure = sum(
            abs(position.market_value)
            for position in positions.values()
        )

        logger.debug(
            "Gross exposure: %.2f",
            gross_exposure,
        )

        return gross_exposure


    def _net_exposure(
        self,
        positions: dict[str, Position],
    ) -> float:
        """
        Calculate net portfolio exposure.

        Net exposure is the signed sum of the
        market values of all open positions.

        Parameters
        ----------
        positions
            Current portfolio positions.

        Returns
        -------
        float
            Net portfolio exposure.
        """

        if not positions:

            return 0.0

        net_exposure = sum(
            position.market_value
            for position in positions.values()
        )

        logger.debug(
            "Net exposure: %.2f",
            net_exposure,
        )

        return net_exposure


    def _daily_return(
        self,
        portfolio_value: float,
    ) -> float:
        """
        Calculate portfolio daily return.

        Parameters
        ----------
        portfolio_value
            Current portfolio value.

        Returns
        -------
        float
            Daily portfolio return.
        """

        if self.previous_value <= 0:

            return 0.0

        daily_return = (
            portfolio_value
            - self.previous_value
        ) / self.previous_value

        logger.debug(
            "Daily return: %.6f",
            daily_return,
        )

        return daily_return


    def _cumulative_return(
        self,
        portfolio_value: float,
    ) -> float:
        """
        Calculate cumulative portfolio return.

        Parameters
        ----------
        portfolio_value
            Current portfolio value.

        Returns
        -------
        float
            Cumulative portfolio return.
        """

        if self.initial_capital <= 0:

            return 0.0

        cumulative_return = (
            portfolio_value
            - self.initial_capital
        ) / self.initial_capital

        logger.debug(
            "Cumulative return: %.6f",
            cumulative_return,
        )

        return cumulative_return


    def history_dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Convert portfolio history to a DataFrame.

        Returns
        -------
        pd.DataFrame
            Portfolio history.
        """

        if not self.history:

            return pd.DataFrame(
                columns=[
                    "date",
                    "cash",
                    "invested_value",
                    "portfolio_value",
                    "daily_return",
                    "cumulative_return",
                    "gross_exposure",
                    "net_exposure",
                    "leverage",
                    "number_of_positions",
                ]
            )

        records = [

            {

                "date":
                    snapshot.date,

                "cash":
                    snapshot.cash,

                "invested_value":
                    snapshot.invested_value,

                "portfolio_value":
                    snapshot.portfolio_value,

                "daily_return":
                    snapshot.daily_return,

                "cumulative_return":
                    snapshot.cumulative_return,

                "gross_exposure":
                    snapshot.gross_exposure,

                "net_exposure":
                    snapshot.net_exposure,

                "leverage":
                    snapshot.leverage,

                "number_of_positions":
                    snapshot.number_of_positions,

                "metadata": snapshot.metadata,

            }

            for snapshot in self.history

        ]

        df = pd.DataFrame(records)

        df.sort_values(
            by="date",
            inplace=True,
        )

        df.reset_index(
            drop=True,
            inplace=True,
        )

        logger.info(
            "Exported %d portfolio snapshots.",
            len(df),
        )

        return df.copy()


    def reset(
        self,
    ) -> None:
        """
        Reset the portfolio tracker to its initial state.
        """

        self.current_cash = (
            self.initial_capital
        )

        self.current_value = (
            self.initial_capital
        )

        self.previous_value = (
            self.initial_capital
        )

        self.cumulative_return = 0.0

        self.latest_snapshot = None

        self.history.clear()

        logger.info(
            "Portfolio Tracker reset."
        )


