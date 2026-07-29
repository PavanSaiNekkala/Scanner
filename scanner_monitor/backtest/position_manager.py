"""
position_manager.py
===================

Institutional Position Management Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import logging

import pandas as pd

logger = logging.getLogger(__name__)


# ==========================================================
# Position
# ==========================================================


@dataclass(slots=True)
class Position:
    """
    Portfolio position.
    """

    symbol: str

    quantity: float

    average_price: float

    last_price: float

    market_value: float = 0.0

    cost_basis: float = 0.0

    unrealized_pnl: float = 0.0

    realized_pnl: float = 0.0

    weight: float = 0.0

    entry_date: pd.Timestamp | None = None

    last_update: datetime = field(
        default_factory=datetime.now,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# ==========================================================
# Position Manager
# ==========================================================


class PositionManager:
    """
    Institutional Position Management Engine.

    Responsibilities
    ----------------
    • Open positions
    • Close positions
    • Increase positions
    • Reduce positions
    • Average cost calculation
    • Cost basis tracking
    • Realized P&L
    • Unrealized P&L
    • Market valuation
    """

    def __init__(self) -> None:

        logger.info(
            "Position Manager initialized."
        )



    def update(
        self,
        positions: dict[str, Position],
        cash: float,
        executions: list[dict[str, Any]],
    ) -> tuple[
        dict[str, Position],
        float,
        list[dict[str, Any]],
    ]:
        """
        Update portfolio positions after trade execution.

        Parameters
        ----------
        positions
            Current portfolio positions.
        cash
            Available cash.
        executions
            Executed trades.

        Returns
        -------
        tuple
            Updated positions, cash and trade ledger.
        """

        logger.info(
            "Updating %d executions.",
            len(executions),
        )

        updated = positions.copy()

        trade_log: list[dict[str, Any]] = []

        for execution in executions:

            side = execution["side"].upper()

            if side == "BUY":

                updated, cash, trade = (
                    self._buy_position(
                        updated,
                        cash,
                        execution,
                    )
                )

            elif side == "SELL":

                updated, cash, trade = (
                    self._sell_position(
                        updated,
                        cash,
                        execution,
                    )
                )

            else:

                logger.warning(
                    "Unknown order side: %s",
                    side,
                )

                continue

            trade_log.append(trade)

        logger.info(
            "Portfolio contains %d open positions.",
            len(updated),
        )

        return (
            updated,
            cash,
            trade_log,
        )

    

    def _buy_position(
        self,
        positions: dict[str, Position],
        cash: float,
        execution: dict[str, Any],
    ) -> tuple[
        dict[str, Position],
        float,
        dict[str, Any],
    ]:
        """
        Process a BUY execution.
        """

        symbol = execution["symbol"]

        quantity = float(
            execution["executed_quantity"]
        )

        price = float(
            execution["execution_price"]
        )

        transaction_cost = float(
            execution["transaction_cost"]
        )

        total_cost = (
            quantity * price
            + transaction_cost
        )

        if total_cost > cash:

            raise ValueError(
                f"Insufficient cash to buy "
                f"{quantity} shares of {symbol}."
            )

        cash -= total_cost

        # -------------------------------------------------
        # Existing Position
        # -------------------------------------------------

        if symbol in positions:

            position = positions[symbol]

            old_quantity = position.quantity

            new_quantity = (
                old_quantity + quantity
            )

            new_average = self._average_cost(
                old_quantity,
                position.average_price,
                quantity,
                price,
            )

            position.quantity = (
                new_quantity
            )

            position.average_price = (
                new_average
            )

            position.cost_basis = (
                new_quantity
                * new_average
            )

            position.last_price = (
                price
            )

            position.market_value = (
                new_quantity
                * price
            )

            position.last_update = (
                datetime.now()
            )

        # -------------------------------------------------
        # New Position
        # -------------------------------------------------

        else:

            positions[symbol] = Position(

                symbol=symbol,

                quantity=quantity,

                average_price=price,

                last_price=price,

                market_value=(
                    quantity
                    * price
                ),

                cost_basis=(
                    quantity
                    * price
                ),

                entry_date=execution[
                    "date"
                ],

            )

        trade = self._trade_record(
            execution=execution,
            side="BUY",
            cash_after_trade=cash,
        )

        return (
            positions,
            cash,
            trade,
        )


    def _average_cost(
        self,
        old_quantity: float,
        old_price: float,
        new_quantity: float,
        new_price: float,
    ) -> float:
        """
        Calculate weighted average cost.
        """

        total_quantity = (
            old_quantity + new_quantity
        )
    
        if abs(total_quantity) < 1e-12:

            return 0.0

        return (

            old_quantity * old_price

            +

            new_quantity * new_price

        ) / total_quantity
    


    def _sell_position(
        self,
        positions: dict[str, Position],
        cash: float,
        execution: dict[str, Any],
    ) -> tuple[
        dict[str, Position],
        float,
        dict[str, Any],
    ]:
        """
        Process a SELL execution.
        """

        symbol = execution["symbol"]

        quantity = float(
            execution["executed_quantity"]
        )

        price = float(
            execution["execution_price"]
        )

        transaction_cost = float(
            execution["transaction_cost"]
        )

        if symbol not in positions:

            logger.warning(
                "Attempted to sell unknown position: %s",
                symbol,
            )

            rejected_execution = execution.copy()

            rejected_execution["status"] = "REJECTED"

            trade = self._trade_record(
                execution=rejected_execution,
                side="SELL",
                realized_pnl=0.0,            
                cash_after_trade=cash,
            )

            return (
                positions,
                cash,
                trade,
            )

        position = positions[symbol]

        if quantity > position.quantity:

            raise ValueError(
                f"Cannot sell "
                f"{quantity} shares of {symbol}; "
                f"only {position.quantity} available."
            )

        sell_quantity = quantity

        proceeds = (
            sell_quantity * price
        )

        realized_pnl = (

            price
            - position.average_price

        ) * sell_quantity

        cash += (
            proceeds
            - transaction_cost
        )

        position.quantity -= sell_quantity

        position.realized_pnl += (
            realized_pnl
        )

        position.market_value = (
            position.quantity
            * price
        )

        position.cost_basis = (
            position.quantity
            * position.average_price
        )

        position.last_price = price

        position.last_update = (
            datetime.now()
        )

        # ---------------------------------------------
        # Close Position
        # ---------------------------------------------

        if abs(position.quantity) < 1e-12:

            positions = self._close_position(
                positions,
                symbol,
            )

        trade = self._trade_record(
            execution=execution,
            side="SELL",
            realized_pnl=realized_pnl,
            cash_after_trade=cash,
        )

        return (
            positions,
            cash,
            trade,
        )



    def _mark_to_market(
        self,
        positions: dict[str, Position],
        market_data: pd.DataFrame,
    ) -> tuple[
        dict[str, Position],
        float,
    ]:
        """
        Mark all positions to current market prices.

        Parameters
        ----------
        positions
            Current portfolio positions.
        market_data
            Current market data.

        Returns
        -------
        tuple
            Updated positions and total invested value.
        """

        logger.info(
            "Marking positions to market."
        )

        if not positions:

            return positions, 0.0

        # -----------------------------------------------------
        # Current Prices
        # -----------------------------------------------------

        required = {"symbol", "close"}

        missing = required.difference(
            market_data.columns
        )

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        prices = (
            market_data
            .set_index("symbol")["close"]
            .to_dict()
        )

        total_market_value = 0.0

        # -----------------------------------------------------
        # Revalue Positions
        # -----------------------------------------------------

        for symbol, position in positions.items():

            if symbol not in prices:

                logger.warning(
                    "Missing market price for %s.",
                    symbol,
                )

                continue

            current_price = float(
                prices[symbol]
            )

            position.last_price = current_price

            position.market_value = (
                position.quantity
                * current_price
            )

            position.cost_basis = (
                position.quantity
                * position.average_price
            )

            position.unrealized_pnl = (

                position.market_value

                - position.cost_basis

            )

            position.last_update = (
                datetime.now()
            )

            total_market_value += (
                position.market_value
            )

        # -----------------------------------------------------
        # Portfolio Weights
        # -----------------------------------------------------

        if total_market_value > 0:

            for position in positions.values():

                position.weight = (

                    position.market_value

                    / total_market_value

                )

        else:

            for position in positions.values():

                position.weight = 0.0

        logger.info(
            "Marked %d positions to market.",
            len(positions),
        )

        return (
            positions,
            total_market_value,
        )

    def _close_position(
        self,
        positions: dict[str, Position],
        symbol: str,
    ) -> dict[str, Position]:
        """
        Close a portfolio position.

        Parameters
        ----------
        positions
            Current portfolio positions.
        symbol
            Position symbol.

        Returns
        -------
        dict
            Updated positions.
        """

        if symbol not in positions:

            logger.warning(
                "Position %s not found.",
                symbol,
            )

            return positions

        position = positions[symbol]

        logger.info(
            "Closing position: %s "
            "(Quantity: %.2f, "
            "Realized P&L: %.2f)",
            symbol,
            position.quantity,
            position.realized_pnl,
        )

        # ---------------------------------------------
        # Final Position State
        # ---------------------------------------------

        position.quantity = 0.0

        position.market_value = 0.0

        position.cost_basis = 0.0

        position.unrealized_pnl = 0.0

        position.weight = 0.0

        position.last_update = (
            datetime.now()
        )

        # ---------------------------------------------
        # Remove Position
        # ---------------------------------------------

        del positions[symbol]

        logger.info(
            "Position %s closed.",
            symbol,
        )

        return positions

    def _trade_record(
        self,
        execution: dict[str, Any],
        side: str,
        cash_after_trade: float,
        realized_pnl: float = 0.0,
    ) -> dict[str, Any]:
        """
        Create a standardized trade record.

        Parameters
        ----------
        execution
            Executed order.
        side
            BUY or SELL.
        cash_after_trade
            Cash balance after execution.
        realized_pnl
            Realized profit/loss.

        Returns
        -------
        dict
            Trade record.
        """

        quantity = float(
            execution["executed_quantity"]
        )

        price = float(
            execution["execution_price"]
        )

        transaction_cost = float(
            execution.get(
                "transaction_cost",
                0.0,
            )
        )

        trade_value = (
            quantity * price
        )

        return {

            "date": execution["date"],

            "symbol": execution["symbol"],

            "side": side,

            "quantity": quantity,

            "price": price,

            "trade_value": trade_value,

            "transaction_cost":
                transaction_cost,

            "realized_pnl":
                realized_pnl,

            "cash_after_trade":
                cash_after_trade,

            "status":
                execution.get(
                    "status",
                    "FILLED",
                ),

            "order_id":
                execution.get(
                    "order_id",
                ),

            "execution_id":
                execution.get(
                    "execution_id",
                ),

        }

    def positions_dataframe(
        self,
        positions: dict[str, Position],
    ) -> pd.DataFrame:
        """
        Convert portfolio positions to a DataFrame.

        Parameters
        ----------
        positions
            Current portfolio positions.

        Returns
        -------
        pd.DataFrame
            Position report.
        """

        if not positions:

            return pd.DataFrame(
                columns=[
                    "symbol",
                    "quantity",
                    "average_price",
                    "last_price",
                    "cost_basis",
                    "market_value",
                    "weight",
                    "unrealized_pnl",
                    "realized_pnl",
                    "entry_date",
                    "last_update",
                ]
            )

        records = []


        for position in positions.values():

            records.append(
                {
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "average_price": position.average_price,
                    "last_price": position.last_price,
                    "cost_basis": position.cost_basis,
                    "market_value": position.market_value,
                    "weight": position.weight,
                    "unrealized_pnl": position.unrealized_pnl,
                    "realized_pnl": position.realized_pnl,
                    "entry_date": position.entry_date,
                    "last_update": position.last_update,
                }
            )

        df = pd.DataFrame(records)

        df.sort_values(
            by="market_value",
            ascending=False,
            inplace=True,
        )

        df.reset_index(
            drop=True,
            inplace=True,
        )

        logger.info(
            "Exported %d portfolio positions.",
            len(df),
        )

        return df.copy()            


__all__ = [
    "Position",
    "PositionManager",
]