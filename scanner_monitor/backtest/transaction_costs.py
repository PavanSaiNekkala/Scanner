"""
transaction_costs.py
====================

Institutional Transaction Cost Models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TransactionCostConfig:
    """
    Transaction cost configuration.
    """

    brokerage_rate: float = 0.001

    minimum_brokerage: float = 1.0

    maximum_brokerage: float | None = None

    exchange_fee_rate: float = 0.0

    regulatory_fee_rate: float = 0.0

    stamp_duty_rate: float = 0.0

    tax_rate: float = 0.0

    currency: str = "USD"


class TransactionCostEngine:
    """
    Institutional transaction cost engine.
    """

    def __init__(
        self,
        config: TransactionCostConfig,
    ) -> None:
        """
        Initialize the transaction cost engine.
        """

        self.config = config

        logger.info(
            "TransactionCostEngine initialized."
        )


    def calculate(
        self,
        quantity: float,
        price: float,
    ) -> dict[str, float]:
        """
        Calculate the complete transaction cost breakdown.
        """

        trade_value = (
            quantity
            * price
        )

        brokerage = self.brokerage(
            trade_value
        )

        exchange_fee = self.exchange_fee(
            trade_value
        )

        regulatory_fee = self.regulatory_fee(
            trade_value
        )

        stamp_duty = self.stamp_duty(
            trade_value
        )

        tax = self.tax(
            brokerage
            + exchange_fee
            + regulatory_fee
        )

        total = (
            brokerage
            + exchange_fee
            + regulatory_fee
            + stamp_duty
            + tax
        )

        return {
            "trade_value": trade_value,
            "brokerage": brokerage,
            "exchange_fee": exchange_fee,
            "regulatory_fee": regulatory_fee,
            "stamp_duty": stamp_duty,
            "tax": tax,
            "total_cost": total,
        }

    def brokerage(
        self,
        trade_value: float,
    ) -> float:
        """
        Calculate brokerage.
        """

        brokerage = (
            trade_value
            * self.config.brokerage_rate
        )

        brokerage = max(
            brokerage,
            self.config.minimum_brokerage,
        )

        if (
            self.config.maximum_brokerage
            is not None
        ):
            brokerage = min(
                brokerage,
                self.config.maximum_brokerage,
            )

        return brokerage

    def exchange_fee(
        self,
        trade_value: float,
    ) -> float:
        """
        Calculate exchange fee.
        """

        return (
            trade_value
            * self.config.exchange_fee_rate
        )

    def regulatory_fee(
        self,
        trade_value: float,
    ) -> float:
        """
        Calculate regulatory fee.
        """

        return (
            trade_value
            * self.config.regulatory_fee_rate
        )

    def stamp_duty(
        self,
        trade_value: float,
    ) -> float:
        """
        Calculate stamp duty.
        """

        return (
            trade_value
            * self.config.stamp_duty_rate
        )

    def tax(
        self,
        taxable_amount: float,
    ) -> float:
        """
        Calculate applicable taxes.
        """

        return (
            taxable_amount
            * self.config.tax_rate
        )

    def total_cost(
        self,
        quantity: float,
        price: float,
    ) -> float:
        """
        Return the total transaction cost.
        """

        return self.calculate(
            quantity=quantity,
            price=price,
        )["total_cost"]

    def breakdown(
        self,
        quantity: float,
        price: float,
    ) -> dict[str, Any]:
        """
        Return a detailed transaction cost breakdown.
        """

        breakdown = self.calculate(
            quantity=quantity,
            price=price,
        )

        logger.debug(
            "Transaction Cost Breakdown: %s",
            breakdown,
        )

        return breakdown

    def reset(
        self,
    ) -> None:
        """
        Reset the transaction cost engine.
        """

        logger.info(
            "TransactionCostEngine reset."
        )