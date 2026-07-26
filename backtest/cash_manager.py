"""
cash_manager.py
===============

Institutional Cash Management Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CashManagerConfig:
    """
    Cash management configuration.
    """

    initial_cash: float

    leverage: float = 1.0

    margin_enabled: bool = False

    margin_requirement: float = 1.0

    allow_negative_cash: bool = False

    currency: str = "USD"


@dataclass(slots=True)
class CashSnapshot:
    """
    Cash account snapshot.
    """

    timestamp: datetime = field(
        default_factory=datetime.now,
    )

    cash: float = 0.0

    reserved_cash: float = 0.0

    available_cash: float = 0.0

    buying_power: float = 0.0

    leverage: float = 1.0

    margin_used: float = 0.0

    equity: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


class CashManager:
    """
    Institutional cash management engine.
    """

    def __init__(
        self,
        config: CashManagerConfig,
    ) -> None:
        """
        Initialize the cash manager.
        """

        if config.initial_cash <= 0:
            raise ValueError(
                "initial_cash must be greater than zero."
            )

        if config.leverage <= 0:
            raise ValueError(
                "leverage must be greater than zero."
            )

        self.config = config

        self.cash = float(
            config.initial_cash
        )

        self.reserved_cash = 0.0

        self.margin_used = 0.0

        self.snapshots: list[
            CashSnapshot
        ] = []

        logger.info(
            "CashManager initialized | "
            "Cash: %.2f | "
            "Leverage: %.2fx",
            self.cash,
            config.leverage,
        )

    def available_cash(
        self,
    ) -> float:
        """
        Return available cash.
        """

        return max(
            0.0,
            self.cash
            - self.reserved_cash,
        )

    def buying_power(
        self,
    ) -> float:
        """
        Return available buying power.
        """

        return (
            self.available_cash()
            * self.config.leverage
        )

    def reserve_cash(
        self,
        amount: float,
    ) -> None:
        """
        Reserve cash for pending orders.
        """

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        if (
            amount
            > self.available_cash()
        ):
            raise ValueError(
                "Insufficient available cash."
            )

        self.reserved_cash += amount

        logger.debug(
            "Reserved cash: %.2f",
            amount,
        )

    def release_cash(
        self,
        amount: float,
    ) -> None:
        """
        Release previously reserved cash.
        """

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        if amount > self.reserved_cash:
            raise ValueError(
                "Cannot release more than reserved cash."
            )

        self.reserved_cash -= amount

        logger.debug(
            "Released cash: %.2f",
            amount,
        )

    def debit(
        self,
        amount: float,
    ) -> None:
        """
        Debit cash from the account.
        """

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        if (
            not self.config.allow_negative_cash
            and amount > self.cash
        ):
            raise ValueError(
                "Insufficient cash balance."
            )

        self.cash -= amount

        logger.debug(
            "Debited %.2f | Balance: %.2f",
            amount,
            self.cash,
        )


    def credit(
        self,
        amount: float,
    ) -> None:
        """
        Credit cash to the account.
        """

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        self.cash += amount

        logger.debug(
            "Credited %.2f | Balance: %.2f",
            amount,
            self.cash,
        )

    def equity(
        self,
    ) -> float:
        """
        Return current account equity.
        """

        return (
            self.cash
            + self.margin_used
        )

    def utilization(
        self,
    ) -> float:
        """
        Return cash utilization ratio.
        """

        if self.cash <= 0:
            return 0.0

        return (
            self.reserved_cash
            / self.cash
        )

    def margin_available(
        self,
    ) -> float:
        """
        Return available margin.
        """

        if (
            not self.config.margin_enabled
        ):
            return 0.0

        maximum_margin = (
            self.cash
            * (
                self.config.leverage
                - 1.0
            )
        )

        return max(
            0.0,
            maximum_margin
            - self.margin_used,
        )

    def snapshot(
        self,
        **metadata: Any,
    ) -> CashSnapshot:
        """
        Create and store a cash snapshot.
        """

        snapshot = CashSnapshot(
            cash=self.cash,
            reserved_cash=self.reserved_cash,
            available_cash=self.available_cash(),
            buying_power=self.buying_power(),
            leverage=self.config.leverage,
            margin_used=self.margin_used,
            equity=self.equity(),
            metadata=metadata,
        )

        self.snapshots.append(
            snapshot
        )

        return snapshot

    def history(
        self,
    ) -> list[CashSnapshot]:
        """
        Return the cash snapshot history.
        """

        return list(
            self.snapshots
        )

    def history_dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Return cash history as a DataFrame.
        """

        if not self.snapshots:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "cash",
                    "reserved_cash",
                    "available_cash",
                    "buying_power",
                    "leverage",
                    "margin_used",
                    "equity",
                    "metadata",
                ]
            )

        return pd.DataFrame(
            [
                {
                    "timestamp": s.timestamp,
                    "cash": s.cash,
                    "reserved_cash": s.reserved_cash,
                    "available_cash": s.available_cash,
                    "buying_power": s.buying_power,
                    "leverage": s.leverage,
                    "margin_used": s.margin_used,
                    "equity": s.equity,
                    "metadata": s.metadata,
                }
                for s in self.snapshots
            ]
        )

    def reset(
        self,
    ) -> None:
        """
        Reset the cash manager to its initial state.
        """

        self.cash = float(
            self.config.initial_cash
        )

        self.reserved_cash = 0.0

        self.margin_used = 0.0

        self.snapshots.clear()

        logger.info(
            "CashManager reset."
        )