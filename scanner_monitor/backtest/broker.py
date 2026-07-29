"""
broker.py
=========

Institutional Backtesting Broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BrokerConfig:
    """
    Broker execution configuration.
    """

    initial_cash: float

    allow_short: bool = False

    allow_fractional_shares: bool = False

    max_position_size: float = 1.0

    max_order_value: float | None = None

    commission_model: str = "fixed"

    slippage_model: str = "fixed"

    margin_enabled: bool = False

    leverage: float = 1.0


@dataclass(slots=True)
class ExecutionReport:
    """
    Executed order information.
    """

    symbol: str

    side: str

    quantity: float

    requested_price: float

    executed_price: float

    gross_value: float

    commission: float

    slippage: float

    net_value: float

    timestamp: datetime = field(
        default_factory=datetime.now,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


class Broker:
    """
    Institutional Backtesting Broker.
    """

    def __init__(
        self,
        config: BrokerConfig,
    ) -> None:
        """
        Initialize the broker.
        """

        self.config = config

        self.cash = float(
            config.initial_cash
        )

        self.reserved_cash = 0.0

        self.buying_power = (
            self.cash
            * config.leverage
        )

        self.orders: list[
            dict[str, Any]
        ] = []

        self.executions: list[
            ExecutionReport
        ] = []

        logger.info(
            "Broker initialized | "
            "Cash: %.2f | "
            "Leverage: %.2fx",
            self.cash,
            config.leverage,
        )


    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ) -> ExecutionReport:
        """
        Submit an order for execution.
        """

        self._validate_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
        )

        self._check_position_limits(
            quantity=quantity,
            price=price,
        )

        self._check_cash(
            side=side,
            quantity=quantity,
            price=price,
        )

        execution = self._execute_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
        )

        self.executions.append(execution)

        logger.info(
            "%s %s %.2f @ %.2f",
            side,
            symbol,
            quantity,
            execution.executed_price,
        )

        return execution

    def _validate_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ) -> None:
        """
        Validate an incoming order.
        """

        if not symbol.strip():
            raise ValueError(
                "Symbol cannot be empty."
            )

        if side not in {"BUY", "SELL"}:
            raise ValueError(
                "Invalid order side."
            )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be positive."
            )

        if price <= 0:
            raise ValueError(
                "Price must be positive."
            )

    def _check_cash(
        self,
        side: str,
        quantity: float,
        price: float,
    ) -> None:
        """
        Verify sufficient buying power.
        """

        if side != "BUY":
            return

        order_value = quantity * price

        if order_value > self.buying_power:
            raise ValueError(
                "Insufficient buying power."
            )

    def _check_position_limits(
        self,
        quantity: float,
        price: float,
    ) -> None:
        """
        Check broker position limits.
        """

        order_value = quantity * price

        if (
            self.config.max_order_value is not None
            and order_value > self.config.max_order_value
        ):
            raise ValueError(
                "Order exceeds maximum allowed value."
            )

    def _execute_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ) -> ExecutionReport:
        """
        Execute an order.
        """

        executed_price = self._apply_slippage(
            side=side,
            price=price,
        )

        commission = (
            self._apply_transaction_costs(
                quantity=quantity,
                price=executed_price,
            )
        )

        gross_value = (
            quantity
            * executed_price
        )

        slippage = abs(
            executed_price
            - price
        ) * quantity

        net_value = (
            gross_value
            + commission
            if side == "BUY"
            else gross_value
            - commission
        )

        self._update_cash(
            side=side,
            amount=net_value,
        )

        return ExecutionReport(
            symbol=symbol,
            side=side,
            quantity=quantity,
            requested_price=price,
            executed_price=executed_price,
            gross_value=gross_value,
            commission=commission,
            slippage=slippage,
            net_value=net_value,
        )

    def _apply_slippage(
        self,
        side: str,
        price: float,
    ) -> float:
        """
        Apply execution slippage.
        """

        if (
            self.config.slippage_model
            == "fixed"
        ):
            slippage_rate = 0.0005
        else:
            slippage_rate = 0.0

        if side == "BUY":
            return price * (
                1.0 + slippage_rate
            )

        return price * (
            1.0 - slippage_rate
        )

    def _apply_transaction_costs(
        self,
        quantity: float,
        price: float,
    ) -> float:
        """
        Calculate transaction costs.
        """

        trade_value = (
            quantity
            * price
        )

        if (
            self.config.commission_model
            == "fixed"
        ):
            return max(
                1.0,
                trade_value
                * 0.001,
            )

        return 0.0


    def _update_cash(
        self,
        side: str,
        amount: float,
    ) -> None:
        """
        Update broker cash balance after execution.
        """

        if side == "BUY":
            self.cash -= amount
        else:
            self.cash += amount

        self.buying_power = (
            self.cash
            * self.config.leverage
        )

    def cancel_order(
        self,
        order_id: int,
    ) -> bool:
        """
        Cancel a pending order.

        Returns
        -------
        bool
            True if cancelled successfully.
        """

        if (
            order_id < 0
            or order_id >= len(self.orders)
        ):
            return False

        order = self.orders[order_id]

        if order.get(
            "status",
        ) == "EXECUTED":
            return False

        order["status"] = "CANCELLED"

        logger.info(
            "Cancelled order %d",
            order_id,
        )

        return True

    def order_history(
        self,
    ) -> list[ExecutionReport]:
        """
        Return execution history.
        """

        return list(
            self.executions
        )

    def reset(
        self,
    ) -> None:
        """
        Reset broker state.
        """

        self.cash = float(
            self.config.initial_cash
        )

        self.reserved_cash = 0.0

        self.buying_power = (
            self.cash
            * self.config.leverage
        )

        self.orders.clear()

        self.executions.clear()

        logger.info(
            "Broker reset."
        )