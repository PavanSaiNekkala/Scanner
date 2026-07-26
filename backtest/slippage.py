"""
slippage.py
===========

Institutional Slippage Models.
"""

from __future__ import annotations

from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SlippageConfig:
    """
    Slippage model configuration.
    """

    model: str = "fixed"

    fixed_bps: float = 5.0

    percentage: float = 0.0005

    volume_impact: float = 0.10

    tick_size: float = 0.01

    maximum_slippage: float | None = None


class SlippageEngine:
    """
    Institutional slippage engine.
    """

    def __init__(
        self,
        config: SlippageConfig,
    ) -> None:
        """
        Initialize the slippage engine.
        """

        self.config = config

        logger.info(
            "SlippageEngine initialized."
        )

    def apply(
        self,
        side: str,
        price: float,
        quantity: float = 0.0,
        volume: float | None = None,
    ) -> float:
        """
        Apply the configured slippage model.
        """

        model = (
            self.config.model.lower()
        )

        if model == "fixed":
            return self.fixed(
                side=side,
                price=price,
            )

        if model == "percentage":
            return self.percentage(
                side=side,
                price=price,
            )

        if model == "volume":
            return self.volume_based(
                side=side,
                price=price,
                quantity=quantity,
                volume=volume,
            )

        return price

    def fixed(
        self,
        side: str,
        price: float,
    ) -> float:
        """
        Apply fixed basis-point slippage.
        """

        rate = (
            self.config.fixed_bps
            / 10000.0
        )

        if side == "BUY":
            return price * (
                1.0 + rate
            )

        return price * (
            1.0 - rate
        )

    def percentage(
        self,
        side: str,
        price: float,
    ) -> float:
        """
        Apply percentage slippage.
        """

        rate = (
            self.config.percentage
        )

        if side == "BUY":
            return price * (
                1.0 + rate
            )

        return price * (
            1.0 - rate
        )

    def volume_based(
        self,
        side: str,
        price: float,
        quantity: float,
        volume: float | None,
    ) -> float:
        """
        Apply volume-based slippage.
        """

        if (
            volume is None
            or volume <= 0
        ):
            return price

        participation = min(
            quantity / volume,
            1.0,
        )

        impact = (
            participation
            * self.config.volume_impact
        )

        if side == "BUY":
            return price * (
                1.0 + impact
            )

        return price * (
            1.0 - impact
        )

    def slippage_amount(
        self,
        requested_price: float,
        executed_price: float,
        quantity: float,
    ) -> float:
        """
        Return absolute slippage cost.
        """

        return (
            abs(
                executed_price
                - requested_price
            )
            * quantity
        )


    def slippage_rate(
        self,
        requested_price: float,
        executed_price: float,
    ) -> float:
        """
        Return slippage as a percentage.
        """

        if requested_price <= 0:
            return 0.0

        return (
            abs(
                executed_price
                - requested_price
            )
            / requested_price
        )

    def summary(
        self,
        requested_price: float,
        executed_price: float,
        quantity: float,
    ) -> dict[str, float]:
        """
        Return a summary of slippage statistics.
        """

        amount = self.slippage_amount(
            requested_price=requested_price,
            executed_price=executed_price,
            quantity=quantity,
        )

        rate = self.slippage_rate(
            requested_price=requested_price,
            executed_price=executed_price,
        )

        return {
            "requested_price": requested_price,
            "executed_price": executed_price,
            "quantity": quantity,
            "slippage_amount": amount,
            "slippage_rate": rate,
        }

    def reset(
        self,
    ) -> None:
        """
        Reset the slippage engine.
        """

        logger.info(
            "SlippageEngine reset."
        )